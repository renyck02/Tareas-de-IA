import os
import easyocr
import torch
import numpy as np
import scipy.io.wavfile
from PIL import Image
from transformers import ViTImageProcessor, ViTForImageClassification, pipeline
import streamlit as st
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip

@st.cache_resource
# -- Carga de modelos de hugging face --
def cargar_modelos():
    lector = easyocr.Reader(['en', 'es'], gpu=False)
    proc_vit = ViTImageProcessor.from_pretrained("./mi_vit_rocket_league")
    mod_vit = ViTForImageClassification.from_pretrained("./mi_vit_rocket_league")
    ia_texto = pipeline("text-generation", model="Qwen/Qwen2.5-0.5B-Instruct")
    ia_voz = pipeline("text-to-speech", model="facebook/mms-tts-spa")
    return lector, proc_vit, mod_vit, ia_texto, ia_voz

# -- Analisis principal --
def ejecutar_analisis(lector_ocr, procesador_vit, modelo_vit, narrador_ia, narrador_voz, ruta_video_original):
    carpeta_cache = "frames_cache"
    if not os.path.exists(carpeta_cache):
        st.error("No existe la caché de frames. Corre tu extractor primero.")
        return

    carpeta_audio = "audio_cache"
    if not os.path.exists(carpeta_audio):
        os.makedirs(carpeta_audio)

    archivos_medallas = [f for f in os.listdir(carpeta_cache) if f.startswith("medalla_")]
    archivos_medallas.sort(key=lambda x: int(x.split('_')[1].split('.')[0]))

# -- Deteccion de palabras a detectar con el EasyOCR (heuristica) --
    palabras_clave = ["shot", "disparo", "save", "salvada", "clear", "despeje", "goal", "gol"]  
    ultima_palabra = None
    ultimo_frame = -999
    FRAMES_DE_COOLDOWN = 150 
    OFFSET_FRAMES = 25       
    FPS_VIDEO = 30 
    
    audios_para_mezclar = []
    
    for archivo in archivos_medallas:
        ruta_medalla = os.path.join(carpeta_cache, archivo)
        frame_actual = int(archivo.split('_')[1].split('.')[0])
        
# -- Lector de pantalla con EasyOCR --
        resultados_texto = lector_ocr.readtext(ruta_medalla, detail=0)
        if not resultados_texto:
            continue
            
        texto_pantalla = " ".join(resultados_texto).lower()
        texto_pantalla = texto_pantalla.replace("shot on goal", "shot").replace("tiro a puerta", "disparo").replace("tiro a gol", "disparo")
        
        for accion in palabras_clave:
            if accion in texto_pantalla:
                if accion == ultima_palabra and (frame_actual - ultimo_frame) < FRAMES_DE_COOLDOWN:
                    break 
                
                ultima_palabra = accion
                ultimo_frame = frame_actual
                
                st.warning(f"🚨 **[FRAME {frame_actual}]** Detectado: {accion.upper()}")
                
# -- Encontrar el frame completo más cercano al impacto --
                frame_objetivo = max(0, frame_actual - OFFSET_FRAMES)
                archivos_completos = [int(f.split('_')[1].split('.')[0]) for f in os.listdir(carpeta_cache) if f.startswith("completo_")]
                
                if archivos_completos:
                    frame_real_impacto = min(archivos_completos, key=lambda x: abs(x - frame_objetivo))
                    ruta_completa = os.path.join(carpeta_cache, f"completo_{frame_real_impacto}.jpg")
                else:
                    ruta_completa = "ruta_falsa.jpg"
                estilo_jugada = "desconocido"
# -- Analisis visual con IA (ViT)--
                try:
                    imagen_impacto = Image.open(ruta_completa)
                    inputs_vit = procesador_vit(images=imagen_impacto, return_tensors="pt")
                    with torch.no_grad():
                        outputs = modelo_vit(**inputs_vit)
                        id_ganador = outputs.logits.argmax(-1).item()
                        estilo_jugada = modelo_vit.config.id2label[id_ganador]
                except FileNotFoundError:
                    pass
                
                st.caption(f"👁️ Estilo visual detectado: {estilo_jugada.upper()}")

# -- Generacion del prompt de narracion con IA (QWEN)--
                traducciones = {
                    "SAVE": "una salvada espectacular", 
                    "SHOT": "un tiro potente", 
                    "GOAL": "un golazo increíble", 
                    "CLEAR": "un despeje vital"
                }
                accion_esp = traducciones.get(accion.upper(), "una gran jugada")

                if estilo_jugada == "golpe_aereo":
                    contexto_estilo = "un golpe en el aire impresionante."
                elif estilo_jugada == "golpe_suelo":
                    contexto_estilo = "un golpe desde el suelo con mucha fuerza."
                elif estilo_jugada == "maxima_velocidad":
                    contexto_estilo = "con un tiro a una velocidad supersónica."
                else:
                    contexto_estilo = "con muchísima técnica."
# -- Prompt de instrucción para el narrador --
                mensajes = [
                    {"role": "system", "content": "Eres un narrador de partidos de e-sports. Tu trabajo es describir la jugada de Rocket League usando términos técnicos y precisos en una sola oración. Nada de groserías ni exageraciones falsas."},
                    {"role": "user", "content": f"Narracion de la siguiente jugada: {accion_esp} {contexto_estilo}."}
                ]
                
                resultado_ia = narrador_ia(mensajes, max_new_tokens=60, temperature=0.4, do_sample=True)
                narracion_final = resultado_ia[0]['generated_text'][-1]['content'].strip()

                st.success(f"🎙️ **NARRADOR:** {narracion_final}")
              
# -- Generacion de voz con IA (MMS-TTS) -- 
                audio_ia = narrador_voz(narracion_final)
                sample_rate = audio_ia["sampling_rate"]
                datos_crudos = np.array(audio_ia["audio"])
                datos_audio_pcm = (datos_crudos.flatten() * 32767).astype(np.int16)

# -- Creacion de archivo de audio temporal para mezclar luego con el video --  
                archivo_audio = os.path.join(carpeta_audio, f"narracion_{frame_actual}.wav")
                scipy.io.wavfile.write(archivo_audio, rate=sample_rate, data=datos_audio_pcm)
                
# Se calcula cuánto dura este clip de voz exactamente
                duracion_audio = len(datos_audio_pcm) / sample_rate
                tiempo_ideal = frame_actual / FPS_VIDEO
                
                if audios_para_mezclar:
                    ultimo_clip = audios_para_mezclar[-1]
                    tiempo_fin_anterior = ultimo_clip["inicio"] + ultimo_clip["duracion"]
                    
# Si el locutor todavía está hablando, empujamos este audio para que espere su turno
                    if tiempo_ideal < tiempo_fin_anterior:
                        tiempo_ideal = tiempo_fin_anterior + 0.2 # Añadimos 0.2 segundos de respiro
                
# Guardamos los datos en la lista
                audios_para_mezclar.append({
                    "ruta": archivo_audio, 
                    "inicio": tiempo_ideal,
                    "duracion": duracion_audio
                })
                
                st.audio(archivo_audio, format="audio/wav")
                st.markdown("---")
                
                break # Rompemos el ciclo de palabras clave

# -- Mezcla final del audio generado con el video original --
    if audios_para_mezclar:
        st.info("Análisis terminado. Juntando el audio con el video original... (Esto puede tardar unos minutos)")
        
        carpeta_videos = "videos_output"
        if not os.path.exists(carpeta_videos):
            os.makedirs(carpeta_videos)
        
        video = VideoFileClip(ruta_video_original)
        pistas_de_audio = [video.audio]
        
        for clip in audios_para_mezclar:
            narracion = AudioFileClip(clip["ruta"]).set_start(clip["inicio"])
            pistas_de_audio.append(narracion)
            
        audio_final = CompositeAudioClip(pistas_de_audio)
        video = video.set_audio(audio_final)
        
        nombre_salida = os.path.join(carpeta_videos, "partida_narrada_final.mp4")
        
# -- Renderizado del video con gpu final con el audio mezclado --
        video.write_videofile(
            nombre_salida, 
            codec="h264_nvenc", 
            audio_codec="aac", 
            threads=6, 
            ffmpeg_params=["-pix_fmt", "yuv420p"], 
            logger=None
        )
        
        st.success(f"Renderizado terminado, guardado en: `{nombre_salida}`")
        st.video(nombre_salida)
        st.info("Análisis del partido finalizado con éxito.")
    else:
        st.warning("Terminó el análisis pero no se detectaron jugadas para narrar.")