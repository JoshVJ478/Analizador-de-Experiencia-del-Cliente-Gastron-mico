# 📖 Documentación Técnica: Pipeline ETL e Inferencia Zero-Shot

Este documento detalla el **diseño arquitectónico**, las **clases**, los **métodos** y la **estrategia de Inteligencia Artificial** que conforman el motor de **Análisis de Sentimiento Basado en Aspectos (ABSA)**.  
En pocas palabras: el *cómo*, el *por qué* y el *con qué* funciona el sistema (sin magia negra, solo buena ingeniería).

---

## 1. Arquitectura Orientada a Objetos (OOP)

El sistema está construido bajo un **paradigma modular**, separando claramente las responsabilidades de **conexión a la base de datos** y la **lógica de procesamiento analítico**.  
Cada clase tiene su misión bien definida; aquí no hay multitasking innecesario.

---

### 🔹 Clase Base: `ProcesadorDatosBase`

Actúa como la **capa de acceso a datos (Data Access Layer)**.  
Su responsabilidad exclusiva es gestionar la conexión con **Supabase** y garantizar la **integridad relacional** de las entidades estáticas.

#### Métodos principales

- **`_conectar_bd(url, key)`**  
  Inicializa el cliente oficial de Supabase.  
  Incluye manejo de excepciones nativo para detener la ejecución si las credenciales fallan, evitando caídas silenciosas (el error se grita, no se susurra).

- **`_obtener_o_crear_cliente(username)`**  
  Implementa un patrón lógico de tipo **Upsert**:
  - Consulta si el usuario ya existe en la base de datos y recupera su `id_cliente` (Foreign Key).
  - Si no existe, lo inserta en tiempo real y devuelve el ID generado.  

  Esto asegura la **integridad referencial** para todas las tablas posteriores del pipeline.

---

### 🔹 Clase Principal: `AnalizadorAspectos`

Hereda de `ProcesadorDatosBase`.  
Funciona como el **orquestador del pipeline** (*Pipeline Orchestrator*), encargado de:

- Cargar el modelo de IA en memoria  
- Leer los datos transaccionales  
- Ejecutar la inferencia  
- Persistir los resultados en la base de datos  

En resumen: manda, coordina y no se olvida de guardar nada.

#### Métodos principales

- **`_cargar_modelo_ia()`**  
  Instancia el pipeline de **Hugging Face** y descarga los pesos del modelo en memoria local, permitiendo su uso continuo en modo offline.

- **`procesar_lote_csv(ruta_csv)`**  
  Núcleo del flujo **ETL (Extracción, Transformación y Carga)**:
  - Itera sobre el `DataFrame` de **Pandas**.
  - Inserta la reseña general como entidad primaria.
  - Ejecuta el análisis iterativo por cada aspecto configurado.
  - Persiste los resultados estructurados en la base de datos.

---

## 2. El Cerebro de IA: ¿Por qué mDeBERTa-v3?

Dentro del amplio catálogo de Hugging Face, se seleccionó el modelo:

**`MoritzLaurer/mDeBERTa-v3-base-mnli-xnli`**

Implementando la estrategia de **Zero-Shot Classification**.

Esta elección no fue casual ni estética: fue la mejor decisión técnica por **tres razones fundamentales**.

---

### 🧠 1. Formulación NLI (Natural Language Inference)

Los modelos tradicionales de sentimiento clasifican un texto completo como *Positivo* o *Negativo*.  
Este modelo, entrenado en tareas **MNLI/XNLI**, trabaja con **premisas e hipótesis lógicas**.

Ejemplo de hipótesis dinámica:

> *“El sentimiento sobre la Calidad de la Comida es positivo”*

El modelo calcula la probabilidad de que la reseña confirme dicha hipótesis específica, permitiendo un **análisis por aspecto**, no solo global.

---

### 🌍 2. Soporte Multilingüe (mDeBERTa)

El modelo está **preentrenado en más de 100 idiomas**, lo que garantiza:

- Interpretación correcta de **jerga, modismos y gramática en español**
- Rendimiento comparable (o superior) a modelos entrenados solo en inglés  

En la práctica, supera ampliamente a alternativas más simples como `roberta-base`.

---

### 🧩 3. Flexibilidad Zero-Shot

No fue necesario construir un dataset masivo de reseñas de restaurantes peruanos etiquetadas manualmente ni realizar **fine-tuning**.

El modelo puede inferir clases que **nunca ha visto** (por ejemplo: *Ambiente*, *Atención*, *Servicio*) basándose únicamente en su **comprensión semántica global**.

Menos datos etiquetados, más inteligencia contextual.  
Un lujo… pero bien justificado.

---

## 3. Flujo de Ejecución (Paso a Paso)

Cuando se ejecuta el script principal (`main.py`), el motor realiza la siguiente secuencia de eventos:

### 1. Ingesta de Datos (Extract)
- **Pandas** carga el archivo `dataset_resenas.csv`, estructurando los registros en memoria para una iteración eficiente.

### 2. Validación de Identidad
- Por cada fila, el sistema extrae el `username` e invoca el método `_obtener_o_crear_cliente` para asegurar que la **Foreign Key** del cliente exista en la base de datos relacional.

### 3. Inserción Primaria (Load Parcial)
- Se inserta la reseña original y cruda en la tabla `resena` con un estado **Neutro** por defecto.
- **Supabase** devuelve el `id_resena` generado, el cual es vital para el desglose posterior (sin él, no hay magia).

### 4. Inferencia Multidimensional (Transform / Inferencia)
- El motor inicia un bucle sobre las tres dimensiones estáticas:
  - **Calidad de Comida**
  - **Atención del Personal**
  - **Ambiente del Local**

- Para cada dimensión, se envían dos hipótesis al modelo *Zero-Shot*:
  - `"el sentimiento sobre [aspecto] es positivo"`
  - `"el sentimiento sobre [aspecto] es negativo"`

- La IA devuelve las probabilidades lógicas y el motor selecciona la etiqueta con mayor *score* (confianza).

### 5. Carga Analítica Detallada (Load Final)
- Los resultados fraccionados se empaquetan en un diccionario y se insertan en la tabla intermedia `resena_aspecto`, vinculando:
  - `id_resena`
  - `id_aspecto`
  - Identificador del sentimiento (`1`, `2` o `3`)
  - Porcentaje de precisión matemática calculado por la IA

### 6. Feedback en Consola
- El sistema imprime un log en tiempo real en la terminal, demostrando la trazabilidad completa de la ejecución hasta procesar el lote completo (transparencia total, como debe ser).