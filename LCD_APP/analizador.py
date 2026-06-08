import pandas as pd
from supabase import create_client, Client
from transformers import pipeline

class ProcesadorDatosBase:
    def __init__(self, db_url: str, db_key: str):
        self._conectar_bd(db_url, db_key)

    def _conectar_bd(self, url: str, key: str):
        try:
            print("Conectando a la base de datos Supabase...")
            self.supabase: Client = create_client(url, key)
            print("Conexión exitosa a Supabase.")
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
            print(f"Error al gestionar el cliente '{username}': {e}")
            return None


class AnalizadorGeneral(ProcesadorDatosBase):
    def __init__(self, db_url: str, db_key: str):
        super().__init__(db_url, db_key)
        self._cargar_modelo_ia()
        self.mapa_sentimientos = {"POS": 1, "NEG": 2, "NEU": 3}

    def _cargar_modelo_ia(self):
        try:
            print("Cargando modelo de Inteligencia Artificial de Hugging Face...")
            self.clasificador = pipeline("sentiment-analysis", model="pysentimiento/robertuito-sentiment-analysis")
            print("Modelo de IA cargado y listo.")
        except Exception as e:
            raise RuntimeError(f"Error al cargar el modelo de Hugging Face: {e}")

    def procesar_lote_csv(self, ruta_csv: str):
        print(f"\nIniciando procesamiento del archivo: {ruta_csv}")
        try:
            df = pd.read_csv(ruta_csv)
            
            for index, fila in df.iterrows():
                username = fila['username']
                texto = fila['texto_resena']
                id_restaurante = fila['id_restaurante']

                id_cliente = self._obtener_o_crear_cliente(username)
                if not id_cliente:
                    continue 
                
                resultado_ia = self.clasificador(texto)[0]
                etiqueta_ia = resultado_ia['label']
                score = round(resultado_ia['score'], 4)
                
                id_sentimiento = self.mapa_sentimientos.get(etiqueta_ia, 3)
                
                datos_insercion = {
                    "id_restaurante": id_restaurante,
                    "id_cliente": id_cliente,
                    "texto_original": texto,
                    "id_sentimiento": id_sentimiento,
                    "score_confianza_ia": score
                }
                self.supabase.table('resena').insert(datos_insercion).execute()
                
                print(f"  -> Reseña de {username} | IA: {etiqueta_ia} (Confianza: {score}) | Guardado en BD ✅")
                
            print("\nProcesamiento completado al 100%. Revisa tu tabla 'resena' en Supabase.")

        except FileNotFoundError:
            print(f"No se encontró el archivo {ruta_csv}. Verifica la ruta.")
        except Exception as e:
            print(f"Ocurrió un error inesperado durante el procesamiento: {e}")


class AnalizadorAspectos(ProcesadorDatosBase):
    def __init__(self, db_url: str, db_key: str):
        super().__init__(db_url, db_key)
        self._cargar_modelo_ia()
        
        self.etiquetas_aspectos = ['Calidad de Comida', 'Atención del Personal', 'Ambiente del Local']
        self.mapa_sentimientos = {"POS": 1, "NEG": 2, "NEU": 3}

    def _cargar_modelo_ia(self):
        try:
            print("⏳ Cargando modelo Multilingüe Zero-Shot (MdeBERTa-v3)...")
            self.clasificador = pipeline("zero-shot-classification", model="MoritzLaurer/mDeBERTa-v3-base-mnli-xnli")
            print("✅ Modelo Zero-Shot cargado y listo.")
        except Exception as e:
            raise RuntimeError(f"❌ Error al cargar el modelo Zero-Shot: {e}")

    def procesar_lote_csv(self, ruta_csv: str):
        print(f"\nIniciando análisis multidimensional del archivo: {ruta_csv}")
        try:
            df = pd.read_csv(ruta_csv)
            
            respuesta_aspectos = self.supabase.table('aspecto').select('id_aspecto', 'nombre').execute()
            mapa_aspectos_db = {item['nombre']: item['id_aspecto'] for item in respuesta_aspectos.data}
            
            for index, fila in df.iterrows():
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
                
                print(f"\nAnalizando a {username}:")
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
                    
                    estado = "✅ POS" if id_sentimiento_aspecto == 1 else "❌ NEG"
                    print(f"  -> {aspecto}: {estado} ({confianza})")
                    
            print("\nProcesamiento completado. Revisa tus tablas en Supabase.")

        except Exception as e:
            print(f"❌ Ocurrió un error inesperado: {e}")