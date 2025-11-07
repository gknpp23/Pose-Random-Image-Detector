from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import json

app = FastAPI()

# 🔓 Libera tudo (inclusive WS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔹 Servindo imagens e overlay pelo mesmo host/porta
app.mount("/images", StaticFiles(directory="images"), name="images")
app.mount("/overlay", StaticFiles(directory="overlay"), name="overlay")

clients = set()

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    clients.add(ws)
    print(f"🟢 Cliente conectado ({len(clients)} ativo[s])")

    try:
        while True:
            data = await ws.receive_text()
            payload = json.loads(data)
            print("📨 Evento recebido:", payload)

            for client in clients.copy():
                try:
                    await client.send_json(payload)
                except Exception:
                    clients.remove(client)
                    print("⚪ Cliente removido (erro no envio)")
    except Exception as e:
        print("❌ Erro WS:", e)
    finally:
        clients.remove(ws)
        print(f"🔴 Cliente desconectado. Restam {len(clients)} ativo(s).")

@app.get("/")
async def home():
    return HTMLResponse("<h1>Servidor PoseAI ativo 🚀</h1>")
