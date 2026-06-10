import os
import pandas as pd
from dotenv import load_dotenv
from analizador import AnalizadorAspectos

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def procesar_nuevas_resenas(df):
    """
    Función puente para Streamlit.
    Recibe un DataFrame, lo procesa con la IA y limpia los residuos temporales.
    """
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("Error: No se encontraron las credenciales en el archivo .env")

    # 1. Guardar el archivo subido en la web como un CSV temporal local
    ruta_temporal = "temp_dataset_resenas.csv"
    df.to_csv(ruta_temporal, index=False)
    
    try:
        # 2. Inicializar tu motor de IA y procesar el archivo temporal
        app = AnalizadorAspectos(SUPABASE_URL, SUPABASE_KEY)
        app.procesar_lote_csv(ruta_temporal)
    finally:
        # 3. Limpieza de seguridad: Borrar el archivo temporal pase lo que pase
        if os.path.exists(ruta_temporal):
            os.remove(ruta_temporal)

def main():
    """Función original para mantener la ejecución clásica desde la consola."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("Error: No se encontraron las credenciales en el archivo .env")
        return

    app = AnalizadorAspectos(SUPABASE_URL, SUPABASE_KEY)
    app.procesar_lote_csv("dataset_resenas.csv")

if __name__ == "__main__":
    main()