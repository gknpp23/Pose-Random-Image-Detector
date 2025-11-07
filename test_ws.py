import asyncio
import websockets

async def test_ws():
    try:
        async with websockets.connect("ws://127.0.0.1:8000/ws") as ws:
            print("✅ Conectou com sucesso ao servidor WebSocket!")
            await ws.send('{"teste": "ping"}')
            print("📤 Mensagem enviada.")
            reply = await ws.recv()
            print("📩 Resposta recebida:", reply)
    except Exception as e:
        print("❌ Falha na conexão:", e)

asyncio.run(test_ws())
