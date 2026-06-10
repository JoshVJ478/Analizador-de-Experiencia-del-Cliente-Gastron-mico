import streamlit as st
import pandas as pd
from supabase import create_client, Client
import os
from dotenv import load_dotenv
import plotly.express as px

# 1. Configuración de página
st.set_page_config(page_title="Dashboard Gerencial", layout="wide")
st.title("📊 Panel de Inteligencia de Negocio - Restaurante")

# 2. Conectar a Supabase
load_dotenv()
supabase: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

# 3. Función optimizada para extraer datos
@st.cache_data(ttl=60)
def cargar_datos():
    respuesta = supabase.table('resena_aspecto').select(
        'id_sentimiento, aspecto(nombre), resena(texto_original)'
    ).execute()
    
    if not respuesta.data:
        return pd.DataFrame()
        
    df = pd.DataFrame(respuesta.data)
    df['aspecto'] = df['aspecto'].apply(lambda x: x['nombre'])
    df['texto'] = df['resena'].apply(lambda x: x['texto_original'])
    
    mapa_visual = {1: "✅ POSITIVO", 2: "❌ NEGATIVO", 3: "➖ NEUTRO"}
    df['sentimiento_visual'] = df['id_sentimiento'].map(mapa_visual)
    
    mapa_grafico = {1: "POSITIVO", 2: "NEGATIVO", 3: "NEUTRO"}
    df['sentimiento_grafico'] = df['id_sentimiento'].map(mapa_grafico)
    
    return df

# --- 🛠️ NUEVO FEATURE: SECCIÓN DE CARGA AUTÓNOMA PARA EL GERENTE ---
st.sidebar.header("⚙️ Panel de Administración")
st.sidebar.markdown("Carga un nuevo archivo de reseñas para procesar con el motor de IA.")

archivo_subido = st.sidebar.file_uploader(
    "Selecciona el archivo CSV de reseñas", 
    type=["csv"],
    help="El archivo debe incluir las columnas estándar: username, texto_resena, id_restaurante"
)

if archivo_subido is not None:
    st.sidebar.info("📂 Archivo cargado temporalmente en memoria.")
    
    # Botón interactivo para disparar el backend
    if st.sidebar.button("🧠 Ejecutar Análisis con IA"):
        with st.spinner("La IA está clasificando los aspectos y sentimientos. Por favor espera..."):
            try:
                # Leemos la data directamente del buffer de Streamlit a un DataFrame
                df_nuevo = pd.read_csv(archivo_subido)
                
                # Importación dinámica para evitar conflictos antes de refactorizar main.py
                from main import procesar_nuevas_resenas
                
                # Enviamos el DataFrame cargado al motor ETL de IA
                procesar_nuevas_resenas(df_nuevo)
                
                st.sidebar.success("🚀 ¡Base de datos actualizada con éxito!")
                
                # Forzamos la limpieza de la caché de Streamlit para leer la nueva data al instante
                st.cache_data.clear()
                st.rerun()
                
            except Exception as e:
                st.sidebar.error(f"❌ Ocurrió un error en el proceso: {e}")

# --- 4. CONSTRUCCIÓN VISUAL PRINCIPAL ---
df_analisis = cargar_datos()

if df_analisis.empty:
    st.warning("⚠️ No hay datos en la base de datos para mostrar.")
else:
    st.subheader("💡 Resumen de Fortalezas y Debilidades")
    col1, col2 = st.columns(2)
    
    positivos = df_analisis[df_analisis['id_sentimiento'] == 1].groupby('aspecto').size()
    fortaleza = positivos.idxmax() if not positivos.empty else "N/A"
    
    negativos = df_analisis[df_analisis['id_sentimiento'] == 2].groupby('aspecto').size()
    debilidad = negativos.idxmax() if not negativos.empty else "N/A"
    
    with col1:
        st.success(f"**🏆 Mayor Fortaleza:** {fortaleza}")
    with col2:
        st.error(f"**⚠️ Área Crítica a Mejorar:** {debilidad}")
        
    st.divider()

    df_agrupado = df_analisis.groupby(['aspecto', 'sentimiento_grafico']).size().reset_index(name='cantidad')
    fig = px.bar(
        df_agrupado, x="aspecto", y="cantidad", color="sentimiento_grafico",
        title="Satisfacción del Cliente por Categoría",
        color_discrete_map={"POSITIVO": "#28a745", "NEGATIVO": "#dc3545", "NEUTRO": "#ffc107"},
        barmode="group"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.divider()

    st.subheader("📝 Análisis Detallado por Comentario (Anónimo)")
    st.markdown("Observa cómo la IA desglosó cada reseña en múltiples calificaciones:")
    
    df_pivot = df_analisis.pivot_table(
        index='texto', 
        columns='aspecto', 
        values='sentimiento_visual', 
        aggfunc='first'
    ).reset_index()
    
    df_pivot.rename(columns={'texto': 'Comentario Original del Cliente'}, inplace=True)
    
    st.dataframe(df_pivot, use_container_width=True, hide_index=True)