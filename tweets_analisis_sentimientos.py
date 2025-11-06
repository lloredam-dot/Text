"""
TWITTER + PYSENTIMIENTO - ANÁLISIS DE SENTIMIENTOS EN TWEETS
Combina descarga de tweets con análisis avanzado de sentimientos y emociones

REQUISITOS:
pip install tweepy pysentimiento matplotlib seaborn

FUNCIONALIDADES:
1. Descarga tweets por palabra clave o usuario
2. Analiza sentimientos (positivo/negativo/neutral)
3. Analiza emociones (alegría, tristeza, enojo, miedo, sorpresa, disgusto)
4. Genera visualizaciones interactivas
5. Guarda resultados completos en JSON
"""

import tweepy
import json
import os
import warnings
import time
from datetime import datetime
from collections import Counter
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Silenciar advertencias de HuggingFace
os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'
warnings.filterwarnings('ignore')

# ============================================
# CONFIGURACIÓN
# ============================================

BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAF445QEAAAAAjCxgFt6xBtmKFlFmEDuPEVKmpWc%3DZmvdUOvevSKimRt4lrgxnmF2mbGle3wJxlRoZhqHRjzCEIksYt1"

# Verificar pysentimiento
try:
    from pysentimiento import create_analyzer
    print("✓ pysentimiento disponible")
    PYSENTIMIENTO_AVAILABLE = True
except ImportError:
    print("✗ pysentimiento no disponible")
    print("  Instala con: pip install pysentimiento")
    PYSENTIMIENTO_AVAILABLE = False


# ============================================
# INICIALIZACIÓN
# ============================================

def verificar_configuracion():
    """Verifica que todo esté configurado correctamente."""
    print("\n" + "=" * 70)
    print(" VERIFICANDO CONFIGURACIÓN")
    print("=" * 70)

    # Verificar Bearer Token
    if not BEARER_TOKEN or BEARER_TOKEN == "tu_bearer_token_aqui":
        print("\n✗ ERROR: Bearer Token no configurado")
        print("\nPasos para obtener tu Bearer Token:")
        print("1. https://developer.twitter.com/en/portal/dashboard")
        print("2. Crea una App")
        print("3. Copia el Bearer Token")
        print("4. Pégalo en la variable BEARER_TOKEN de este script")
        print("\n" + "=" * 70)
        return False

    # Verificar pysentimiento
    if not PYSENTIMIENTO_AVAILABLE:
        print("\n✗ ERROR: pysentimiento no está instalado")
        print("\nInstala con: pip install pysentimiento")
        print("\n" + "=" * 70)
        return False

    print("\n✓ Configuración correcta")
    print("=" * 70 + "\n")
    return True


def inicializar_clientes():
    """Inicializa clientes de Twitter y pysentimiento."""
    print("Inicializando clientes...")

    # Cliente de Twitter
    try:
        twitter_client = tweepy.Client(bearer_token=BEARER_TOKEN)
        print("✓ Cliente de Twitter inicializado")
    except Exception as e:
        print(f"✗ Error al inicializar Twitter: {e}")
        return None, None, None

    # Analizadores de pysentimiento
    try:
        print("Cargando modelos de pysentimiento (puede tardar un momento)...")
        sentiment_analyzer = create_analyzer(task="sentiment", lang="es")
        emotion_analyzer = create_analyzer(task="emotion", lang="es")
        print("✓ Analizadores de sentimientos y emociones cargados")
        return twitter_client, sentiment_analyzer, emotion_analyzer
    except Exception as e:
        print(f"✗ Error al cargar pysentimiento: {e}")
        return twitter_client, None, None


# ============================================
# DESCARGA DE TWEETS
# ============================================

def descargar_tweets_busqueda(twitter_client, query, max_tweets=100):
    """Descarga tweets por búsqueda usando paginación para mayor eficiencia."""
    print(f"\n{'='*70}")
    print(f"DESCARGANDO TWEETS: '{query}'")
    print(f"{'='*70}")
    print(f"Cantidad solicitada: {max_tweets}")
    print("-" * 70)

    tweets = []
    usuarios = {}
    tweets_descargados = 0

    try:
        paginator = tweepy.Paginator(
            twitter_client.search_recent_tweets,
            query=query,
            max_results=10,  # Máximo por página
            tweet_fields=['created_at', 'author_id', 'public_metrics', 'lang'],
            expansions=['author_id'],
            user_fields=['username', 'name', 'verified']
        )

        print("Iniciando descarga paginada...")
        for i, response in enumerate(paginator):
            print(f"  Página {i+1} procesada...", end='\r')
            
            # Guardar usuarios de la página
            if response.includes and 'users' in response.includes:
                for user in response.includes['users']:
                    usuarios[user.id] = user

            # Procesar tweets de la página
            if response.data:
                for tweet in response.data:
                    if tweets_descargados < max_tweets:
                        autor = usuarios.get(tweet.author_id)
                        tweet_data = {
                            'id': str(tweet.id),
                            'texto': tweet.text,
                            'fecha': tweet.created_at.strftime("%Y-%m-%d %H:%M:%S") if tweet.created_at else 'N/A',
                            'autor_username': autor.username if autor else 'N/A',
                            'autor_nombre': autor.name if autor else 'N/A',
                            'verificado': autor.verified if autor else False,
                            'idioma': tweet.lang if hasattr(tweet, 'lang') else 'N/A',
                            'likes': tweet.public_metrics['like_count'] if hasattr(tweet, 'public_metrics') else 0,
                            'retweets': tweet.public_metrics['retweet_count'] if hasattr(tweet, 'public_metrics') else 0,
                            'respuestas': tweet.public_metrics['reply_count'] if hasattr(tweet, 'public_metrics') else 0,
                        }
                        tweets.append(tweet_data)
                        tweets_descargados += 1
                    else:
                        break  # Límite alcanzado
            
            if tweets_descargados >= max_tweets:
                break # Salir del bucle de paginación

            # Pausa cortés para no saturar la API
            time.sleep(1)

        print(f"\n✓ Descargados: {len(tweets)} tweets de {i+1} página(s)")
        print(f"{'='*70}\n")
        return tweets

    except tweepy.TweepyException as e:
        print(f"\n✗ Error al descargar tweets: {e}")
        return []


def descargar_tweets_usuario(twitter_client, username, max_tweets=100):
    """Descarga tweets de un usuario usando paginación."""
    print(f"\n{'='*70}")
    print(f"DESCARGANDO TWEETS DE @{username}")
    print(f"{'='*70}")
    print(f"Cantidad solicitada: {max_tweets}")
    print("-" * 70)

    try:
        user = twitter_client.get_user(username=username)
        if not user.data:
            print(f"✗ Usuario @{username} no encontrado.")
            return []
        user_id = user.data.id

        tweets = []
        tweets_descargados = 0

        paginator = tweepy.Paginator(
            twitter_client.get_users_tweets,
            id=user_id,
            max_results=100,
            tweet_fields=['created_at', 'public_metrics', 'lang']
        )
        
        print("Iniciando descarga paginada...")
        for i, response in enumerate(paginator):
            print(f"  Página {i+1} procesada...", end='\r')

            if response.data:
                for tweet in response.data:
                    if tweets_descargados < max_tweets:
                        tweet_data = {
                            'id': str(tweet.id),
                            'texto': tweet.text,
                            'fecha': tweet.created_at.strftime("%Y-%m-%d %H:%M:%S") if tweet.created_at else 'N/A',
                            'autor_username': username,
                            'autor_nombre': user.data.name,
                            'verificado': user.data.verified if hasattr(user.data, 'verified') else False,
                            'idioma': tweet.lang if hasattr(tweet, 'lang') else 'N/A',
                            'likes': tweet.public_metrics['like_count'] if hasattr(tweet, 'public_metrics') else 0,
                            'retweets': tweet.public_metrics['retweet_count'] if hasattr(tweet, 'public_metrics') else 0,
                            'respuestas': tweet.public_metrics['reply_count'] if hasattr(tweet, 'public_metrics') else 0,
                        }
                        tweets.append(tweet_data)
                        tweets_descargados += 1
                    else:
                        break
            
            if tweets_descargados >= max_tweets:
                break
            
            time.sleep(1)

        print(f"\n✓ Descargados: {len(tweets)} tweets de {i+1} página(s)")
        print(f"{'='*70}\n")
        return tweets

    except tweepy.TweepyException as e:
        print(f"\n✗ Error al descargar tweets: {e}")
        return []


# ============================================
# ANÁLISIS DE SENTIMIENTOS
# ============================================

def analizar_tweets(tweets, sentiment_analyzer, emotion_analyzer):
    """Analiza sentimientos y emociones de los tweets usando procesamiento por lotes."""
    print(f"\n{'='*70}")
    print("ANALIZANDO SENTIMIENTOS Y EMOCIONES")
    print(f"{'='*70}")
    print(f"Analizando {len(tweets)} tweets...")
    print("-" * 70)

    if not tweets:
        print("No hay tweets para analizar.")
        return []

    # Extraer todos los textos para el análisis por lotes
    textos = [tweet['texto'] for tweet in tweets]

    # Realizar análisis en un solo lote (mucho más eficiente)
    print("  Procesando sentimientos...")
    sent_results = sentiment_analyzer.predict(textos)
    print("  Procesando emociones...")
    emo_results = emotion_analyzer.predict(textos)

    tweets_analizados = []
    for i, tweet in enumerate(tweets):
        sent_result = sent_results[i]
        emo_result = emo_results[i]

        # Añadir análisis al tweet
        tweet_analizado = tweet.copy()
        tweet_analizado['sentimiento'] = sent_result.output
        tweet_analizado['sentimiento_confianza'] = float(sent_result.probas[sent_result.output])
        tweet_analizado['sentimiento_scores'] = {k: float(v) for k, v in sent_result.probas.items()}

        tweet_analizado['emocion'] = emo_result.output
        tweet_analizado['emocion_confianza'] = float(emo_result.probas[emo_result.output])
        tweet_analizado['emocion_scores'] = {k: float(v) for k, v in emo_result.probas.items()}

        tweets_analizados.append(tweet_analizado)

    print(f"\n✓ Análisis completado: {len(tweets_analizados)} tweets procesados")
    print(f"{'='*70}\n")

    return tweets_analizados


# ============================================
# ESTADÍSTICAS
# ============================================

def generar_estadisticas(tweets_analizados):
    """Genera estadísticas de los tweets analizados."""
    print(f"\n{'='*70}")
    print("ESTADÍSTICAS DEL ANÁLISIS")
    print(f"{'='*70}\n")

    # Contar sentimientos
    sentimientos = [t['sentimiento'] for t in tweets_analizados]
    contador_sentimientos = Counter(sentimientos)

    print("--- DISTRIBUCIÓN DE SENTIMIENTOS ---")
    for sent, count in contador_sentimientos.most_common():
        porcentaje = (count / len(tweets_analizados)) * 100
        sent_nombre = {'POS': 'POSITIVO', 'NEG': 'NEGATIVO', 'NEU': 'NEUTRAL'}
        print(f"  {sent_nombre.get(sent, sent):<12}: {count:3} ({porcentaje:5.1f}%)")

    # Contar emociones
    emociones = [t['emocion'] for t in tweets_analizados]
    contador_emociones = Counter(emociones)

    print("\n--- DISTRIBUCIÓN DE EMOCIONES ---")
    emociones_es = {
        'joy': 'Alegría',
        'sadness': 'Tristeza',
        'anger': 'Enojo',
        'surprise': 'Sorpresa',
        'disgust': 'Disgusto',
        'fear': 'Miedo'
    }
    for emo, count in contador_emociones.most_common():
        porcentaje = (count / len(tweets_analizados)) * 100
        print(f"  {emociones_es.get(emo, emo):<12}: {count:3} ({porcentaje:5.1f}%)")

    # Tweet más popular
    if tweets_analizados:
        tweet_top = max(tweets_analizados, key=lambda x: x['likes'] + x['retweets'])
        print("\n--- TWEET MÁS POPULAR ---")
        print(f"  Usuario: @{tweet_top['autor_username']}")
        print(f"  Texto: {tweet_top['texto'][:100]}...")
        print(f"  ❤️ {tweet_top['likes']} | 🔄 {tweet_top['retweets']}")
        print(f"  Sentimiento: {tweet_top['sentimiento']} ({tweet_top['sentimiento_confianza']:.1%})")
        print(f"  Emoción: {tweet_top['emocion']} ({tweet_top['emocion_confianza']:.1%})")

    # Ejemplos por sentimiento
    print("\n--- EJEMPLOS DE TWEETS ---")
    for sent_tipo in ['POS', 'NEG', 'NEU']:
        ejemplos = [t for t in tweets_analizados if t['sentimiento'] == sent_tipo]
        if ejemplos:
            ejemplo = ejemplos[0]
            sent_nombre = {'POS': 'POSITIVO', 'NEG': 'NEGATIVO', 'NEU': 'NEUTRAL'}
            print(f"\n{sent_nombre[sent_tipo]}:")
            print(f"  '{ejemplo['texto'][:80]}...'")
            print(f"  @{ejemplo['autor_username']} | Confianza: {ejemplo['sentimiento_confianza']:.1%}")

    print(f"\n{'='*70}\n")

    return {
        'sentimientos': contador_sentimientos,
        'emociones': contador_emociones
    }


# ============================================
# VISUALIZACIONES
# ============================================

def visualizar_analisis(tweets_analizados, estadisticas, titulo="Análisis de Tweets"):
    """Genera visualizaciones del análisis."""
    print(f"\n{'='*70}")
    print("GENERANDO VISUALIZACIONES")
    print(f"{'='*70}")
    print("Creando gráficos...")

    fig = plt.figure(figsize=(18, 10))
    gs = fig.add_gridspec(2, 3, hspace=0.3, wspace=0.3)

    # 1. Distribución de Sentimientos (Pie)
    ax1 = fig.add_subplot(gs[0, 0])
    sentimientos = estadisticas['sentimientos']
    labels = ['Positivo', 'Negativo', 'Neutral']
    sizes = [sentimientos.get('POS', 0), sentimientos.get('NEG', 0), sentimientos.get('NEU', 0)]
    colors = ['#66bb6a', '#ef5350', '#ffa726']

    ax1.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
            startangle=90, textprops={'fontsize': 10, 'weight': 'bold'})
    ax1.set_title('Distribución de Sentimientos', fontsize=14, fontweight='bold')

    # 2. Distribución de Emociones (Barras)
    ax2 = fig.add_subplot(gs[0, 1:])
    emociones = estadisticas['emociones']
    emociones_es = {
        'joy': 'Alegría', 'sadness': 'Tristeza', 'anger': 'Enojo',
        'surprise': 'Sorpresa', 'disgust': 'Disgusto', 'fear': 'Miedo'
    }
    colores_emo = {
        'joy': '#ffeb3b', 'sadness': '#2196f3', 'anger': '#f44336',
        'surprise': '#9c27b0', 'disgust': '#4caf50', 'fear': '#ff9800'
    }

    emo_ordenadas = sorted(emociones.items(), key=lambda x: x[1], reverse=True)
    nombres = [emociones_es.get(e[0], e[0]) for e in emo_ordenadas]
    valores = [e[1] for e in emo_ordenadas]
    colores = [colores_emo.get(e[0], '#999') for e in emo_ordenadas]

    ax2.barh(nombres, valores, color=colores, edgecolor='black', linewidth=1.5)
    ax2.set_xlabel('Cantidad de Tweets', fontsize=12, fontweight='bold')
    ax2.set_title('Distribución de Emociones', fontsize=14, fontweight='bold')
    ax2.grid(axis='x', alpha=0.3)

    # 3. Timeline de Sentimientos
    ax3 = fig.add_subplot(gs[1, 0])
    sentimientos_time = [1 if t['sentimiento'] == 'POS' else (-1 if t['sentimiento'] == 'NEG' else 0)
                         for t in tweets_analizados]
    ax3.plot(sentimientos_time, marker='o', linestyle='-', markersize=4, linewidth=1.5,
             color='#2196f3', markerfacecolor='#ff5722')
    ax3.axhline(y=0, color='gray', linestyle='--', linewidth=1)
    ax3.set_ylabel('Sentimiento', fontsize=12, fontweight='bold')
    ax3.set_xlabel('Tweet #', fontsize=12, fontweight='bold')
    ax3.set_title('Evolución de Sentimientos', fontsize=14, fontweight='bold')
    ax3.set_yticks([-1, 0, 1])
    ax3.set_yticklabels(['Negativo', 'Neutral', 'Positivo'])
    ax3.grid(True, alpha=0.3)

    # 4. Top Usuarios
    ax4 = fig.add_subplot(gs[1, 1])
    usuarios = Counter([t['autor_username'] for t in tweets_analizados])
    top_usuarios = usuarios.most_common(10)
    if top_usuarios:
        nombres_usuarios = [u[0][:15] for u in top_usuarios]
        counts = [u[1] for u in top_usuarios]
        ax4.barh(nombres_usuarios, counts, color='#9c27b0', edgecolor='black', linewidth=1.5)
        ax4.set_xlabel('Tweets', fontsize=12, fontweight='bold')
        ax4.set_title('Top 10 Usuarios Activos', fontsize=14, fontweight='bold')
        ax4.grid(axis='x', alpha=0.3)

    # 5. Engagement vs Sentimiento
    ax5 = fig.add_subplot(gs[1, 2])
    engagement = [t['likes'] + t['retweets'] for t in tweets_analizados]
    sent_colors = ['#66bb6a' if t['sentimiento'] == 'POS' else
                   ('#ef5350' if t['sentimiento'] == 'NEG' else '#ffa726')
                   for t in tweets_analizados]

    ax5.scatter(range(len(engagement)), engagement, c=sent_colors, alpha=0.6, s=50)
    ax5.set_ylabel('Engagement (Likes + RTs)', fontsize=12, fontweight='bold')
    ax5.set_xlabel('Tweet #', fontsize=12, fontweight='bold')
    ax5.set_title('Engagement por Tweet', fontsize=14, fontweight='bold')
    ax5.grid(True, alpha=0.3)

    # Crear leyenda manual para scatter
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#66bb6a', label='Positivo'),
        Patch(facecolor='#ef5350', label='Negativo'),
        Patch(facecolor='#ffa726', label='Neutral')
    ]
    ax5.legend(handles=legend_elements, loc='upper right')

    # Título general
    fig.suptitle(f'{titulo} - Análisis con PySentimiento',
                 fontsize=18, fontweight='bold', y=0.98)

    print("✓ Visualizaciones generadas")
    print(f"{'='*70}\n")

    plt.tight_layout()
    plt.show()


# ============================================
# GUARDAR RESULTADOS
# ============================================

def guardar_resultados(tweets_analizados, estadisticas, nombre_archivo="tweets_analizados.json"):
    """Guarda tweets analizados y estadísticas en JSON."""
    print(f"Guardando resultados en {nombre_archivo}...")

    datos_completos = {
        'metadata': {
            'total_tweets': len(tweets_analizados),
            'fecha_analisis': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'estadisticas': {
                'sentimientos': {k: v for k, v in estadisticas['sentimientos'].items()},
                'emociones': {k: v for k, v in estadisticas['emociones'].items()}
            }
        },
        'tweets': tweets_analizados
    }

    try:
        with open(nombre_archivo, 'w', encoding='utf-8') as f:
            json.dump(datos_completos, f, ensure_ascii=False, indent=2)
        print(f"✓ Resultados guardados exitosamente\n")
    except Exception as e:
        print(f"✗ Error al guardar: {e}\n")


# ============================================
# PROGRAMA PRINCIPAL
# ============================================

def main():
    print("\n" + "=" * 70)
    print(" TWITTER + PYSENTIMIENTO - ANÁLISIS DE SENTIMIENTOS")
    print("=" * 70 + "\n")

    # Verificar configuración
    if not verificar_configuracion():
        return

    # Inicializar clientes
    twitter_client, sentiment_analyzer, emotion_analyzer = inicializar_clientes()
    if not twitter_client or not sentiment_analyzer or not emotion_analyzer:
        return

    # Menú principal
    while True:
        print("\n" + "=" * 70)
        print("MENÚ PRINCIPAL")
        print("=" * 70)
        print("1. Analizar tweets por palabra clave")
        print("2. Analizar tweets de un usuario")
        print("3. Salir")
        print("-" * 70)

        opcion = input("Elige una opción (1-3): ").strip()

        tweets_analizados = None

        if opcion == "1":
            query = input("\nPalabra clave o hashtag: ").strip()
            if not query:
                print("Debe ingresar una palabra clave.")
                continue

            cantidad = input("Cantidad de tweets a descargar (e.g., 200, 500, default 25): ").strip()
            max_tweets = int(cantidad) if cantidad.isdigit() else 25
            max_tweets = min(5000, max(10, max_tweets))

            # Descargar tweets
            tweets = descargar_tweets_busqueda(twitter_client, query, max_tweets)

            if tweets:
                # Analizar
                tweets_analizados = analizar_tweets(tweets, sentiment_analyzer, emotion_analyzer)

                # Estadísticas
                estadisticas = generar_estadisticas(tweets_analizados)

                # Visualizar
                mostrar = input("\n¿Mostrar gráficos? (s/n): ").strip().lower()
                if mostrar == 's':
                    visualizar_analisis(tweets_analizados, estadisticas, f"Análisis: {query}")

                # Guardar
                guardar = input("¿Guardar resultados? (s/n): ").strip().lower()
                if guardar == 's':
                    nombre = input("Nombre archivo (tweets_analizados.json): ").strip() or "tweets_analizados.json"
                    if not nombre.endswith('.json'):
                        nombre += '.json'
                    guardar_resultados(tweets_analizados, estadisticas, nombre)

        elif opcion == "2":
            username = input("\nUsuario (sin @): ").strip()
            if not username:
                print("Debe ingresar un usuario.")
                continue

            cantidad = input("Cantidad de tweets a descargar (máx 3200, default 25): ").strip()
            max_tweets = int(cantidad) if cantidad.isdigit() else 25
            max_tweets = min(3200, max(10, max_tweets))

            # Descargar tweets
            tweets = descargar_tweets_usuario(twitter_client, username, max_tweets)

            if tweets:
                # Analizar
                tweets_analizados = analizar_tweets(tweets, sentiment_analyzer, emotion_analyzer)

                # Estadísticas
                estadisticas = generar_estadisticas(tweets_analizados)

                # Visualizar
                mostrar = input("\n¿Mostrar gráficos? (s/n): ").strip().lower()
                if mostrar == 's':
                    visualizar_analisis(tweets_analizados, estadisticas, f"Análisis: @{username}")

                # Guardar
                guardar = input("¿Guardar resultados? (s/n): ").strip().lower()
                if guardar == 's':
                    nombre = input("Nombre archivo (tweets_analizados.json): ").strip() or "tweets_analizados.json"
                    if not nombre.endswith('.json'):
                        nombre += '.json'
                    guardar_resultados(tweets_analizados, estadisticas, nombre)

        elif opcion == "3":
            print("\n¡Hasta luego!")
            break

        else:
            print("\nOpción no válida.")


# ============================================
# EJEMPLOS DE USO RÁPIDO
# ============================================

def ejemplo_rapido():
    """Ejemplo de uso rápido sin menú."""

    # Inicializar
    twitter_client, sentiment_analyzer, emotion_analyzer = inicializar_clientes()

    # Analizar tweets sobre Bitcoin
    tweets = descargar_tweets_busqueda(twitter_client, "bitcoin", max_tweets=50)
    tweets_analizados = analizar_tweets(tweets, sentiment_analyzer, emotion_analyzer)
    estadisticas = generar_estadisticas(tweets_analizados)
    visualizar_analisis(tweets_analizados, estadisticas, "Bitcoin")
    guardar_resultados(tweets_analizados, estadisticas, "bitcoin_analisis.json")


if __name__ == "__main__":
    main()

    # Para uso rápido, descomenta:
    # ejemplo_rapido()
