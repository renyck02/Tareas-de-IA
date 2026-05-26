import streamlit as st
import os
from main import cargar_modelos, ejecutar_analisis
from extractor import procesar_video_dual

st.set_page_config(page_title="Narrador IA de Rocket League", page_icon="🏎️", layout="wide")

st.title("Narrador de rocket league con Inteligencia Artificial)")
st.markdown("---")

os.makedirs("videos", exist_ok=True)

# Carga Dinámica del Video
video_subido = st.file_uploader("Sube tu clip de Rocket League (.mp4)", type=["mp4"])

if video_subido is not None:
    # Guardamos el archivo subido localmente en ferhp9
    ruta_video_dinamica = os.path.join("videos", video_subido.name)
    
    with open(ruta_video_dinamica, "wb") as f:
        f.write(video_subido.getbuffer())

    col_video, col_narracion = st.columns([7, 3])

    with col_video:
        st.subheader("Video original del partido")
        st.video(ruta_video_dinamica)

    with col_narracion:
        st.subheader("Zona de narracion automatica con IA")
        
        if st.button("Empezar a analizar el clip", use_container_width=True):
            
            with st.spinner("Cargando motores de IA en memoria..."):
                lector, p_vit, m_vit, n_ia, n_voz = cargar_modelos() 
                
            caja_comentarios = st.container(height=500)
            
            with caja_comentarios:
                # Disparamos la cascada enviando la misma variable
                st.info("1. Extrayendo frames del video...")
                procesar_video_dual(ruta_video_dinamica)
                
                st.info("2. Escaneando el partido en busca de jugadas...")
                ejecutar_analisis(lector, p_vit, m_vit, n_ia, n_voz, ruta_video_dinamica)

st.markdown("---")
st.write("Miembros del equipo: Beltran Heredia Jose Armando, Diaz Oleta Rene, Encines Beltran Carlos Gabriel, Monge Shimizu Fernando")