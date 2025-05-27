import cv2
import re
import easyocr
import json
from loguru import logger
from datetime import datetime

class RealTimePlateDetector:
    def __init__(self, decoder='beamsearch'):
        self.reader = easyocr.Reader(['en'])
        self.decoder = decoder
        self.plates_detected = []

    def is_valid_plate(self, plate):
        pattern = r"^[A-Z]{3}[0-9][0-9A-Z][0-9]{2}$"
        return bool(re.fullmatch(pattern, plate))

    def process_frame(self, frame):
        results = self.reader.readtext(frame, decoder=self.decoder)
        plates_in_frame = []

        for bbox, text, precision in results:
            cleaned_text = text.replace('-', '').replace(' ', '').upper()

            if precision > 0.75 and self.is_valid_plate(cleaned_text):
                now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                plate_data = {
                    "plate": cleaned_text,
                    "precision": round(precision, 3),
                    "time": now
                }
                plates_in_frame.append((plate_data, bbox))
        
        return plates_in_frame

    def draw_plate_info(self, frame, plate_data, bbox):
        text = plate_data["plate"]
        top_left = tuple(map(int, bbox[0]))
        bottom_right = tuple(map(int, bbox[2]))

        cv2.rectangle(frame, top_left, bottom_right, (0, 255, 0), 2)
        cv2.putText(frame, f'{text}', (top_left[0], top_left[1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    def run_camera(self):
        cap = cv2.VideoCapture(0)  # 0 = webcam padrão

        if not cap.isOpened():
            logger.error("Erro ao abrir a câmera")
            return

        logger.info("Pressione 'q' para sair")
        frame_count = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1

            if frame_count % 15 == 0:  # Processa a cada 15 frames
                plates_in_frame = self.process_frame(frame)

                for plate_data, bbox in plates_in_frame:
                    logger.success(f"PLACA DETECTADA: {plate_data}")
                    self.plates_detected.append(plate_data)
                    self.draw_plate_info(frame, plate_data, bbox)

            cv2.imshow('Detecção de Placas em Tempo Real', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

        # Salvar placas detectadas
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        with open(f'plates_realtime_{timestamp}.json', 'w') as f:
            json.dump(self.plates_detected, f, indent=4)
        logger.info("Processamento finalizado e dados salvos.")

if __name__ == '__main__':
    detector = RealTimePlateDetector(decoder='beamsearch')
    detector.run_camera()
