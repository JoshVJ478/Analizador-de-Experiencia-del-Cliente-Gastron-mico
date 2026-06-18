import pandas as pd
import os
from supabase import create_client, Client
from transformers import pipeline
from rich.console import Console
from rich.progress import track
from rich.table import Table

console = Console()

class ProcesadorDatosBase:
    def __init__(self, db_url: str, db_key: str):
        self._conectar_bd(db_url, db_key)

    def _conectar_bd(self, url: str, key: str):
        try:
            console.print("[cyan]Conectando a la base de datos Supabase...[/cyan]")
            self.supabase: Client = create_client(url, key)
            console.print("[bold green]✅ Conexión exitosa a Supabase.[/bold green]")
        except Exception as e:
            raise ConnectionError(f"Error al conectar con Supabase: {e}")

    def _obtener_o_crear_cliente(self, username: str) -> int:
        try:
            respuesta = self.supabase.table('cliente').select('id_cliente').eq('username', username).execute()
            if len(respuesta.data) > 0:
                return respuesta.data[0]['id_cliente']
            else:
                nuevo = self.supabase.table('cliente').insert({"username": username}).execute()
                return nuevo.data[0]['id_cliente']
        except Exception as e:
            console.print(f"[red]Error al gestionar el cliente '{username}': {e}[/red]")
            return None


class AnalizadorAspectos(ProcesadorDatosBase):
    def __init__(self, db_url: str, db_key: str):
        super().__init__(db_url, db_key)
        self._cargar_modelo_ia()
        
        self.etiquetas_aspectos = ['Calidad de Comida', 'Atención del Personal', 'Ambiente del Local']
        self.mapa_sentimientos = {"POS": 1, "NEG": 2, "NEU": 3}

    def _cargar_modelo_ia(self):
        try:
            console.print("[yellow]⏳ Cargando modelo Multilingüe Zero-Shot (MdeBERTa-v3)...[/yellow]")
            self.clasificador = pipeline("zero-shot-classification", model="MoritzLaurer/mDeBERTa-v3-base-mnli-xnli")
            console.print("[bold green]✅ Modelo Zero-Shot cargado y listo.[/bold green]")
        except Exception as e:
            raise RuntimeError(f"❌ Error al cargar el modelo Zero-Shot: {e}")

    def procesar_lote_csv(self, ruta_csv: str):
        console.print(f"\n[bold blue]Iniciando análisis multidimensional del archivo:[/bold blue] {ruta_csv}")
        try:
            df = pd.read_csv(ruta_csv)
            
            total_original = len(df)
            df = df.dropna(subset=['texto_resena'])

            df = df[df['texto_resena'].apply(lambda x: len(str(x).strip().split()) >= 3)]
            console.print(f"[dim]Filtro funcional aplicado: {total_original - len(df)} reseñas descartadas por irrelevantes o vacías.[/dim]\n")
            
            respuesta_aspectos = self.supabase.table('aspecto').select('id_aspecto', 'nombre').execute()
            mapa_aspectos_db = {item['nombre']: item['id_aspecto'] for item in respuesta_aspectos.data}
            
            reporte_local = []
            
            for index, fila in track(df.iterrows(), total=len(df), description="[cyan]Procesando reseñas con IA...[/cyan]"):
                username, texto, id_restaurante = fila['username'], fila['texto_resena'], fila['id_restaurante']
                
                id_cliente = self._obtener_o_crear_cliente(username)
                if not id_cliente: continue
                
                datos_resena_general = {
                    "id_restaurante": id_restaurante,
                    "id_cliente": id_cliente,
                    "texto_original": texto,
                    "id_sentimiento": 3, 
                    "score_confianza_ia": 1.0 
                }
                nueva_resena = self.supabase.table('resena').insert(datos_resena_general).execute()
                id_resena = nueva_resena.data[0]['id_resena']
                
                for aspecto in self.etiquetas_aspectos:
                    hipotesis = [f"el sentimiento sobre {aspecto} es positivo", f"el sentimiento sobre {aspecto} es negativo"]
                    resultado = self.clasificador(texto, hipotesis, multi_label=False)
                    
                    etiqueta_ganadora = resultado['labels'][0]
                    confianza = round(resultado['scores'][0], 4)
                    
                    id_sentimiento_aspecto = 1 if "positivo" in etiqueta_ganadora else 2 if "negativo" in etiqueta_ganadora else 3
                    
                    datos_aspecto = {
                        "id_resena": id_resena,
                        "id_aspecto": mapa_aspectos_db.get(aspecto),
                        "id_sentimiento": id_sentimiento_aspecto,
                        "score_confianza_ia": confianza
                    }
                    self.supabase.table('resena_aspecto').insert(datos_aspecto).execute()
                    
                    estado = "POSITIVO" if id_sentimiento_aspecto == 1 else ("NEGATIVO" if id_sentimiento_aspecto == 2 else "NEUTRO")
                    reporte_local.append({
                        "Usuario": username,
                        "Aspecto Evaluado": aspecto,
                        "Sentimiento IA": estado,
                        "Confianza": f"{confianza*100:.2f}%"
                    })
                    
            df_reporte = pd.DataFrame(reporte_local)
            
            directorio_base = os.path.dirname(os.path.abspath(__file__))
            ruta_reportes = os.path.join(directorio_base, "reportes")
            os.makedirs(ruta_reportes, exist_ok=True) 
            
            ruta_salida = os.path.join(ruta_reportes, "reporte_ejecutivo.csv")
            df_reporte.to_csv(ruta_salida, index=False)
            
            print("\n")
            tabla = Table(title="📊 Resumen de Ejecución ETL")
            tabla.add_column("Métrica Operativa", justify="left", style="cyan", no_wrap=True)
            tabla.add_column("Resultado", justify="right", style="magenta")
            
            tabla.add_row("Reseñas Validas Procesadas", str(len(df)))
            tabla.add_row("Dimensiones Evaluadas", str(len(reporte_local)))
            tabla.add_row("Reporte Generado", "reporte_ejecutivo.csv")
            
            console.print(tabla)
            console.print("[bold green]✅ ¡Pipeline ejecutado y cargado en Supabase con éxito![/bold green]\n")

        except Exception as e:
            console.print(f"[bold red]❌ Ocurrió un error inesperado: {e}[/bold red]")