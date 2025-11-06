# --- EJERCICIO 4: SIMILITUD DE TEXTO Y MAPAS DE CALOR ---

# --- CONTEXTO ---
# Objetivo: Aprender a cuantificar la similitud entre diferentes textos. Esto es fundamental para tareas
# como la detección de plagio, agrupación de documentos o sistemas de recomendación.
# Usaremos una métrica simple y muy intuitiva, la "Similitud de Jaccard", y visualizaremos
# nuestros resultados con un mapa de calor (heatmap) para una interpretación rápida.
#
# ¿Qué es la Similitud de Jaccard? Mide la similitud entre dos conjuntos (sets). Se define como
# el tamaño de la intersección dividido por el tamaño de la unión de los dos conjuntos.
# Jaccard = |A ∩ B| / |A ∪ B|. Un valor de 1 significa que los textos son idénticos (en términos de palabras únicas),
# y un valor de 0 significa que no tienen ninguna palabra en común.

# --- IMPORTACIONES ---
import re
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

# --- CORPUS Y STOPWORDS ---
corpus = [
    "Me encanta este producto, es fantástico y muy útil.",
    "El servicio al cliente fue terrible, muy decepcionante.",
    "El precio es adecuado, ni caro ni barato.",
    "No volvería a comprar, la calidad es pésima.",
    "Una experiencia increíble, lo recomiendo totalmente.",
    "El envío tardó más de lo esperado.",
    "Fantástico, simplemente fantástico.",
    "No está mal, pero podría mejorar.",
    "La batería dura poquísimo, un desastre."
]

stopwords_es = set([
    'de', 'la', 'que', 'el', 'en', 'y', 'a', 'los', 'del', 'las', 'un', 'por', 'con', 'no', 'una', 'su', 'para', 'es', 'al', 'lo', 'como', 'más', 'pero', 'sus', 'le', 'ha', 'me', 'sin', 'sobre', 'este', 'ya', 'entre', 'cuando', 'todo', 'esta', 'ser', 'son', 'dos', 'también', 'fue', 'había', 'era', 'muy', 'hasta', 'desde', 'mucho', 'hacia', 'mi', 'se', 'ni', 'ese', 'yo', 'qué', 'e', 'o', 'u', 'algunos', 'aspectos'
])

# --- PROCESAMIENTO ---

# 1. Preprocesamiento: Convertir cada frase en un conjunto de palabras limpias
def preprocess_to_set(frase, stopwords):
    """Limpia una frase y la convierte en un conjunto de palabras únicas."""
    frase_lower = frase.lower()
    words = re.findall(r'\b\w+\b', frase_lower)
    words_cleaned = [word for word in words if word not in stopwords]
    return set(words_cleaned)

print("Paso 1: Preprocesando cada frase del corpus en un conjunto de palabras...")
sets_de_palabras = [preprocess_to_set(frase, stopwords_es) for frase in corpus]
print("Ejemplo, conjunto para la primera frase:", sets_de_palabras[0])

# 2. Cálculo de la Similitud de Jaccard
def jaccard_similarity(set1, set2):
    """Calcula la similitud de Jaccard entre dos conjuntos."""
    interseccion = set1.intersection(set2)
    union = set1.union(set2)
    
    # Evitamos la división por cero si ambos conjuntos están vacíos
    if not union:
        return 1.0
    else:
        return len(interseccion) / len(union)

# 3. Creación de la Matriz de Similitud
# Esta matriz cuadrada nos dirá la similitud de cada frase con cada otra frase.
num_frases = len(corpus)
matriz_similitud = np.zeros((num_frases, num_frases))

print("\nPaso 2: Calculando la matriz de similitud... (Jaccard)")
for i in range(num_frases):
    for j in range(num_frases):
        similitud = jaccard_similarity(sets_de_palabras[i], sets_de_palabras[j])
        matriz_similitud[i, j] = similitud

print("Matriz de similitud calculada (primeras 5x5 filas/columnas):")
print(np.round(matriz_similitud[:5, :5], 2))

# --- VISUALIZACIÓN ---

print("\nGenerando mapa de calor (heatmap) de la similitud...")

plt.figure(figsize=(12, 10))

# Usamos seaborn para crear el heatmap. Es una librería de visualización construida sobre matplotlib.
# `annot=True` muestra los valores de similitud en cada celda.
# `cmap='coolwarm'` es una paleta de colores que va de azul (baja similitud) a rojo (alta similitud).
sns.heatmap(matriz_similitud, 
            annot=True, 
            cmap='coolwarm', 
            fmt=".2f", # Formato de los números a 2 decimales
            xticklabels=[f'Frase {i+1}' for i in range(num_frases)],
            yticklabels=[f'Frase {i+1}' for i in range(num_frases)])

plt.title('Mapa de Calor de Similitud de Jaccard entre Frases', fontsize=16)
plt.xticks(rotation=45, ha='right')
plt.yticks(rotation=0)
plt.tight_layout()
plt.show()

print("\n--- FIN DEL EJERCICIO 4 ---")
print("Observación: El mapa de calor nos permite identificar rápidamente los 'puntos calientes'.")
print("La diagonal principal es siempre 1.0 (rojo intenso), ya que cada frase es idéntica a sí misma.")
print("Busca otros cuadrados rojos o naranjas para encontrar las frases más parecidas en su vocabulario.")
