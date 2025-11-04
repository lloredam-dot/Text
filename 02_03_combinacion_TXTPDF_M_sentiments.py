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

# --- LÉXICOS DE SENTIMIENTOS EN INGLÉS ---
positive_lexicon = {
    "love", "fantastic", "useful", "appropriate", "incredible", "recommend", "totally", "improve",
    "excellent", "wonderful", "perfect", "good", "great", "amazing", "impressive", "pleasant",
    "satisfied", "happy", "joyful", "positive", "favorable", "beneficial", "advantageous",
    "optimistic", "hopeful", "promising", "brilliant", "extraordinary", "remarkable", "outstanding",
    "magnificent", "splendid", "awesome", "formidable", "profitable", "valuable", "usable",
    "convenient", "accurate", "correct", "advisable", "recommendable", "desirable", "ideal",
    "optimal", "superior", "best", "fine", "nice", "beautiful", "gorgeous", "stunning",
    "marvelous", "terrific", "superb", "delightful", "enjoyable", "pleasing", "comfortable",
    "reliable", "trustworthy", "honest", "sincere", "genuine", "authentic", "truthful",
    "confident", "secure", "safe", "protected", "healthy", "strong", "powerful", "energetic",
    "vibrant", "lively", "dynamic", "active", "creative", "innovative", "inventive", "resourceful",
    "clever", "smart", "intelligent", "wise", "knowledgeable", "experienced", "skillful",
    "talented", "gifted", "capable", "competent", "efficient", "effective", "productive",
    "successful", "winning", "victorious", "triumphant", "champion", "winner", "achiever"
}

negative_lexicon = {
    "terrible", "disappointing", "expensive", "cheap", "awful", "late", "bad", "little",
    "disaster", "horrible", "terrible", "defective", "deficient", "useless", "worthless",
    "catastrophic", "lamentable", "deplorable", "sad", "sadness", "unfortunate", "unhappy",
    "unlucky", "discouraging", "hopeless", "pessimistic", "negative", "adverse", "unfavorable",
    "harmful", "damaging", "detrimental", "injurious", "hurtful", "disadvantageous",
    "inconvenient", "inappropriate", "incorrect", "wrong", "mistaken", "inaccurate",
    "inappropriate", "imperfect", "defective", "deficient", "insufficient", "limited",
    "restricted", "scarce", "poor", "mediocre", "hate", "despise", "loathe", "detest",
    "abhor", "dislike", "displeasing", "unpleasant", "uncomfortable", "painful", "hurtful",
    "harmful", "dangerous", "risky", "unsafe", "vulnerable", "weak", "fragile", "brittle",
    "broken", "damaged", "ruined", "destroyed", "lost", "failed", "defeated", "beaten",
    "rejected", "abandoned", "lonely", "isolated", "alone", "depressed", "miserable",
    "unfortunate", "tragic", "calamitous", "cataclysmic", "devastating", "ruinous",
    "destructive", "fatal", "lethal", "deadly", "mortal", "terminal", "hopeless", "desperate"
}


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
print(" STEP 1: CONFIGURE ANALYSIS")
print("=" * 60)

# 1. Obtener nombre del archivo
nombre_archivo = input("Please enter the file name (.txt or .pdf): ").strip()

# 2. Obtener número de top words
while True:
    try:
        top_n_str = input("How many top words do you want to see? (e.g., 10, 15, 20): ").strip()
        top_n = int(top_n_str)
        if top_n > 0:
            break
        else:
            print("Please enter a positive number.")
    except ValueError:
        print("Invalid input. Please enter an integer.")

# Cargar el corpus desde el archivo
print(f"\nLoading corpus from '{nombre_archivo}'...")
corpus = leer_corpus_desde_archivo(nombre_archivo)

# Si el archivo está vacío o no existe, usar un corpus de ejemplo
if not corpus:
    print("Using example corpus...")
    corpus = [
        "I love this product, it is fantastic and very useful.",
        "The customer service was terrible, very disappointing.",
        "The price is adequate, neither expensive nor cheap.",
        "I would not buy again, the quality is awful.",
        "An incredible experience, I totally recommend it.",
        "The delivery took longer than expected.",
        "Fantastic, simply fantastic.",
        "Not bad, but could improve in some aspects.",
        "The battery lasts very little, a disaster."
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
print(f"\nStep 2: Analyzing frequencies WITHOUT cleaning...")
all_text = ' '.join(corpus)
word_counts_sin_limpieza = procesar_y_contar(all_text)
top_words_sin_limpieza = word_counts_sin_limpieza.most_common(top_n)
print(f"Top {top_n} words (without cleaning):", top_words_sin_limpieza)

# 2. Análisis CON limpieza
print(f"\nStep 3: Analyzing frequencies WITH stopwords cleaning...")
word_counts_con_limpieza = procesar_y_contar(all_text, stopwords=stopwords_en)
top_words_con_limpieza = word_counts_con_limpieza.most_common(top_n)
print(f"Top {top_n} words (with cleaning):", top_words_con_limpieza)

# --- VISUALIZACIÓN COMPARATIVA ---

print("\nGenerating comparative graphs...")

# Desempaquetamos los resultados para ambos gráficos
words_sin, counts_sin = zip(*top_words_sin_limpieza)
words_con, counts_con = zip(*top_words_con_limpieza)

# Creamos una figura con dos subplots (uno al lado del otro)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))

# Gráfico 1: Sin Limpieza
ax1.bar(words_sin, counts_sin, color='#ff9999')
ax1.set_title('Frequencies BEFORE Cleaning', fontsize=16)
ax1.set_xlabel('Words')
ax1.set_ylabel('Frequency')
ax1.tick_params(axis='x', rotation=45)

# Gráfico 2: Con Limpieza
ax2.bar(words_con, counts_con, color='#99ff99')
ax2.set_title('Frequencies AFTER Cleaning', fontsize=16)
ax2.set_xlabel('Words')
ax2.set_ylabel('Frequency')
ax2.tick_params(axis='x', rotation=45)

# Título general para toda la figura
fig.suptitle('Impact of Stopwords Removal', fontsize=20)

# Ajustamos el layout y mostramos
plt.tight_layout(rect=[0, 0, 1, 0.96])  # Ajuste para el supertítulo
plt.show()

print("\n--- END OF INITIAL ANALYSIS ---")
print("Observation: The change is drastic! The right graph reveals the words that really add meaning:")
print("Now we can see the key terms of the analyzed text.")


# --- FUNCIONALIDAD MEJORADA: AGREGAR STOPWORDS MANUALMENTE ---
def agregar_stopwords_interactivo(stopwords_actuales, top_palabras_con_limpieza):
    """Permite al usuario agregar stopwords manualmente basado en los resultados"""
    print("\n" + "=" * 60)
    print("🎯 STEP 4: REFINE STOPWORDS MANUALLY")
    print("=" * 60)

    # Mostrar las palabras que aparecieron después de la limpieza
    print(f"\nWords that appeared after cleaning:")
    for i, (palabra, frecuencia) in enumerate(top_palabras_con_limpieza, 1):
        print(f"  {i:2d}. '{palabra}': {frecuencia} appearances")

    # Preguntar si quiere agregar más stopwords
    while True:
        print(f"\nDo you want to add any words to the stopwords?")
        print("1. Yes, add specific words")
        print("2. No, the results are fine")
        print("3. See all current stopwords")

        opcion = input("\nChoose an option (1-3): ").strip()

        if opcion == '1':
            print(f"\nCurrent words in the top: {[p[0] for p in top_palabras_con_limpieza]}")
            palabras_agregar = input(
                "Enter the words you want to add (separated by spaces): ").lower().split()

            if palabras_agregar:
                nuevas_stopwords = set(palabras_agregar)
                stopwords_actuales.update(nuevas_stopwords)
                print(f"✓ Added {len(nuevas_stopwords)} new stopwords: {nuevas_stopwords}")
                print(f"🎯 Total stopwords now: {len(stopwords_actuales)}")

                # Re-procesar con las nuevas stopwords
                print("\n🔄 Re-processing with new stopwords...")
                word_counts_mejorado = procesar_y_contar(all_text, stopwords=stopwords_actuales)
                top_words_mejorado = word_counts_mejorado.most_common(top_n)
                print(f"Top {top_n} words (with improved stopwords):", top_words_mejorado)

                # Mostrar comparación
                print(f"\n📊 COMPARISON:")
                print(f"BEFORE: {[p[0] for p in top_palabras_con_limpieza]}")
                print(f"NOW: {[p[0] for p in top_words_mejorado]}")

                top_palabras_con_limpieza = top_words_mejorado

        elif opcion == '2':
            print("✓ Perfect! Keeping current results.")
            break

        elif opcion == '3':
            print(f"\n📋 Current stopwords ({len(stopwords_actuales)} words):")
            # Mostrar en columnas para mejor visualización
            stopwords_lista = sorted(stopwords_actuales)
            for i in range(0, len(stopwords_lista), 8):
                print("   " + " | ".join(f"{palabra:12}" for palabra in stopwords_lista[i:i + 8]))

        else:
            print("❌ Invalid option. Please choose 1, 2 or 3.")

    return stopwords_actuales, top_palabras_con_limpieza


# Ejecutar la funcionalidad interactiva
stopwords_en, top_words_con_limpieza = agregar_stopwords_interactivo(stopwords_en, top_words_con_limpieza)

# --- ANÁLISIS DE SENTIMIENTOS ---
print("\n" + "=" * 60)
print("😊 STEP 5: SENTIMENT ANALYSIS")
print("=" * 60)


def analyze_sentiment(text, stopwords, positive_lex, negative_lex):
    """Analyzes text and returns sentiment score and classification."""
    # Clean and tokenize text
    text_lower = text.lower()
    words = re.findall(r'\b\w+\b', text_lower)
    words_cleaned = [word for word in words if word not in stopwords]

    # Count positive and negative words
    positive_score = sum(1 for word in words_cleaned if word in positive_lex)
    negative_score = sum(1 for word in words_cleaned if word in negative_lex)

    # Calculate final score
    final_score = positive_score - negative_score

    # Classification
    if final_score > 0:
        classification = "Positive"
    elif final_score < 0:
        classification = "Negative"
    else:
        classification = "Neutral"

    return {
        "text": text,
        "score": final_score,
        "classification": classification,
        "positive_words": [word for word in words_cleaned if word in positive_lex],
        "negative_words": [word for word in words_cleaned if word in negative_lex]
    }


# Analyze each sentence in the corpus
sentiment_results = [analyze_sentiment(sentence, stopwords_en, positive_lexicon, negative_lexicon) for sentence in
                     corpus]

print("--- SENTIMENT ANALYSIS RESULTS ---")
for i, result in enumerate(sentiment_results, 1):
    print(f"\nSentence {i}: '{result['text']}'")
    if result['positive_words']:
        print(f"  ✓ Positive words: {result['positive_words']}")
    if result['negative_words']:
        print(f"  ✗ Negative words: {result['negative_words']}")
    print(f"  📊 Score: {result['score']}, Classification: {result['classification']}")

# Statistics
sentiment_counts = Counter([res['classification'] for res in sentiment_results])
total_sentences = len(sentiment_results)

print(f"\n{'=' * 50}")
print("CORPUS SENTIMENT SUMMARY")
print(f"{'=' * 50}")
print(f"Total sentences analyzed: {total_sentences}")
for sentiment, count in sentiment_counts.items():
    percentage = (count / total_sentences) * 100
    print(f"  {sentiment}: {count} sentences ({percentage:.1f}%)")

# --- VISUALIZACIÓN DE SENTIMIENTOS ---
print("\nGenerating sentiment visualization...")

# Prepare data for visualization
labels = list(sentiment_counts.keys())
sizes = list(sentiment_counts.values())
colors = {'Positive': '#99ff99', 'Negative': '#ff9999', 'Neutral': '#ffcc99'}
color_list = [colors[label] for label in labels]

# Create figure with two subplots
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8))

# Pie chart
ax1.pie(sizes, labels=labels, colors=color_list, autopct='%1.1f%%', startangle=90, textprops={'fontsize': 12})
ax1.set_title('Sentiment Distribution in Corpus', fontsize=16)

# Bar chart
ax2.bar(labels, sizes, color=color_list)
ax2.set_title('Sentiment Count by Category', fontsize=16)
ax2.set_ylabel('Number of Sentences')
ax2.set_xlabel('Sentiment')

# Add values on bars
for i, v in enumerate(sizes):
    ax2.text(i, v + 0.1, str(v), ha='center', va='bottom', fontsize=12)

plt.tight_layout()
plt.show()

# --- DETAILED SENTIMENT WORD ANALYSIS ---
print("\n" + "=" * 60)
print("📊 DETAILED SENTIMENT WORD ANALYSIS")
print("=" * 60)

# Count sentiment word frequencies in cleaned text
positive_sentiment_words = []
negative_sentiment_words = []

for sentence in corpus:
    sentence_lower = sentence.lower()
    words = re.findall(r'\b\w+\b', sentence_lower)
    words_cleaned = [word for word in words if word not in stopwords_en]

    for word in words_cleaned:
        if word in positive_lexicon:
            positive_sentiment_words.append(word)
        elif word in negative_lexicon:
            negative_sentiment_words.append(word)

# Count frequencies
positive_freq = Counter(positive_sentiment_words)
negative_freq = Counter(negative_sentiment_words)

print("\nMOST FREQUENT POSITIVE WORDS:")
if positive_freq:
    for word, freq in positive_freq.most_common(10):
        print(f"  '{word}': {freq} appearances")
else:
    print("  No positive words found")

print("\nMOST FREQUENT NEGATIVE WORDS:")
if negative_freq:
    for word, freq in negative_freq.most_common(10):
        print(f"  '{word}': {freq} appearances")
else:
    print("  No negative words found")

# --- VISUALIZACIÓN FINAL MEJORADA ---
print("\n" + "=" * 60)
print("📈 STEP 6: FINAL VISUALIZATION")
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
ax1.set_title('Frequencies BEFORE Any Cleaning', fontsize=16)
ax1.set_xlabel('Words')
ax1.set_ylabel('Frequency')
ax1.tick_params(axis='x', rotation=45)

# Gráfico 2: Con Limpieza Mejorada
ax2.bar(words_final, counts_final, color='#99ff99')
ax2.set_title('Frequencies AFTER Improved Cleaning', fontsize=16)
ax2.set_xlabel('Words')
ax2.set_ylabel('Frequency')
ax2.tick_params(axis='x', rotation=45)

# Título general para toda la figura
fig.suptitle('Impact of Stopwords Removal (Improved Version)', fontsize=20)

# Ajustamos el layout y mostramos
plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.show()

print(f"\n🎉 ANALYSIS COMPLETED!")
print(f"📊 Final stopwords used: {len(stopwords_en)} words")
print(f"🔍 Key words identified: {[p[0] for p in top_words_final]}")
print(f"📈 Noise reduction: From {len(word_counts_sin_limpieza)} to {len(word_counts_final)} unique words")
print(
    f"😊 Sentiment summary: {sentiment_counts.get('Positive', 0)} Positive, {sentiment_counts.get('Negative', 0)} Negative, {sentiment_counts.get('Neutral', 0)} Neutral")