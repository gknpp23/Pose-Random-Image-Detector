import os
import cv2
import time
import json
import asyncio
import random
from typing import List, Optional

import mediapipe as mp
import websockets
from dotenv import load_dotenv


# ======================
load_dotenv()

SERVER_IP = os.getenv("SERVER_IP", "127.0.0.1")
SERVER_PORT = os.getenv("SERVER_PORT", "8000")
SERVER_URL = f"ws://{SERVER_IP}:{SERVER_PORT}/ws"

CAMERA_INDEX = int(os.getenv("CAMERA_INDEX", 0))
SIMULATION_MODE = os.getenv("SIMULATION_MODE", "false").lower() == "true"

DETECTION_COOLDOWN = float(os.getenv("DETECTION_COOLDOWN", 2.5))
DEBUG_DRAW = os.getenv("DEBUG_DRAW", "false").lower() == "true"

IMAGE_DIR = os.getenv("IMAGE_DIR", "images")
IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".gif", ".webp")



# ======================
class ImageManager:
    """
    Faz o gerenciamento das imagens de meme:
    - Lê automaticamente a pasta /images
    - Atualiza a lista de tempos em tempos (hot reload)
    - Retorna uma imagem aleatória quando solicitado
    """

    def __init__(self, directory: str, extensions: tuple, rescan_interval: float = 5.0):
        self.directory = directory
        self.extensions = extensions
        self.rescan_interval = rescan_interval
        self._last_scan_time: float = 0.0
        self._images: List[str] = []

    def _scan_images(self) -> None:
        """Atualiza a lista de imagens a partir do diretório."""
        try:
            files = os.listdir(self.directory)
        except FileNotFoundError:
            print(f"⚠️  Pasta de imagens não encontrada: {self.directory}")
            self._images = []
            return

        self._images = [
            os.path.join(self.directory, f)
            for f in files
            if f.lower().endswith(self.extensions)
        ]
        self._last_scan_time = time.time()

        if self._images:
            print(f"🖼️  {len(self._images)} imagem(ns) disponível(is) em '{self.directory}'")
        else:
            print(f"⚠️  Nenhuma imagem válida encontrada em '{self.directory}'")

    def _ensure_images(self) -> None:
        """Reescaneia periodicamente para permitir hot reload."""
        now = time.time()
        if not self._images or (now - self._last_scan_time) > self.rescan_interval:
            self._scan_images()

    def get_random_image(self) -> Optional[str]:
        """Retorna o path de uma imagem aleatória, ou None se não houver nenhuma."""
        self._ensure_images()
        if not self._images:
            return None
        return random.choice(self._images)



# ======================
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils


class PoseDetector:
    """
    Responsável por:
    - Ler a câmera
    - Detectar mãos abertas com MediaPipe
    - Disparar eventos via WebSocket
    - Rodar em modo real ou simulado
    """

    def __init__(
        self,
        server_url: str,
        camera_index: int,
        image_manager: ImageManager,
        detection_cooldown: float = 2.5,
        debug_draw: bool = False,
        simulation_mode: bool = False,
    ):
        self.server_url = server_url
        self.camera_index = camera_index
        self.image_manager = image_manager
        self.detection_cooldown = detection_cooldown
        self.debug_draw = debug_draw
        self.simulation_mode = simulation_mode

        self._last_detection_time: float = 0.0

        # MediaPipe Hands
        self.hands = mp_hands.Hands(
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7,
        )

    # Detectar mãos abertas
    # ----------------------
    @staticmethod
    def is_hand_open(hand_landmarks) -> bool:
        """Verifica se a mão está aberta com base na posição dos dedos."""
        try:
            lm = hand_landmarks.landmark
            return all(
                lm[f_tip].y < lm[f_pip].y
                for f_tip, f_pip in [
                    (mp_hands.HandLandmark.INDEX_FINGER_TIP, mp_hands.HandLandmark.INDEX_FINGER_PIP),
                    (mp_hands.HandLandmark.MIDDLE_FINGER_TIP, mp_hands.HandLandmark.MIDDLE_FINGER_PIP),
                    (mp_hands.HandLandmark.RING_FINGER_TIP, mp_hands.HandLandmark.RING_FINGER_PIP),
                    (mp_hands.HandLandmark.PINKY_TIP, mp_hands.HandLandmark.PINKY_PIP),
                ]
            )
        except Exception:
            return False

    def _can_trigger(self) -> bool:
        """Verifica cooldown para evitar spam de eventos."""
        return (time.time() - self._last_detection_time) > self.detection_cooldown

    def _mark_trigger(self) -> None:
        self._last_detection_time = time.time()

    
    # ----------------------
    async def send_event(self, payload: dict) -> None:
        """Envia um evento pontual: conecta, manda e fecha."""
        for attempt in range(5):
            try:
                async with websockets.connect(self.server_url) as ws:
                    await ws.send(json.dumps(payload))
                    print(f"📤 Evento enviado: {payload}")
                    return
            except Exception as e:
                print(f"⚠️ Falha ao enviar ({e}) — tentativa {attempt + 1}/5")
                await asyncio.sleep(1)
        print("❌ Não foi possível enviar o evento após múltiplas tentativas.")

   
    # ----------------------
    async def run_realtime(self) -> None:
        print(
            f"🎬 Iniciando captura (camera index={self.camera_index}) — enviando para {self.server_url}"
        )
        cap = cv2.VideoCapture(self.camera_index)
        if not cap.isOpened():
            print(f"❌ Erro: não foi possível acessar a câmera (índice {self.camera_index})")
            return

        print("🙌 Mostre as duas mãos abertas para ativar o evento!")

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("⚠️ Falha ao ler frame da câmera. Tentando novamente...")
                    await asyncio.sleep(0.2)
                    continue

                # Espelha para ficar mais natural
                frame = cv2.flip(frame, 1)
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = self.hands.process(rgb_frame)

                open_hands = 0
                if results.multi_hand_landmarks:
                    for hand in results.multi_hand_landmarks:
                        if self.is_hand_open(hand):
                            open_hands += 1
                        if self.debug_draw:
                            mp_drawing.draw_landmarks(
                                frame, hand, mp_hands.HAND_CONNECTIONS
                            )

                # Duas mãos abertas = evento
                if open_hands == 2 and self._can_trigger():
                    meme = self.image_manager.get_random_image()
                    if meme is None:
                        print("⚠️ Nenhuma imagem disponível. Evento não será enviado.")
                    else:
                        self._mark_trigger()
                        payload = {"pose": "two_hands_open", "meme": meme}
                        print(f"📸 Pose detectada: {payload}")
                        await self.send_event(payload)

                cv2.imshow("PoseEdit Detector", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    print("👋 Saindo do detector (tecla 'q' pressionada).")
                    break

        finally:
            cap.release()
            cv2.destroyAllWindows()
            self.hands.close()
            print("🧹 Recursos liberados. Detector encerrado.")

    
    # Modo simulado
    # ----------------------
    async def _simulate_pose_event(self) -> dict:
        """Gera um evento simulado com pose e imagem."""
        poses = ["two_hands_open", "hands_down"]
        pose = random.choice(poses)

        meme = self.image_manager.get_random_image()
        if meme is None:
            # fallback amigável
            meme = "images/placeholder.jpg"
            print("⚠️ Nenhuma imagem encontrada. Usando placeholder no evento simulado.")

        event = {"pose": pose, "meme": meme}
        print(f"🤖 Evento simulado: {event}")
        return event

    async def run_simulation(self) -> None:
        """Mantém conexão estável com o servidor e envia eventos simulados."""
        while True:
            try:
                async with websockets.connect(self.server_url) as ws:
                    print("✅ Conectado ao servidor WebSocket (modo simulado)")

                    while True:
                        event = await self._simulate_pose_event()
                        await ws.send(json.dumps(event))
                        await asyncio.sleep(3)

            except websockets.exceptions.ConnectionClosedError:
                print("⚠️ Conexão encerrada inesperadamente. Tentando reconectar em 2s...")
                await asyncio.sleep(2)
            except ConnectionRefusedError:
                print("❌ Servidor indisponível. Tentando novamente em 3s...")
                await asyncio.sleep(3)
            except Exception as e:
                print(f"💥 Erro inesperado no modo simulado: {e}")
                await asyncio.sleep(3)

   
    # ----------------------
    async def run(self) -> None:
        if self.simulation_mode:
            print("🧪 Executando em modo simulado (SIMULATION_MODE=true)")
            await self.run_simulation()
        else:
            await self.run_realtime()



# ======================
if __name__ == "__main__":
    try:
        img_manager = ImageManager(
            directory=IMAGE_DIR,
            extensions=IMAGE_EXTENSIONS,
            rescan_interval=5.0,  # hot reload a cada 5s
        )

        detector = PoseDetector(
            server_url=SERVER_URL,
            camera_index=CAMERA_INDEX,
            image_manager=img_manager,
            detection_cooldown=DETECTION_COOLDOWN,
            debug_draw=DEBUG_DRAW,
            simulation_mode=SIMULATION_MODE,
        )

        asyncio.run(detector.run())
    except KeyboardInterrupt:
        print("\n👋 Encerrado manualmente pelo usuário.")
