# Importação das bibliotecas necessárias
import cv2                # OpenCV: usada para captura e manipulação de vídeo/imagem
import re                 # Expressões regulares: usada para validar o formato das placas
import easyocr            # Biblioteca de OCR (Reconhecimento Óptico de Caracteres)
import json               # Para salvar os resultados em arquivos JSON
from loguru import logger # Biblioteca para exibir logs de forma amigável
from datetime import datetime  # Para registrar a hora da detecção da placa

# Definição da classe principal do sistema de detecção de placas em tempo real
class RealTimePlateDetector:
    
    # Método construtor, executado quando a classe é instanciada
    def __init__(self, decoder='beamsearch'):
        # Inicializa o leitor OCR com suporte ao idioma inglês
        self.reader = easyocr.Reader(['en'])
        
        # Define qual decodificador será usado (pode ser: 'greedy', 'beamsearch' ou 'wordbeamsearch')
        self.decoder = decoder
        
        # Lista para armazenar os dados das placas detectadas
        self.plates_detected = []

    # Função para validar se um texto reconhecido está no formato de uma placa brasileira
    def is_valid_plate(self, plate):
        # Expressão regular para o padrão AAA0A00 (padrão de placas no Brasil a partir de 2018)
        pattern = r"^[A-Z]{3}[0-9][0-9A-Z][0-9]{2}$"
        return bool(re.fullmatch(pattern, plate))

    # Função que processa um único frame (imagem) da câmera
    def process_frame(self, frame):
        # Usa OCR para tentar identificar textos na imagem
        results = self.reader.readtext(frame, decoder=self.decoder)
        
        # Lista para armazenar todas as placas encontradas no frame
        plates_in_frame = []

        # Percorre os resultados encontrados pelo OCR
        for bbox, text, precision in results:
            # Limpa o texto reconhecido (remove traços e espaços)
            cleaned_text = text.replace('-', '').replace(' ', '').upper()

            # Verifica se o texto é uma placa válida e se a confiança (precisão) é suficiente
            if precision > 0.75 and self.is_valid_plate(cleaned_text):
                now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Registra a hora da detecção
                
                # Armazena os dados da placa
                plate_data = {
                    "plate": cleaned_text,
                    "precision": round(precision, 3),
                    "time": now
                }
                plates_in_frame.append((plate_data, bbox))  # Guarda junto com as coordenadas da placa
        
        return plates_in_frame  # Retorna todas as placas detectadas neste frame

    # Função para desenhar retângulos e textos na imagem com os dados da placa
    def draw_plate_info(self, frame, plate_data, bbox):
        text = plate_data["plate"]  # Pega o texto da placa
        top_left = tuple(map(int, bbox[0]))       # Canto superior esquerdo do retângulo
        bottom_right = tuple(map(int, bbox[2]))   # Canto inferior direito do retângulo

        # Desenha o retângulo na imagem
        cv2.rectangle(frame, top_left, bottom_right, (0, 255, 0), 2)
        
        # Escreve o texto da placa acima do retângulo
        cv2.putText(frame, f'{text}', (top_left[0], top_left[1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    # Função principal para capturar vídeo da câmera e processar em tempo real
    def run_camera(self):
        cap = cv2.VideoCapture(0)  # 0 indica a webcam padrão do computador

        if not cap.isOpened():  # Verifica se a câmera foi aberta corretamente
            logger.error("Erro ao abrir a câmera")
            return

        logger.info("Pressione 'q' para sair")
        frame_count = 0  # Contador de frames

        while True:
            ret, frame = cap.read()  # Captura um frame da câmera
            if not ret:
                break

            frame_count += 1

            # Processa um frame a cada 15 (para não sobrecarregar o processamento)
            if frame_count % 15 == 0:
                plates_in_frame = self.process_frame(frame)

                # Para cada placa detectada, desenha na imagem e salva
                for plate_data, bbox in plates_in_frame:
                    logger.success(f"PLACA DETECTADA: {plate_data}")
                    self.plates_detected.append(plate_data)
                    self.draw_plate_info(frame, plate_data, bbox)

            # Exibe a imagem com anotações em tempo real
            cv2.imshow('Detecção de Placas em Tempo Real', frame)

            # Se o usuário pressionar a tecla 'q', o programa é encerrado
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Encerra a captura da câmera e fecha as janelas
        cap.release()
        cv2.destroyAllWindows()

        # Salva os dados das placas detectadas em um arquivo JSON com timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        with open(f'plates_realtime_{timestamp}.json', 'w') as f:
            json.dump(self.plates_detected, f, indent=4)
        logger.info("Processamento finalizado e dados salvos.")

# Bloco principal: roda quando o script é executado diretamente
if __name__ == '__main__':
    detector = RealTimePlateDetector(decoder='beamsearch')  # Cria o detector com o decodificador escolhido
    detector.run_camera()  # Inicia o processamento da câmera

