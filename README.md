# Posedit Random Image Detector  

> Sistema em tempo real que reconhece poses, gestos e expressões faciais e exibe memes aleatórios via WebSocket e overlay web.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)
![MediaPipe](https://img.shields.io/badge/MediaPipe-Hands-orange)
![OpenCV](https://img.shields.io/badge/OpenCV-vision-lightblue)

---

## 🧩 Sobre o Projeto  

O **Poseedit** é um sistema de detecção de gestos construído em **Python**, capaz de identificar quando o usuário realiza poses específicas.  
Quando o gesto é reconhecido, o sistema envia um **evento via WebSocket** para um **servidor FastAPI**, que aciona um **overlay web** — exibindo uma imagem aleatória (meme) na tela em tempo real.

A arquitetura foi projetada para demonstrar comunicação **assíncrona entre Python e Web**, integrando visão computacional, backend e interface interativa.

---

## ✨ Funcionalidades  

✅ **Detecção em tempo real de mãos** com MediaPipe  
✅ **Identificação da pose “duas mãos abertas”**  
✅ **Envio de eventos assíncronos via WebSocket**  
✅ **Servidor FastAPI** responsável por retransmitir os eventos  
✅ **Overlay HTML interativo** que exibe imagens (memes) recebidas  
✅ **Sistema de reconexão automática e tratamento de erros** no cliente Python  
✅ **Arquitetura modular** (detector / servidor / overlay)  

---

## ⚙️ Estrutura do Projeto  

```bash
Pose-Random-Image-Detector/
├── backend/
│   └── server.py          # Servidor FastAPI + WebSocket
│
├── detector/
│   └── detector.py        # Cliente de detecção e envio de eventos
│
├── overlay/
│   └── index.html         # Interface que exibe as imagens em tempo real
│
├── images/
│   ├── calma.jpg
│   ├── davi.jpg
│   └── ...                # Outras imagens utilizadas no overlay
│
├── requirements.txt       # Dependências do projeto
└── README.md              # Este arquivo 😄
````

---

## 🧠 Tecnologias Utilizadas

* **Python 3.12+**
* **[FastAPI](https://fastapi.tiangolo.com/)** → Servidor WebSocket backend
* **[MediaPipe Hands](https://developers.google.com/mediapipe)** → Detecção dos pontos da mão
* **[OpenCV](https://opencv.org/)** → Processamento e captura de vídeo
* **WebSockets (asyncio)** → Comunicação em tempo real entre Python ↔ Front-end
* **HTML + JavaScript** → Overlay leve e reativo para exibir os memes

---

## Como Executar

### 1. Clonar o repositório

```bash
git clone https://github.com/gknpp23/Pose-Random-Image-Detector.git
cd Pose-Random-Image-Detector
```

### 2. Criar e ativar o ambiente virtual

```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```

### 3. Instalar as dependências

```bash
pip install -r requirements.txt
```

### 4. Executar o servidor

```bash
python backend/server.py
```

> O servidor ficará disponível em:
> 📍 `http://127.0.0.1:8000`
> 📡 WebSocket ativo em `ws://127.0.0.1:8000/ws`

### 5. Iniciar o detector

```bash
python detector/detector.py
```

> O detector abrirá o vídeo (webcam ou arquivo) e enviará eventos ao servidor quando a pose for detectada.

### 6. Abrir o overlay

Abra no navegador:

```
http://127.0.0.1:8000/overlay/index.html
```

> Ao detectar a pose, o overlay exibirá uma imagem aleatória da pasta `/images`.

---

## 🧪 Teste de Conexão

Para verificar se o servidor WebSocket está ativo, você pode rodar:

```bash
python test_ws.py
```

Se tudo estiver certo, verá algo como:

```
✅ Conectou com sucesso ao servidor WebSocket!
📩 Resposta recebida: {"teste": "ping"}
```

---

## 🧱 Roadmap Futuro

* [ ] Suporte a múltiplas poses (gestos diferentes)
* [ ] API REST para upload de novas imagens
* [ ] Dashboard web para visualização de métricas em tempo real
* [ ] Deploy em nuvem com Docker + FastAPI
* [ ] Sistema de pontuação gamificado para interações

---

## 🖼️ Exemplo Visual

### 🔹 Interface Web (Overlay)

O overlay exibe automaticamente um meme quando a pose é detectada.
*(Exemplo real do projeto em execução)*

![Overlay Example](https://github.com/gknpp23/Pose-Random-Image-Detector/assets/overlay-example.png)

---

## 📜 Licença

Distribuído sob a licença **MIT**.
Sinta-se livre para usar, modificar e distribuir.
Veja o arquivo `LICENSE` para mais detalhes.

---

## 👨‍💻 Autor

**Gabriel Knupp**
💼 Desenvolvedor & entusiasta de automação e IA
📍 Minas Gerais — Brasil
🌐 [github.com/gknpp23](https://github.com/gknpp23)


