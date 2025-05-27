# 📷 OCR em Tempo Real para Placas de Veículos

Este projeto realiza a **detecção de placas veiculares em tempo real** a partir de uma webcam, utilizando **EasyOCR** e **OpenCV**. As placas no padrão brasileiro (Mercosul) são extraídas com alta precisão e armazenadas com data e hora da detecção.

---

## 🚀 Funcionalidades

- Captura de vídeo da webcam em tempo real  
- Extração de texto (OCR) com EasyOCR  
- Reconhecimento de múltiplas placas por frame  
- Validação com Regex (padrão Mercosul)  
- Armazenamento da placa com **precisão e timestamp**  
- Exibição ao vivo com as placas sobrepostas no vídeo  
- Geração de relatório JSON com as placas detectadas  

---

## 🧠 Tecnologias Usadas

- [Python 3.8+](https://www.python.org/)
- [OpenCV](https://opencv.org/)
- [EasyOCR](https://github.com/JaidedAI/EasyOCR)
- [Loguru](https://github.com/Delgan/loguru)

---

## 📦 Instalação

1. Clone o repositório:
```bash
git clone https://github.com/AndrePontes08/Placas-veiculares-em-tempo-real.git
cd ocr-placas-realtime
```

2. Crie e ative um ambiente virtual (opcional):
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

> **Ou, instale manualmente:**
```bash
pip install opencv-python easyocr loguru
```

---

## ▶️ Como Usar

Execute o script principal:

```bash
python ocr_placas_realtime.py
```

- A webcam será ativada automaticamente.
- As placas reconhecidas serão exibidas no vídeo com suas respectivas precisões.
- Um arquivo `plates_realtime_YYYYMMDD_HHMMSS.json` será salvo com as detecções.

Pressione **`q`** para encerrar o programa.

---

## ⚙️ Parâmetros Ajustáveis

| Parâmetro           | Local do Código             | Descrição                                     |
|---------------------|-----------------------------|-----------------------------------------------|
| `precision > 0.75`  | `if precision > 0.75:`      | Define o limiar de confiança mínimo           |
| `frame_count % 15`  | `if frame_count % 15 == 0:` | Define a frequência de detecção por frame     |
| `decoder`           | `decoder = 'beamsearch'`    | Algoritmo OCR: 'greedy', 'beamsearch' ou 'wordbeamsearch' |

---

## 🧪 Exemplo de Saída

```json
[
  {
    "plate": "ABC1D23",
    "precision": 0.912,
    "time": "2025-05-26 21:43:07"
  },
  {
    "plate": "XYZ2K98",
    "precision": 0.878,
    "time": "2025-05-26 21:44:09"
  }
]
```

---

## 📄 Licença

Este projeto está sob a licença [MIT](LICENSE).

---

## 🤝 Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou pull requests.

---

## 📬 Contato

Desenvolvido por **Andre Pontes Vaz de Medeiros Filho**  
🌐 [LinkedIn](https://www.linkedin.com/in/andre-pontes-vaz-de-medeiros-filho/)
