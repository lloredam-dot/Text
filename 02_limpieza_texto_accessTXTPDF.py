# --- EJERCICIO 2: LIMPIEZA DE RUIDO Y EL IMPACTO VISUAL ---

# --- CONTEXTO ---
# Objetivo: Aprender a limpiar texto eliminando "stopwords" (palabras comunes sin significado semántico)
# y visualizar de forma impactante cómo esta limpieza cambia el análisis de frecuencia, haciendo que
# las palabras verdaderamente importantes emerjan.

# --- IMPORTACIONES ---
import re
from collections import Counter
import matplotlib.pyplot as plt


# --- STOPWORDS DE BASES DE DATOS PROFESIONALES ---
def cargar_stopwords_profesionales():
    """Carga stopwords combinando múltiples bases de datos profesionales"""
    stopwords_set = set()

    # 1. NLTK (179 palabras)
    try:
        import nltk
        from nltk.corpus import stopwords
        stopwords_set.update(stopwords.words('english'))
        print("✓ NLTK: 179 stopwords cargadas")
    except ImportError:
        print("✗ NLTK no disponible. Instálalo con: pip install nltk")
    except LookupError:
        print("⚠️  Datos de NLTK ('stopwords') no encontrados. Intentando descargar...")
        try:
            nltk.download('stopwords')
            from nltk.corpus import stopwords
            stopwords_set.update(stopwords.words('english'))
            print("✓ NLTK: stopwords descargadas y cargadas")
        except Exception as e:
            print(f"✗ Falló la descarga de datos de NLTK: {e}")

    # 2. spaCy (326 palabras)
    try:
        import spacy
        nlp = spacy.load('en_core_web_sm')
        stopwords_set.update(nlp.Defaults.stop_words)
        print(f"✓ spaCy: {len(nlp.Defaults.stop_words)} stopwords cargadas")
    except ImportError:
        print("✗ spaCy no disponible. Instálalo con: pip install spacy")
    except OSError:
        print("✗ Modelo spaCy 'en_core_web_sm' no encontrado. Descárgalo con: python -m spacy download en_core_web_sm")

    # 3. Scikit-learn (318 palabras)
    try:
        from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
        stopwords_set.update(ENGLISH_STOP_WORDS)
        print(f"✓ Scikit-learn: {len(ENGLISH_STOP_WORDS)} stopwords cargadas")
    except ImportError:
        print("✗ Scikit-learn no disponible. Instálalo con: pip install scikit-learn")

    print(f"🎯 Total stopwords únicas: {len(stopwords_set)}")
    return stopwords_set


# Cargar stopwords profesionales
stopwords_en = cargar_stopwords_profesionales()

# Si no se cargó ninguna, usar lista básica
if not stopwords_en:
    print("⚠️  Usando lista básica de stopwords")
    stopwords_en = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}


# --- CORPUS ---
# Funciones para leer diferentes tipos de archivos
def leer_corpus_desde_archivo(nombre_archivo):
    """Lee el corpus desde un archivo de texto o PDF."""
    try:
        if nombre_archivo.lower().endswith('.txt'):
            return leer_txt(nombre_archivo)
        elif nombre_archivo.lower().endswith('.pdf'):
            return leer_pdf(nombre_archivo)
        else:
            print(f"Error: Formato no soportado. Use .txt o .pdf")
            return []
    except Exception as e:
        print(f"Error al leer el archivo: {e}")
        return []


def leer_txt(nombre_archivo):
    """Lee un archivo de texto donde cada línea es una frase."""
    with open(nombre_archivo, 'r', encoding='utf-8') as archivo:
        lineas = [linea.strip() for linea in archivo if linea.strip()]
    return lineas


def leer_pdf(nombre_archivo):
    """Lee un archivo PDF y extrae el texto dividido en frases."""
    try:
        import PyPDF2
        frases = []
        with open(nombre_archivo, 'rb') as archivo:
            lector_pdf = PyPDF2.PdfReader(archivo)
            for pagina in lector_pdf.pages:
                texto = pagina.extract_text()
                if texto:
                    # Dividir el texto en frases usando puntos como delimitadores
                    frases_pagina = [frase.strip() for frase in texto.split('.') if frase.strip()]
                    frases.extend(frases_pagina)
        return frases
    except ImportError:
        print("Error: PyPDF2 no está instalado. Instálalo con: pip install PyPDF2")
        return []
    except Exception as e:
        print(f"Error al leer PDF: {e}")
        return []


# Cargar el corpus desde el archivo
corpus = leer_corpus_desde_archivo('1984.pdf')  # Cambia a 'example.txt' o 'example.pdf'

# Si el archivo está vacío o no existe, usar un corpus de ejemplo
if not corpus:
    print("Usando corpus de ejemplo...")
    corpus = [
        "The first Monday of the month of April 1625, the town of Meung,",
        "where the author of the Roman de la Rose was born, appeared to be in",
        "as complete a revolution as if the Huguenots had come to",
        "make a second Rochelle."
    ]


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
print("\nPaso 1: Analizando frecuencias SIN limpiar el texto...")
all_text = ' '.join(corpus)
word_counts_sin_limpieza = procesar_y_contar(all_text)
top_10_sin_limpieza = word_counts_sin_limpieza.most_common(10)
print("Top 10 palabras (sin limpieza):", top_10_sin_limpieza)

# 2. Análisis CON limpieza
print("\nPaso 2: Analizando frecuencias CON limpieza de stopwords...")
word_counts_con_limpieza = procesar_y_contar(all_text, stopwords=stopwords_en)
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
plt.tight_layout(rect=[0, 0, 1, 0.96])  # Ajuste para el supertítulo
plt.show()

print("\n--- FIN DEL EJERCICIO 2 ---")
print(
    "Observación: ¡El cambio es drástico! El gráfico de la derecha revela las palabras que realmente aportan significado:")
print("Ahora podemos ver los términos clave del texto analizado.")