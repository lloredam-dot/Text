# --- EJERCICIO 1: LA ANATOMÍA DEL TEXTO Y VISUALIZACIÓN DE FRECUENCIAS ---

# --- CONTEXTO ---
# Objetivo: Aprender el primer paso fundamental en cualquier tarea de NLP: convertir texto no estructurado
# en datos cuantitativos (frecuencias) y visualizar estos datos para obtener una primera impresión del contenido.
#
# Nuestra "Base de Datos":
# Por ahora, es un "corpus controlado": una simple lista de frases en Python.
# Esto nos permite experimentar en un laboratorio aislado, sin preocuparnos por la complejidad de
# leer archivos, conectarnos a APIs o limpiar datos del mundo real. Nos centramos 100% en la técnica.

# --- IMPORTACIONES --- 
# Importamos las herramientas que necesitaremos.

import re
from collections import Counter
import matplotlib.pyplot as plt

# --- NUESTRO CORPUS (BASE DE DATOS DE TEXTO) ---
corpus = [
    "Me encanta este producto, es fantástico y muy útil.",
    "El servicio al cliente fue terrible, muy decepcionante.",
    "El precio es adecuado, ni caro ni barato.",
    "No volvería a comprar, la calidad es pésima.",
    "Una experiencia increíble, lo recomiendo totalmente.",
    "El envío tardó más de lo esperado.",
    "Fantástico, simplemente fantástico.",
    "No está mal, pero podría mejorar en algunos aspectos.",
    "La batería dura poquísimo, un desastre."
]

# --- PROCESAMIENTO ---


# 1. Unificar todo el texto
# Para analizar la frecuencia en todo el corpus, primero unimos todas las frases en un único bloque de texto.
print("Paso 1: Unificando el corpus en un solo bloque de texto...")
all_text = ' '.join(corpus)
print(f"Texto completo: '{all_text[:100]}...'")

# 2. Normalización: Convertir a minúsculas
# Esto es crucial para que palabras como "Fantástico" y "fantástico" se cuenten como una sola.
print("\nPaso 2: Normalizando el texto a minúsculas...")
all_text_lower = all_text.lower()
print(f"Texto normalizado: '{all_text_lower[:100]}...'")

# 3. Tokenización: Dividir el texto en palabras (tokens)
# Usamos una expresión regular `\b\w+\b` que es más robusta que un simple `.split()`.
# `\b` asegura que solo cojamos palabras completas, ignorando signos de puntuación como comas o puntos.
print("\nPaso 3: Tokenizando el texto en palabras...")
words = re.findall(r'\b\w+\b', all_text_lower)
print(f"Primeras 20 palabras (tokens): {words[:20]}")

# 4. Conteo de Frecuencias
# `collections.Counter` es una herramienta de Python extremadamente eficiente para contar la frecuencia de elementos en una lista.
print("\nPaso 4: Contando la frecuencia de cada palabra...")
word_counts = Counter(words)

# `most_common(10)` nos da una lista de las 10 tuplas (palabra, frecuencia) más comunes.
top_10_words = word_counts.most_common(10)

print("\n--- RESULTADOS DEL ANÁLISIS DE FRECUENCIA ---")
print("Top 10 palabras más frecuentes (antes de la limpieza):")
for word, count in top_10_words:
    print(f"- '{word}': {count} veces")

# --- VISUALIZACIÓN ---
# Un análisis no está completo si no podemos comunicarlo visualmente.

print("\nGenerando gráfico de barras... (una ventana nueva debería aparecer)")

# Desempaquetamos las palabras y sus conteos en dos listas separadas para el gráfico.
words_for_plot, counts_for_plot = zip(*top_10_words)

# Creamos la figura y los ejes para el gráfico.
plt.figure(figsize=(12, 7))
plt.bar(words_for_plot, counts_for_plot, color='skyblue')

# Añadimos títulos y etiquetas para que el gráfico sea legible.
plt.title('Top 10 Palabras Más Frecuentes en el Corpus (Sin Limpieza)')
plt.xlabel('Palabras')
plt.ylabel('Frecuencia')
plt.xticks(rotation=45, ha="right") # Rotamos las etiquetas para que no se solapen
plt.tight_layout() # Ajusta el gráfico para que todo quepa bien

# Mostramos el gráfico. Esto abrirá una nueva ventana.
plt.show()

print("\n--- FIN DEL EJERCICIO 1 ---")
print("Observación: Nota cómo palabras como 'es', 'el', 'y', 'muy' dominan el gráfico.")
print("Estas son 'stopwords' y no aportan mucho significado. ¡Esto es lo que solucionaremos en el siguiente ejercicio!")
