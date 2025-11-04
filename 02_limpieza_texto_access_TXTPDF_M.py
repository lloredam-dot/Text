# --- EJERCICIO 2: LIMPIEZA DE RUIDO Y EL IMPACTO VISUAL ---

# --- CONTEXTO ---
# Objetivo: Aprender a limpiar texto eliminando "stopwords" (palabras comunes sin significado semántico)
# y visualizar de forma impactante cómo esta limpieza cambia el análisis de frecuencia, haciendo que
# las palabras verdaderamente importantes emerjan.

# --- IMPORTACIONES ---
import re
from collections import Counter
import matplotlib.pyplot as plt
import subprocess
import sys


# --- INSTALACIÓN AUTOMÁTICA (opcional) ---
def instalar_dependencias():
    """Instala las dependencias automáticamente si no están disponibles"""
    paquetes = ['nltk', 'spacy', 'sklearn', 'PyPDF2']

    for paquete in paquetes:
        try:
            if paquete == 'sklearn':
                __import__('sklearn')
            else:
                __import__(paquete)
        except ImportError:
            print(f"Instalando {paquete}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", paquete])


# Ejecutar instalación automática (descomenta la línea siguiente si quieres auto-instalación)
# instalar_dependencias()

# --- STOPWORDS DE BASES DE DATOS PROFESIONALES ---
def cargar_stopwords_profesionales():
    """Carga stopwords combinando múltiples bases de datos profesionales"""
    stopwords_set = set()

    # 1. NLTK (179 palabras)
    try:
        from nltk.corpus import stopwords
        # Descargar stopwords si no están disponibles
        try:
            stopwords.words('english')
        except LookupError:
            print("Descargando stopwords de NLTK...")
            import nltk
            nltk.download('stopwords', quiet=True)

        stopwords_set.update(stopwords.words('english'))
        print("✓ NLTK: 179 stopwords cargadas")
    except ImportError:
        print("✗ NLTK no disponible")

    # 2. spaCy (326 palabras)
    try:
        import spacy
        try:
            nlp = spacy.load('en_core_web_sm')
        except OSError:
            print("Modelo spaCy no encontrado. Usando solo NLTK y Scikit-learn...")
            nlp = None

        if nlp:
            stopwords_set.update(nlp.Defaults.stop_words)
            print("✓ spaCy: 326 stopwords cargadas")
    except ImportError:
        print("✗ spaCy no disponible")

    # 3. Scikit-learn (318 palabras)
    try:
        from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
        stopwords_set.update(ENGLISH_STOP_WORDS)
        print("✓ Scikit-learn: 318 stopwords cargadas")
    except ImportError:
        print("✗ Scikit-learn no disponible")

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

# --- OBTENER PARÁMETROS DEL USUARIO ---
print("\n" + "=" * 60)
print(" PASO 1: CONFIGURAR ANÁLISIS")
print("=" * 60)

# 1. Obtener nombre del archivo
nombre_archivo = input("Por favor, introduce el nombre del archivo (.txt o .pdf): ").strip()

# 2. Obtener número de top words
while True:
    try:
        top_n_str = input("¿Cuántas palabras del top quieres ver? (ej: 10, 15, 20): ").strip()
        top_n = int(top_n_str)
        if top_n > 0:
            break
        else:
            print("Por favor, introduce un número positivo.")
    except ValueError:
        print("Entrada no válida. Por favor, introduce un número entero.")


# Cargar el corpus desde el archivo
print(f"\nCargando corpus desde '{nombre_archivo}'...")
corpus = leer_corpus_desde_archivo(nombre_archivo)

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


# 1. Análisis SIN limpieza
print(f"\nPaso 2: Analizando frecuencias SIN limpiar el texto...")
all_text = ' '.join(corpus)
word_counts_sin_limpieza = procesar_y_contar(all_text)
top_words_sin_limpieza = word_counts_sin_limpieza.most_common(top_n)
print(f"Top {top_n} palabras (sin limpieza):", top_words_sin_limpieza)

# 2. Análisis CON limpieza
print(f"\nPaso 3: Analizando frecuencias CON limpieza de stopwords...")
word_counts_con_limpieza = procesar_y_contar(all_text, stopwords=stopwords_en)
top_words_con_limpieza = word_counts_con_limpieza.most_common(top_n)
print(f"Top {top_n} palabras (con limpieza):", top_words_con_limpieza)

# --- VISUALIZACIÓN COMPARATIVA ---

print("\nGenerando gráficos comparativos...")

# Desempaquetamos los resultados para ambos gráficos
words_sin, counts_sin = zip(*top_words_sin_limpieza)
words_con, counts_con = zip(*top_words_con_limpieza)

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

print("\n--- FIN DEL ANÁLISIS INICIAL ---")
print(
    "Observación: ¡El cambio es drástico! El gráfico de la derecha revela las palabras que realmente aportan significado:")
print("Ahora podemos ver los términos clave del texto analizado.")


# --- FUNCIONALIDAD MEJORADA: AGREGAR STOPWORDS MANUALMENTE ---
def agregar_stopwords_interactivo(stopwords_actuales, top_palabras_con_limpieza):
    """Permite al usuario agregar stopwords manualmente basado en los resultados"""
    print("\n" + "=" * 60)
    print("🎯 PASO 4: REFINAR STOPWORDS MANUALMENTE")
    print("=" * 60)

    # Mostrar las palabras que aparecieron después de la limpieza
    print(f"\nPalabras que aparecieron después de la limpieza:")
    for i, (palabra, frecuencia) in enumerate(top_palabras_con_limpieza, 1):
        print(f"  {i:2d}. '{palabra}': {frecuencia} apariciones")

    # Preguntar si quiere agregar más stopwords
    while True:
        print(f"\n¿Quieres agregar alguna palabra a las stopwords?")
        print("1. Sí, agregar palabras específicas")
        print("2. No, los resultados están bien")
        print("3. Ver todas las stopwords actuales")

        opcion = input("\nElige una opción (1-3): ").strip()

        if opcion == '1':
            print(f"\nPalabras actuales en el top: {[p[0] for p in top_palabras_con_limpieza]}")
            palabras_agregar = input(
                "Ingresa las palabras que quieres agregar (separadas por espacios): ").lower().split()

            if palabras_agregar:
                nuevas_stopwords = set(palabras_agregar)
                stopwords_actuales.update(nuevas_stopwords)
                print(f"✓ Agregadas {len(nuevas_stopwords)} nuevas stopwords: {nuevas_stopwords}")
                print(f"🎯 Total stopwords ahora: {len(stopwords_actuales)}")

                # Re-procesar con las nuevas stopwords
                print("\n🔄 Re-procesando con las nuevas stopwords...")
                word_counts_mejorado = procesar_y_contar(all_text, stopwords=stopwords_actuales)
                top_words_mejorado = word_counts_mejorado.most_common(top_n)
                print(f"Top {top_n} palabras (con stopwords mejoradas):", top_words_mejorado)

                # Mostrar comparación
                print(f"\n📊 COMPARACIÓN:")
                print(f"ANTES: {[p[0] for p in top_palabras_con_limpieza]}")
                print(f"AHORA: {[p[0] for p in top_words_mejorado]}")

                top_palabras_con_limpieza = top_words_mejorado

        elif opcion == '2':
            print("✓ Perfecto! Manteniendo los resultados actuales.")
            break

        elif opcion == '3':
            print(f"\n📋 Stopwords actuales ({len(stopwords_actuales)} palabras):")
            # Mostrar en columnas para mejor visualización
            stopwords_lista = sorted(stopwords_actuales)
            for i in range(0, len(stopwords_lista), 8):
                print("   " + " | ".join(f"{palabra:12}" for palabra in stopwords_lista[i:i + 8]))

        else:
            print("❌ Opción no válida. Por favor elige 1, 2 o 3.")

    return stopwords_actuales, top_palabras_con_limpieza


# Ejecutar la funcionalidad interactiva
stopwords_en, top_words_con_limpieza = agregar_stopwords_interactivo(stopwords_en, top_words_con_limpieza)

# --- VISUALIZACIÓN FINAL MEJORADA ---
print("\n" + "=" * 60)
print("📈 PASO 5: VISUALIZACIÓN FINAL")
print("=" * 60)

# Re-procesar para la visualización final
word_counts_final = procesar_y_contar(all_text, stopwords=stopwords_en)
top_words_final = word_counts_final.most_common(top_n)

# Crear visualización final
words_sin, counts_sin = zip(*top_words_sin_limpieza)
words_final, counts_final = zip(*top_words_final)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))

# Gráfico 1: Sin Limpieza
ax1.bar(words_sin, counts_sin, color='#ff9999')
ax1.set_title('Frecuencias ANTES de Cualquier Limpieza', fontsize=16)
ax1.set_xlabel('Palabras')
ax1.set_ylabel('Frecuencia')
ax1.tick_params(axis='x', rotation=45)

# Gráfico 2: Con Limpieza Mejorada
ax2.bar(words_final, counts_final, color='#99ff99')
ax2.set_title('Frecuencias DESPUÉS de Limpieza Mejorada', fontsize=16)
ax2.set_xlabel('Palabras')
ax2.set_ylabel('Frecuencia')
ax2.tick_params(axis='x', rotation=45)

# Título general para toda la figura
fig.suptitle('Impacto de la Eliminación de Stopwords (Versión Mejorada)', fontsize=20)

# Ajustamos el layout y mostramos
plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.show()

print(f"\n🎉 ANÁLISIS COMPLETADO!")
print(f"📊 Stopwords finales utilizadas: {len(stopwords_en)} palabras")
print(f"🔍 Palabras clave identificadas: {[p[0] for p in top_words_final]}")
print(f"📈 Reducción de ruido: De {len(word_counts_sin_limpieza)} a {len(word_counts_final)} palabras únicas")