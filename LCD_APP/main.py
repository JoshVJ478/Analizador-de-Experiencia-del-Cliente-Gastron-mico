import os
import sys
from dotenv import load_dotenv
from analizador import AnalizadorAspectos
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

console = Console()

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def mostrar_menu():
    """Dibuja el menú principal en la consola"""
    console.print("\n[bold yellow]📌 MENÚ DE ADMINISTRACIÓN GLOBAL[/bold yellow]")
    console.print("1. 🚀 Ejecutar Pipeline ETL (Analizar dataset local)")
    console.print("2. 📊 Consultar Últimos Registros (Read)")
    console.print("3. 🧹 Purgar Entorno de Pruebas (Delete masivo)")
    console.print("4. ❌ Salir")
    return Prompt.ask("[bold cyan]Seleccione una opción[/bold cyan]", choices=["1", "2", "3", "4"])

def consultar_registros(app):
    """Realiza un SELECT a Supabase para demostrar lectura de datos"""
    console.print("\n[cyan]Obteniendo las últimas 5 reseñas de Supabase...[/cyan]")
    try:
        respuesta = app.supabase.table('resena').select('*').order('id_resena', desc=True).limit(5).execute()
        datos = respuesta.data
        
        if not datos:
            console.print("[yellow]La base de datos se encuentra vacía.[/yellow]")
            return

        tabla = Table(title="📊 Últimas Reseñas Procesadas")
        tabla.add_column("ID Reseña", style="cyan", justify="center")
        tabla.add_column("ID Cliente", style="magenta", justify="center")
        tabla.add_column("Texto Original", style="green")

        for fila in datos:
            texto = fila['texto_original']
            if len(texto) > 60:
                texto = texto[:57] + "..."
            tabla.add_row(str(fila['id_resena']), str(fila['id_cliente']), texto)

        console.print(tabla)
    except Exception as e:
        console.print(f"[bold red]❌ Error al consultar la base de datos: {e}[/bold red]")

def purgar_base_datos(app):
    """Realiza un DELETE estructurado para limpiar el entorno"""
    confirmacion = Prompt.ask(
        "[bold red]⚠️ ¿Está seguro que desea ELIMINAR TODOS los registros de las tablas? (s/n)[/bold red]", 
        choices=["s", "n"], default="n"
    )
    
    if confirmacion.lower() == 's':
        console.print("[yellow]Purgando tablas en orden de dependencias...[/yellow]")
        try:
            app.supabase.table('resena_aspecto').delete().neq('id_resena', 0).execute()
            app.supabase.table('resena').delete().neq('id_resena', 0).execute()
            app.supabase.table('cliente').delete().neq('id_cliente', 0).execute()
            
            console.print("[bold green]✅ Entorno de pruebas purgado correctamente. Tablas limpias.[/bold green]")
        except Exception as e:
            console.print(f"[bold red]❌ Error al purgar la base de datos: {e}[/bold red]")
    else:
        console.print("[cyan]Operación cancelada por el usuario.[/cyan]")

def main():
    directorio_actual = os.path.dirname(os.path.abspath(__file__))
    ruta_csv = os.path.join(directorio_actual, "datasets", "dataset_resenas.csv")
    console.print(Panel.fit("🧠 Analizador de Experiencia Gastronómica [Pipeline ETL]", style="bold cyan"))
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        console.print("[bold red]❌ Error: No se encontraron las credenciales en el archivo .env[/bold red]")
        return

    app = AnalizadorAspectos(SUPABASE_URL, SUPABASE_KEY)
    
    while True:
        opcion = mostrar_menu()
        
        if opcion == "1":
            app.procesar_lote_csv(ruta_csv)
        elif opcion == "2":
            consultar_registros(app)
        elif opcion == "3":
            purgar_base_datos(app)
        elif opcion == "4":
            console.print("[bold green]¡Cerrando motor analítico! Hasta luego. 👋[/bold green]")
            sys.exit(0)

if __name__ == "__main__":
    main()