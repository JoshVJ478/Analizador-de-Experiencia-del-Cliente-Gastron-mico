# 📊 Analizador de Experiencia del Cliente Gastronómico (ABSA)

Este proyecto es un pipeline de Inteligencia de Negocios (BI) y Data Engineering diseñado para procesar, analizar y visualizar reseñas de clientes de restaurantes. Utiliza un modelo de Inteligencia Artificial **Zero-Shot** para realizar un Análisis de Sentimiento Basado en Aspectos (ABSA), desglosando una sola reseña en múltiples calificaciones (Comida, Personal y Ambiente) de manera completamente anónima y eficiente.

## 🚀 Arquitectura y Tecnologías
* **Lenguaje:** Python 3.10+
* **Procesamiento de Datos (ETL):** Pandas
* **Base de Datos:** Supabase (PostgreSQL en la nube con eliminación en cascada)
* **Inteligencia Artificial:** Hugging Face `transformers` (Modelo Zero-Shot Multilingüe)
* **Visualización:** Streamlit & Plotly

---

## 🛠️ Instrucciones de Despliegue para el Equipo

Sigue estos pasos para clonar y ejecutar el proyecto en tu entorno local sin conflictos.

### 1. Clonar el repositorio
Abre tu terminal y ejecuta:
```bash
git clone [https://github.com/JoshVJ478/Analizador-de-Experiencia-del-Cliente-Gastron-mico.git](https://github.com/JoshVJ478/Analizador-de-Experiencia-del-Cliente-Gastron-mico.git)
cd Analizador-de-Experiencia-del-Cliente-Gastron-mico
```

### 2. Crear y activar el Entorno Virtual
Es indispensable aislar las dependencias para evitar conflictos. Asegúrate de estar en la raíz del repositorio y ejecuta:

**En Windows (PowerShell / CMD):**
```bash
python -m venv .venv
.venv\Scripts\activate
```
**En macOS/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```
*(Sabrás que funcionó cuando veas el indicador `(.venv)` en color verde al inicio de tu línea de comandos en la terminal).*

### 3. Instalar las dependencias
Una vez activado el entorno virtual, navega a la subcarpeta de la aplicación e instala las librerías necesarias:

Usando el instalador clásico `pip`:
```bash
cd LCD_APP
pip install -r requirements.txt
```
*(⚡ **Tip de rendimiento:** Si tu equipo cuenta con el gestor de paquetes `uv`, pueden instalar las dependencias muchísimo más rápido ejecutando `uv pip install -r requirements.txt`).*

### 4. Configurar las Variables de Entorno
Por seguridad, las credenciales de la base de datos están protegidas por el `.gitignore` y no se suben a GitHub. 
1. Asegúrate de estar dentro de la carpeta `LCD_APP`.
2. Crea un archivo nuevo y nómbralo exactamente `.env`.
3. Pega las credenciales del proyecto de Supabase en el archivo con el siguiente formato estricto:

```env
SUPABASE_URL="tu_url_de_supabase_aqui"
SUPABASE_KEY="tu_anon_key_de_supabase_aqui"
```

---

## ⚙️ Ejecución del Sistema

El proyecto consta de dos procesos principales que se ejecutan de manera independiente. **Recuerda ejecutarlos siempre teniendo la terminal dentro de la carpeta `LCD_APP`** y con el entorno virtual `(.venv)` activo.

### Paso A: Procesamiento ETL y Motor de IA (Backend)
Si necesitas procesar nuevas reseñas desde el archivo `dataset_resenas.csv` para que la IA realice la inferencia Zero-Shot y las inyecte limpias en la base de datos relacional de Supabase, ejecuta:
```bash
python main.py
```
*Espera a que la consola confirme que el procesamiento y la inserción transaccional se han completado exitosamente.*

### Paso B: Levantar el Dashboard Gerencial (Frontend)
Para visualizar las métricas interactivas de satisfacción, el análisis automático de fortalezas/debilidades del negocio y la matriz de sentimiento detallada, inicia el servidor web local:
```bash
streamlit run dashboard.py
```
*Streamlit abrirá automáticamente una pestaña en tu navegador web predeterminado (usualmente en la dirección `http://localhost:8501`) mostrando el panel de inteligencia de negocio en tiempo real.*

---
**Desarrollado con estándares de arquitectura limpia para el análisis avanzado de datos gastronómicos.**
