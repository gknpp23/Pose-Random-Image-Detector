<<<<<<< HEAD
import cv2
import mediapipe as mp
=======
>>>>>>> 2ebf81f (feat(core): implementa base completa do PoseAI com backend, detector e overlay integrados)
import asyncio
import websockets
import json
import random
<<<<<<< HEAD
import time
import os
from dotenv import load_dotenv

# ======================
# 🔧 CONFIGURAÇÃO
# ======================
load_dotenv()

SERVER_IP = os.getenv("SERVER_IP", "127.0.0.1")
SERVER_PORT = os.getenv("SERVER_PORT", "8000")
SERVER_URL = f"ws://{SERVER_IP}:{SERVER_PORT}/ws"
CAMERA_INDEX = int(os.getenv("CAMERA_INDEX", 0))
IMAGE_FILENAMES = ["images/davi.jpg", "images/calma.jpg"]
DETECTION_COOLDOWN = 2.5
DEBUG_DRAW = False

# ======================
# 🧠 MEDIA PIPE
# ======================
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7, min_tracking_confidence=0.7)

# ======================
# ✋ LÓGICA DE DETECÇÃO
# ======================
def is_hand_open(hand_landmarks):
    try:
        lm = hand_landmarks.landmark
        return all(
            lm[finger_tip].y < lm[finger_pip].y
            for finger_tip, finger_pip in [
                (mp_hands.HandLandmark.INDEX_FINGER_TIP, mp_hands.HandLandmark.INDEX_FINGER_PIP),
                (mp_hands.HandLandmark.MIDDLE_FINGER_TIP, mp_hands.HandLandmark.MIDDLE_FINGER_PIP),
                (mp_hands.HandLandmark.RING_FINGER_TIP, mp_hands.HandLandmark.RING_FINGER_PIP),
                (mp_hands.HandLandmark.PINKY_TIP, mp_hands.HandLandmark.PINKY_PIP),
            ]
        )
    except Exception:
        return False

# ======================
# 🌐 ENVIO DE EVENTOS
# ======================
async def send_event(payload):
    for attempt in range(5):
        try:
            async with websockets.connect(SERVER_URL) as ws:
                await ws.send(json.dumps(payload))
                print(f"📤 Evento enviado: {payload}")
                return
        except Exception as e:
            print(f"⚠️ Falha ao enviar ({e}) — tentativa {attempt+1}/5")
            await asyncio.sleep(1)
    print("❌ Não foi possível enviar o evento após múltiplas tentativas.")

# ======================
# 🎥 LOOP PRINCIPAL
# ======================
async def main():
    print(f"🎬 Iniciando captura (camera index={CAMERA_INDEX}) — enviando para {SERVER_URL}")
    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        print(f"❌ Erro: não foi possível acessar a câmera (índice {CAMERA_INDEX})")
        return

    print("🙌 Mostre as duas mãos abertas para ativar o evento!")
    last_detection_time = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            await asyncio.sleep(0.5)
            continue

        frame = cv2.flip(frame, 1)
        results = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        open_hands = sum(is_hand_open(hand) for hand in (results.multi_hand_landmarks or []))
        if DEBUG_DRAW and results.multi_hand_landmarks:
            for hand in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)

        if open_hands == 2 and time.time() - last_detection_time > DETECTION_COOLDOWN:
            last_detection_time = time.time()
            meme = random.choice(IMAGE_FILENAMES)
            payload = {"pose": "two_hands_open", "meme": meme}
            print(f"📸 Pose detectada: {payload}")
            await send_event(payload)

        cv2.imshow("PoseEdit Detector", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
    hands.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
<<<<<<< HEAD
        print("\nEncerrado manualmente...")
=======

async def simulate_pose():
    """Simula a detecção de poses e seleciona uma imagem aleatória."""
    poses = ["two_hands_open", "hands_down"]
    memes = ["images/calma.jpg", "images/davi.jpg"]
    pose = random.choice(poses)
    meme = random.choice(memes)
    print(f"🤖 Evento simulado: {meme}")
    return {"pose": pose, "meme": meme}

async def send_events():
    """Mantém conexão estável com o servidor e reenvia em caso de erro."""
    uri = "ws://127.0.0.1:8000/ws"
    while True:
        try:
            async with websockets.connect(uri) as ws:
                print("✅ Conectado ao servidor WebSocket")

                while True:
                    event = await simulate_pose()
                    await ws.send(json.dumps(event))
                    await asyncio.sleep(3)

        except websockets.exceptions.ConnectionClosedError:
            print("⚠️ Conexão encerrada inesperadamente. Tentando reconectar em 2s...")
            await asyncio.sleep(2)

        except ConnectionRefusedError:
            print("❌ Servidor indisponível. Tentando novamente em 3s...")
            await asyncio.sleep(3)

        except Exception as e:
            print(f"💥 Erro inesperado: {e}")
            await asyncio.sleep(3)

async def main():
    await send_events()

if __name__ == "__main__":
    asyncio.run(main())
>>>>>>> 2ebf81f (feat(core): implementa base completa do PoseAI com backend, detector e overlay integrados)
=======
        print("\n👋 Encerrado manualmente.")
>>>>>>> 087df6b (release(v3.0.0): integrate dotenv configuration and WS auto-reconnect overlay)
