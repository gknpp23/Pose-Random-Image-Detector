# PoseEdit Lite

Overlay básico que exibe imagens na tela quando recebe eventos do servidor Python via WebSocket.  
Versão simplificada para estudos e uso no OBS.

## Como funciona
- O servidor Python (FastAPI) envia eventos pelo endpoint `/ws`.
- O overlay recebe mensagens contendo o campo `"meme"`.
- Quando recebe `{ "meme": "images/arquivo.jpg" }`, mostra a imagem por alguns segundos e depois some.

## Estrutura
- overlay/index.html — overlay usado no navegador ou OBS
- overlay/config.js — configura IP, porta e tempo de exibição
- images/ — imagens servidas pelo backend
- backend/server.py — servidor WebSocket em Python (FastAPI)

## Como usar
1. Ajuste `overlay/config.js` com o IP e porta do backend.
2. Inicie o servidor:
```bash
uvicorn backend.server:app --host 0.0.0.0 --port 8000
```
3. Abra o overlay:
```
http://SEU_IP:800.0.0.0:8000/overlay/index.html
```
4. O detector ou simulação envia eventos assim:
```json
{ "pose": "two_hands_open", "meme": "images/calma.jpg" }
```

## OBS (Browser Source)
- Adicione uma fonte “Browser”.
- Defina a URL do overlay:
```
http://SEU_IP:8000/overlay/index.html
```
- Ative fundo transparente com:
```
body { background: rgba(0,0,0,0) !important; }
```

## Licença
MIT.
