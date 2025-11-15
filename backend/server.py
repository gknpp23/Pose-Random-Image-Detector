import json
from typing import Set

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles



# ======================
app = FastAPI(title="PoseEdit Server", version="1.0")



# ======================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# ======================
app.mount("/images", StaticFiles(directory="images"), name="images")
app.mount("/overlay", StaticFiles(directory="overlay", html=True), name="overlay")




class WebSocketManager:
    """Gerencia os WebSockets conectados de forma simples e direta."""

    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active_connections.add(ws)
        print(f"🟢 Cliente conectado ({len(self.active_connections)} ativo[s])")

    def disconnect(self, ws: WebSocket):
        if ws in self.active_connections:
            self.active_connections.remove(ws)
        print(f"🔴 Cliente desconectado ({len(self.active_connections)} ativo[s] restantes)")

    async def broadcast(self, message: dict):
        """Envia o payload a todos os overlays conectados."""
        dead_clients = []

        for ws in self.active_connections:
            try:
                await ws.send_json(message)
            except Exception as e:
                print(f"⚠️ Falha ao enviar para um cliente: {e}")
                dead_clients.append(ws)

        # remove clientes mortos
        for ws in dead_clients:
            self.disconnect(ws)


ws_manager = WebSocketManager()



# ======================
@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws_manager.connect(ws)

    try:
        while True:
            # recebe eventos do detector
            data = await ws.receive_text()
            payload = json.loads(data)

            print("📨 Evento recebido:", payload)

            # envia para todos os overlays
            await ws_manager.broadcast(payload)

    except Exception as e:
        print(f"❌ Erro na conexão WS: {e}")

    finally:
        ws_manager.disconnect(ws)


# ======================
@app.get("/", response_class=HTMLResponse)
async def root():
    return HTMLResponse(
        """
        <h1>PoseEdit Server</h1>
        <p>Servidor funcionando! 🎉</p>
        <a href='/overlay/index.html'>
            👉 Abrir Overlay
        </a>
        """
    )
