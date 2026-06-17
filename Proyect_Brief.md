## 🎯 El Concepto Central

El proyecto es un **Pipeline de Ingeniería de Datos automatizado**, potenciado por **Inteligencia Artificial**.  
Su objetivo principal es transformar datos desestructurados (comentarios en texto libre de clientes) en **métricas de negocio precisas**, utilizando la técnica de **Análisis de Sentimiento Basado en Aspectos (ABSA)**.

---

## ⚙️ ¿Cómo funciona? (Flujo en 3 Pasos)

### 1. Ingesta de Datos (Extracción)
El motor backend lee automáticamente un lote masivo de reseñas crudas desde un archivo transaccional (CSV).  
Por cada registro, el sistema identifica al usuario y al restaurante, validando o creando su identidad en la base de datos para garantizar la **integridad relacional**.

---

### 2. El Cerebro IA (Transformación e Inferencia)
Aquí ocurre la magia —con bata de laboratorio y todo—.  
En lugar de clasificar una reseña completa de forma genérica (“buena” o “mala”), el texto es procesado por un **modelo neuronal Zero-Shot multilingüe**.

La IA analiza el comentario y lo fragmenta para responder de forma independiente a tres preguntas clave:

- ¿El cliente tuvo una experiencia positiva o negativa con la **Calidad de la Comida**?
- ¿Cómo percibió la **Atención del Personal**?
- ¿Qué opinó sobre el **Ambiente del Local**?

---

### 3. Carga Transaccional (Almacenamiento)
La IA no solo emite un veredicto (**Positivo, Negativo o Neutro**) para cada dimensión, sino que también adjunta una **probabilidad matemática de confianza**.

Toda esta información, ahora completamente estructurada, se almacena de forma segura en las **tablas relacionales de la base de datos en la nube (Supabase)**.

---

## 🏆 El Valor de Negocio (El verdadero “por qué”)

El gran logro de esta arquitectura es convertir **opiniones subjetivas** en **datos cuantificables**.

Al finalizar la ejecución del script, el restaurante deja de tener una simple *“caja de sugerencias”* y pasa a contar con un **modelo de datos robusto**, listo para **Inteligencia de Negocios**.

Esto permite —como se demuestra en la **Versión 2 con interfaz web**— identificar matemáticamente las fortalezas del negocio y detectar áreas críticas de mejora con **precisión quirúrgica**, sin que ningún humano tenga que leer miles de reseñas una por una.  
La IA trabaja; el equipo analiza. Todos felices.