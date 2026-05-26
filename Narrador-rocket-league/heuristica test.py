import easyocr
import os
import warnings

warnings.filterwarnings("ignore")

def analizar_jugadas_con_cooldown():
    print("1. Cargando la Lógica Heurística Bilingüe con Cooldown...")
    lector = easyocr.Reader(['en', 'es'], gpu=False)
    
    carpeta_cache = "frames_cache"
    
    if not os.path.exists(carpeta_cache):
        print("❌ Error: No existe la carpeta caché. Corre el extractor primero.")
        return

    archivos_medallas = [f for f in os.listdir(carpeta_cache) if f.startswith("medalla_")]
    archivos_medallas.sort(key=lambda x: int(x.split('_')[1].split('.')[0]))

    print(f"2. Analizando {len(archivos_medallas)} instantes con filtro de duplicados...\n")
    
    palabras_clave = ["disparo", "salvada", "gol", "goal", "shot", "save", "clear"]
    
    # --- 🧠 VARIABLES DE ESTADO (LA MEMORIA DEL SISTEMA) ---
    ultima_palabra_detectada = None
    ultimo_frame_detectado = -999
    
    # Definimos la ventana de bloqueo en frames.
    # Si tu video es a 30fps, 45 frames equivalen a 1.5 segundos de inmunidad.
    FRAMES_DE_COOLDOWN = 150

    for archivo in archivos_medallas:
        ruta_imagen = os.path.join(carpeta_cache, archivo)
        frame_actual = int(archivo.split('_')[1].split('.')[0])
        
        # Leemos el texto de la medalla
        resultados = lector.readtext(ruta_imagen, detail=0)
        
        if len(resultados) > 0:
            texto_detectado = " ".join(resultados).lower()
            
            for palabra in palabras_clave:
                if palabra in texto_detectado:
                    
                    # --- 🛑 FILTRO HEURÍSTICO DE DUPLICADOS ---
                    # Verificamos si es la misma palabra y si ocurrió muy rápido desde la última vez
                    if palabra == ultima_palabra_detectada and (frame_actual - ultimo_frame_detectado) < FRAMES_DE_COOLDOWN:
                        # Es un duplicado visual en ráfaga, pasamos de largo en silencio
                        break 
                    
                    # Si pasa el filtro, significa que es un evento legítimo o uno nuevo
                    print("======================================================")
                    print(f"🚨 ¡EVENTO REAL DETECTADO EN EL FRAME {frame_actual}!")
                    print(f"🎯 Acción: {palabra.upper()}")
                    print(f"📸 Archivo de contexto: completo_{frame_actual}.jpg")
                    print("======================================================\n")
                    
                    # Guardamos este evento en la memoria para el futuro bloqueo
                    ultima_palabra_detectada = palabra
                    ultimo_frame_detectado = frame_actual
                    
                    break # Salimos del bucle de palabras clave para este frame

    print("✅ Análisis con filtro anti-repetición terminado de forma limpia.")

analizar_jugadas_con_cooldown()