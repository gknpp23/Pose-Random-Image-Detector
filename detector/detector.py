import asyncio
import websockets
import json
import random

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
