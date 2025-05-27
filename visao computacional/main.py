# Importa bibliotecas essenciais para o funcionamento do script
import cv2                    # OpenCV para trabalhar com vídeo e imagens
import os                     # Para operações com o sistema de arquivos
import re                     # Expressões regulares para validar placas
import easyocr                # OCR para extrair textos de imagens
import json                   # Para salvar resultados em JSON
from glob import glob         # Para buscar arquivos com padrão (ex: *.jpg)
from tqdm import tqdm         # Barra de progresso no terminal
from loguru import logger     # Ferramenta de logging avançada

# Classe principal para análise de placas
class PlateDataAnalysis:
  def __init__(self) -> None:
    self.plates = []                          # Lista para armazenar placas encontradas
    self.reader = easyocr.Reader(['en'])      # Inicializa OCR para idioma inglês

  # Converte vídeo em imagens (1 frame a cada 15)
  def convert_video_to_images(self, video_path:str, images_folder:str):
    cam = cv2.VideoCapture(video_path)        # Abre o vídeo

    try:
        if not os.path.exists(images_folder): # Cria pasta se não existir
            os.makedirs(images_folder)
            first_time = True
        else:
          first_time = False                  # Se já existe, não extrai de novo
          logger.info('Path already exists')

    except OSError:
        logger.error(f'Error: Creating directory of {images_folder}') 

    # Só extrai frames se for a primeira vez
    if first_time:
      currentframe = 0
      while cam.isOpened():
          ret, frame = cam.read()             # Lê um frame

          if ret:
              name = f'./{images_folder}/frame_{str(currentframe)}.jpg'
              logger.info(f'Processing Frame: {currentframe}')

              cv2.imwrite(name, frame)        # Salva imagem do frame
              cam.set(cv2.CAP_PROP_POS_FRAMES, currentframe)  # Ajusta posição do vídeo
              currentframe += 15              # Pula 15 frames
          else:
              cam.release()
              break

      cam.release()                           # Libera recursos
      cv2.destroyAllWindows()
      return True

    return False                              # Se já extraiu antes, retorna False

  # Verifica se texto corresponde a padrão de placa (Mercosul)
  def is_valid_plate(self, plate):
    pattern = r"^[A-Z]{3}[0-9][0-9A-Z][0-9]{2}$"   # Ex: ABC1D23
    return bool(re.fullmatch(pattern, plate))

  # Aplica OCR na imagem
  def read_text_from_image(self, path_image:str, decoder:str):
      try:
          results = self.reader.readtext(path_image, decoder=decoder)
          return results
      except Exception as e:
          logger.error(e)
          return None   

  # Filtra os textos detectados para encontrar placas válidas
  def filter_plates(self, text_items:str):
      for item in text_items:
          text = item[1].replace('-','').replace(' ','').upper()  # Normaliza texto
          precision = item[2]                                     # Precisão do OCR

          logger.info(f'extracted text: {text} precision {precision}')

          is_plate = self.is_valid_plate(text)                   # Verifica formato
          if precision > 0.75 and is_plate:
            data = {
              "plate": text,
              "precision": precision
            }
            return data                                          # Retorna se for válida
      return None

  # Lista imagens no caminho informado
  def list_images(self, path:str):
     jpgs = glob(path)       # Busca arquivos com padrão
     return jpgs

# Bloco principal
if __name__ == '__main__':
  decoder = 'beamsearch'     # Define decodificador usado pelo OCR

  plate_analysis = PlateDataAnalysis()                              # Cria objeto principal
  plate_analysis.convert_video_to_images('./videoplayback.mp4', 'images')  # Extrai imagens
  images_list = plate_analysis.list_images('./images/*')            # Lista imagens extraídas

  plates_list = {}       # Dicionário com placas válidas e precisões

  # Para cada imagem, tenta extrair texto e validar como placa
  for image in tqdm(images_list):
      texts = plate_analysis.read_text_from_image(image, decoder)   # OCR na imagem
      text_plate = plate_analysis.filter_plates(texts)              # Tenta identificar placa
      logger.info(f'plate text:  {text_plate}')

      # Só salva se a precisão for maior do que uma já existente
      if text_plate and text_plate['precision'] > plates_list.get(text_plate['plate'], 0):
          plates_list[text_plate['plate']] = text_plate['precision']
      logger.info('Not a valid plate')

  # Salva resultados em um arquivo JSON
  with open(f'./plates_{decoder}.json', 'w') as file:
    json.dump(plates_list, file, indent=4)

logger.info('Processing Finished')   # Indica fim do processamento
