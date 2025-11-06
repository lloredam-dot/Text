# --- EJERCICIO 2: LIMPIEZA DE RUIDO Y EL IMPACTO VISUAL ---

# --- CONTEXTO ---
# Objetivo: Aprender a limpiar texto eliminando "stopwords" (palabras comunes sin significado semántico)
# y visualizar de forma impactante cómo esta limpieza cambia el análisis de frecuencia, haciendo que
# las palabras verdaderamente importantes emerjan.
#
# ¿Qué son las Stopwords? Son palabras como 'el', 'y', 'o', 'de', que son extremadamente frecuentes
# pero no nos dicen nada sobre el tema o el sentimiento de un texto. Son el "ruido" del lenguaje.

# --- IMPORTACIONES ---
import re
from collections import Counter
import matplotlib.pyplot as plt

# --- CORPUS Y STOPWORDS ---
corpus = [
    "El primer lunes del mes de abril de 1625, la burguesía de Meung,",
    "donde nació el autor del Roman de la Rose, parecía estar en",
    "tan completa revolución como si los hugonotes hubieran venido a",
    "hacer una segunda Rochela.",
    "Muchos burgueses, viendo huir a las mujeres por la calle Mayor,",
    "oyendo a los niños gritar en el umbral de las puertas,",
    "se apresuraban a ponerse la coraza y, armados con un arcabuz",
    "o con una alabarda, se dirigían hacia el hostal del Francón,",
    "delante del cual se agolpaba un grupo compacto,",
    "cada vez más numeroso y ruidoso.",
    "En aquellos tiempos los motines eran frecuentes,",
    "y pocos días transcurrían sin que alguna ciudad",
    "registrase en sus anales uno de esos acontecimientos.",
    "Los señores guerreaban entre sí; el rey guerreaba con el cardenal;",
    "los españoles guerreaban con el rey.",
    "Luego, aparte de estas guerras sordas o públicas, secretas o patentes,",
    "estaban los ladrones, los mendigos, los hugonotes, los lobos",
    "y los lacayos, que guerreaban con todo el mundo.",
    "Los burgueses se armaban siempre contra los ladrones,",
    "contra los lobos, contra los lacayos, muchas veces contra los señores"
]

# Lista de stopwords comunes en español. En proyectos reales, se usan listas más exhaustivas de librerías como NLTK o spaCy.
stopwords_es = set([
    'de', 'la', 'que', 'el', 'en', 'y', 'a', 'los', 'del', 'las', 'un', 'por', 'con', 'no', 'una', 'su', 'para', 'es', 'al', 'lo', 'como', 'más', 'pero', 'sus', 'le', 'ha', 'me', 'sin', 'sobre', 'este', 'ya', 'entre', 'cuando', 'todo', 'esta', 'ser', 'son', 'dos', 'también', 'fue', 'había', 'era', 'muy', 'hasta', 'desde', 'mucho', 'hacia', 'mi', 'se', 'ni', 'ese', 'yo', 'qué', 'e', 'o', 'u', 'algunos', 'aspectos'
])

# --- PROCESAMIENTO ---

# Función para procesar y limpiar texto
def procesar_y_contar(text, stopwords=None):
    """Toma un bloque de texto, lo normaliza, tokeniza y opcionalmente elimina stopwords."""
    text_lower = text.lower()
    words = re.findall(r'\b\w+\b', text_lower)
    if stopwords:
        words = [word for word in words if word not in stopwords]
    return Counter(words)

# 1. Análisis SIN limpieza (Repetimos el paso del ejercicio 1 para comparar)
print("Paso 1: Analizando frecuencias SIN limpiar el texto...")
all_text = ' '.join(corpus)
word_counts_sin_limpieza = procesar_y_contar(all_text)
top_10_sin_limpieza = word_counts_sin_limpieza.most_common(10)
print("Top 10 palabras (sin limpieza):", top_10_sin_limpieza)

# 2. Análisis CON limpieza
print("\nPaso 2: Analizando frecuencias CON limpieza de stopwords...")
word_counts_con_limpieza = procesar_y_contar(all_text, stopwords=stopwords_es)
top_10_con_limpieza = word_counts_con_limpieza.most_common(10)
print("Top 10 palabras (con limpieza):", top_10_con_limpieza)


# --- VISUALIZACIÓN COMPARATIVA ---

print("\nGenerando gráficos comparativos...")

# Desempaquetamos los resultados para ambos gráficos
words_sin, counts_sin = zip(*top_10_sin_limpieza)
words_con, counts_con = zip(*top_10_con_limpieza)

# Creamos una figura con dos subplots (uno al lado del otro)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))

# Gráfico 1: Sin Limpieza
ax1.bar(words_sin, counts_sin, color='#ff9999')
ax1.set_title('Frecuencias ANTES de la Limpieza', fontsize=16)
ax1.set_xlabel('Palabras')
ax1.set_ylabel('Frecuencia')
ax1.tick_params(axis='x', rotation=45)

# Gráfico 2: Con Limpieza
ax2.bar(words_con, counts_con, color='#99ff99')
ax2.set_title('Frecuencias DESPUÉS de la Limpieza', fontsize=16)
ax2.set_xlabel('Palabras')
ax2.set_ylabel('Frecuencia')
ax2.tick_params(axis='x', rotation=45)

# Título general para toda la figura
fig.suptitle('Impacto de la Eliminación de Stopwords', fontsize=20)

# Ajustamos el layout y mostramos
plt.tight_layout(rect=[0, 0, 1, 0.96]) # Ajuste para el supertítulo
plt.show()

print("\n--- FIN DEL EJERCICIO 2 ---")
print("Observación: ¡El cambio es drástico! El gráfico de la derecha revela las palabras que realmente aportan significado:")
print("Ahora podemos ver los términos clave de la narrativa histórica de Los Tres Mosqueteros.")