import cv2
import os

# -- Función para procesar el video y extraer frames completos y recortes de medallas --
def procesar_video_dual(ruta_video):
    print(f"1. Preparando video: {ruta_video}")
    
    if not os.path.exists(ruta_video):
        print("¡ERROR! Python no encuentra el archivo.")
        return

    cap = cv2.VideoCapture(ruta_video)
    alto = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    ancho = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    fps_original = cap.get(cv2.CAP_PROP_FPS)
    
    print(f"2. Resolución: {ancho}x{alto}")

# -- Definicion de la carpeta de caché para guardar los frames --
    carpeta_cache = "frames_cache"
    
    if not os.path.exists(carpeta_cache):
        os.makedirs(carpeta_cache)
    else:
        print("Limpiando el caché viejo para evitar cochinero...")
        for archivo in os.listdir(carpeta_cache):
            ruta_archivo = os.path.join(carpeta_cache, archivo)
            if os.path.isfile(ruta_archivo):
                os.unlink(ruta_archivo)

# -- Zona de recorte para las medallas (ajustable según el video) --
    ymin, ymax = int(alto * 0.15), int(alto * 0.35)
    xmin, xmax = int(ancho * 0.35), int(ancho * 0.65)
    
# -- Extracción de frames completos y recortes de medallas, y saber cada cuanto hacer los cortes --
    contador_frames = 0
    intervalo_frames = int(fps_original / 2) if fps_original > 0 else 1
    frames_guardados = 0

    print("Extrayendo frames completos y recortes de medallas...")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
# -- Guardar un frame completo cada cierto intervalo para el análisis visual, y el recorte de la medalla para el análisis de texto, y el nombre de los frames en el caché --
        if contador_frames % intervalo_frames == 0:
            ruta_completo = os.path.join(carpeta_cache, f"completo_{contador_frames}.jpg")
            cv2.imwrite(ruta_completo, frame)
            
            zona_medalla = frame[ymin:ymax, xmin:xmax]
            ruta_medalla = os.path.join(carpeta_cache, f"medalla_{contador_frames}.jpg")
            cv2.imwrite(ruta_medalla, zona_medalla)
            
            frames_guardados += 1
            
        contador_frames += 1
        
    cap.release()
    print("======================================================")
    print(f"¡Terminado! Se generaron {frames_guardados} pares de imágenes.")
    print("======================================================")