import os
from dotenv import load_dotenv
from analizador import AnalizadorAspectos

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def main():
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("Error: No se encontraron las credenciales en el archivo .env")
        return

    app = AnalizadorAspectos(SUPABASE_URL, SUPABASE_KEY)
    app.procesar_lote_csv("dataset_resenas.csv")

if __name__ == "__main__":
    main()