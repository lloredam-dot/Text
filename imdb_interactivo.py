"""
Scraper Interactivo de IMDb con Selenium y Flask - VERSIÓN CORREGIDA
Ejecutar: python imdb_scraper.py
"""

import time
import json
import re
import webbrowser
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Intentar importar Flask
try:
    from flask import Flask, render_template_string, request

    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False


class IMDbScraperSelenium:
    def __init__(self, headless=False):
        self.movies = []
        self.driver = None
        self.setup_driver(headless)

    def setup_driver(self, headless=False):
        """Configura el driver de Chrome con opciones mejoradas"""
        print("🔄 Iniciando navegador Chrome...")

        chrome_options = Options()

        if headless:
            chrome_options.add_argument("--headless")

        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        chrome_options.add_argument(
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            print("✅ Navegador Chrome iniciado correctamente")

        except Exception as e:
            print(f"❌ Error al iniciar Chrome: {e}")
            raise

    def handle_cookies_and_popups(self):
        """Maneja cookies y popups emergentes en IMDb"""
        print("🔄 Manejando cookies y popups...")
        cookie_selectors = [
            "#onetrust-accept-btn-handler",
            'button[data-testid="accept-button"]',
            'button:contains("Accept")',
            'button:contains("Aceptar")'
        ]
        for selector in cookie_selectors:
            try:
                cookie_btn = WebDriverWait(self.driver, 3).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                )
                cookie_btn.click()
                print("✅ Cookies/popups manejados")
                time.sleep(1)
                return True
            except (TimeoutException, ElementClickInterceptedException):
                continue
        print("ℹ️ No se encontraron popups de cookies")
        return False

    def extract_movie_data(self, element, index):
        """Extrae datos de una película individual con selectores más robustos"""
        try:
            print(f"🔍 Procesando elemento {index + 1}...")

            # TÍTULO - Múltiples estrategias
            titulo = "Sin título"
            titulo_selectors = [
                "h3 a",
                "h3",
                ".ipc-title__text",
                ".ipc-title-link-wrapper",
                ".find-result-item h3",
                ".result_text a"
            ]

            for selector in titulo_selectors:
                try:
                    titulo_elem = element.find_element(By.CSS_SELECTOR, selector)
                    titulo_text = titulo_elem.text.strip()
                    if titulo_text and len(titulo_text) > 2:
                        titulo = titulo_text
                        # Limpiar número si existe
                        titulo = re.sub(r'^\d+\.\s*', '', titulo)
                        print(f"  ✅ Título encontrado: {titulo[:50]}...")
                        break
                except NoSuchElementException:
                    continue

            # AÑO
            año = "N/A"
            try:
                # Buscar año en el texto del elemento completo
                element_text = element.text
                year_match = re.search(r'(19|20)\d{2}', element_text)
                if year_match:
                    año = year_match.group()
                print(f"  📅 Año: {año}")
            except:
                pass

            # RATING - Estrategias múltiples
            rating_text = "Sin rating"
            rating_num = 0.0
            rating_selectors = [
                ".ipc-rating-star",
                ".rating-rating",
                ".ratings-imdb-rating",
                "[data-testid='ratingGroup']"
            ]

            for selector in rating_selectors:
                try:
                    rating_elem = element.find_element(By.CSS_SELECTOR, selector)
                    rating_content = rating_elem.text.strip()
                    if rating_content:
                        rating_match = re.search(r'(\d+[.,]\d+)', rating_content)
                        if rating_match:
                            rating_num = float(rating_match.group(1).replace(',', '.'))
                            rating_text = f"{rating_num}/10"
                            print(f"  ⭐ Rating: {rating_text}")
                            break
                except NoSuchElementException:
                    continue

            # DURACIÓN
            duracion = "N/A"
            try:
                # Buscar patrones de duración en el texto
                element_text = element.text
                duration_match = re.search(r'(\d+h\s*\d+m|\d+ min)', element_text, re.IGNORECASE)
                if duration_match:
                    duracion = duration_match.group(1)
                print(f"  ⏱️ Duración: {duracion}")
            except:
                pass

            # GÉNEROS
            generos = []
            try:
                # Buscar géneros en el texto
                element_text = element.text.lower()
                common_genres = ['action', 'comedy', 'drama', 'horror', 'sci-fi', 'romance', 'thriller', 'documentary']
                for genre in common_genres:
                    if genre in element_text:
                        generos.append(genre.title())
                if generos:
                    print(f"  🎭 Géneros: {generos}")
            except:
                pass

            # URL
            url_completa = ""
            link_selectors = [
                "h3 a",
                "a.ipc-title-link-wrapper",
                ".result_text a",
                ".find-result-item a"
            ]
            for selector in link_selectors:
                try:
                    link_elem = element.find_element(By.CSS_SELECTOR, selector)
                    url_relativa = link_elem.get_attribute('href')
                    if url_relativa:
                        url_completa = f"https://www.imdb.com{url_relativa}" if url_relativa.startswith(
                            '/') else url_relativa
                        print(f"  🔗 URL: {url_completa[:50]}...")
                        break
                except NoSuchElementException:
                    continue

            # IMAGEN
            imagen_url = ""
            img_selectors = [
                "img",
                ".ipc-image",
                ".find-result-item img",
                ".poster img"
            ]
            for selector in img_selectors:
                try:
                    img_elem = element.find_element(By.CSS_SELECTOR, selector)
                    imagen_url = img_elem.get_attribute('src')
                    if imagen_url and 'http' in imagen_url:
                        print(f"  🖼️ Imagen encontrada")
                        break
                except NoSuchElementException:
                    continue

            movie_data = {
                'id': index + 1,
                'titulo': titulo,
                'año': año,
                'rating': rating_text,
                'rating_num': rating_num,
                'duracion': duracion,
                'generos': generos,
                'url': url_completa,
                'imagen_url': imagen_url,
                'timestamp': datetime.now().isoformat()
            }

            # Solo retornar si tenemos al menos un título válido
            if titulo != "Sin título":
                return movie_data
            else:
                print(f"  ❌ Elemento {index + 1} descartado - sin título válido")
                return None

        except Exception as e:
            print(f"❌ Error extrayendo película {index + 1}: {e}")
            return None

    def scrape_movies(self, busqueda, cantidad=20, min_rating=0.0, max_rating=10.0, min_year=1900, max_year=2024):
        """Scrapea películas de IMDb con estrategia mejorada"""
        print(f"\n🎬 BUSQUEDA: {busqueda}")
        print(f"📦 Objetivo: {cantidad} películas")
        print(f"⭐ Rango de rating: {min_rating}-{max_rating}")
        print(f"📅 Años: {min_year}-{max_year}")

        try:
            # Estrategia 1: Búsqueda directa
            search_query = busqueda.replace(' ', '+')
            url = f"https://www.imdb.com/find?q={search_query}&s=tt&ttype=ft"

            print(f"🌐 Navegando a: {url}")
            self.driver.get(url)

            # Esperar a que cargue
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            self.handle_cookies_and_popups()

            # Esperar resultados con múltiples selectores posibles
            print("🔍 Esperando resultados...")
            selectors_to_try = [
                ".find-result",
                ".ipc-metadata-list-summary-item",
                ".find-title-result",
                ".result_text",
                "h3"  # Último recurso: cualquier h3
            ]

            elements = []
            for selector in selectors_to_try:
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        print(f"✅ Encontrados {len(elements)} elementos con selector: {selector}")
                        break
                except TimeoutException:
                    continue

            if not elements:
                print("❌ No se pudieron encontrar resultados en la página")
                # Tomar screenshot para debug
                self.driver.save_screenshot("debug_imdb.png")
                print("📸 Screenshot guardado como 'debug_imdb.png'")
                return []

            print(f"\n--- 🎬 Procesando {len(elements)} elementos encontrados ---")
            peliculas_procesadas = 0

            for i, elem in enumerate(elements):
                if peliculas_procesadas >= cantidad:
                    break

                print(f"\n📝 Procesando elemento {i + 1}/{len(elements)}...")
                pelicula = self.extract_movie_data(elem, peliculas_procesadas)

                if pelicula:
                    # Aplicar filtros
                    año_valido = (pelicula['año'] != "N/A" and
                                  pelicula['año'].isdigit() and
                                  min_year <= int(pelicula['año']) <= max_year)

                    rating_valido = min_rating <= pelicula['rating_num'] <= max_rating

                    if año_valido and rating_valido:
                        self.movies.append(pelicula)
                        peliculas_procesadas += 1
                        print(f"🎉 ✅ Añadida: {pelicula['titulo'][:40]}...")
                    else:
                        print(f"⏭️  Filtrada: {pelicula['titulo'][:40]}... (no cumple filtros)")

            print("\n---------------------------------")
            print(f"✅ Scraping completado: {len(self.movies)} películas obtenidas")

            if not self.movies:
                print("💡 Consejo: Prueba con menos filtros o otra búsqueda")

            return self.movies

        except Exception as e:
            print(f"❌ Error durante el scraping: {e}")
            import traceback
            traceback.print_exc()
            return []

    def close(self):
        if self.driver:
            self.driver.quit()
            print("✅ Navegador cerrado")


app = Flask(__name__)

HTML_FORM_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>IMDb Scraper</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 600px; margin: 40px auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px; background-color: #f5f5f5; }
        h1 { text-align: center; color: #f5c518; }
        form { display: flex; flex-direction: column; }
        input[type=text], input[type=number] { padding: 10px; margin-bottom: 15px; border-radius: 5px; border: 1px solid #ccc; }
        input[type=submit] { padding: 10px 20px; background-color: #f5c518; color: black; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; }
        .filter-group { display: flex; gap: 10px; }
        .filter-group input { flex: 1; }
        label { font-weight: bold; margin-bottom: 5px; }
        .tips { background: #fff3cd; padding: 10px; border-radius: 5px; margin-top: 20px; }
    </style>
</head>
<body>
    <h1>🎬 IMDb Scraper</h1>
    <form action="/scrape" method="post">
        <label for="busqueda">Película o serie a buscar:</label>
        <input type="text" id="busqueda" name="busqueda" value="avengers" required>

        <label for="cantidad">Cantidad de resultados:</label>
        <input type="number" id="cantidad" name="cantidad" value="10" min="1" max="50">

        <label>Rango de Rating (0-10):</label>
        <div class="filter-group">
            <input type="number" id="min_rating" name="min_rating" placeholder="Mínimo (0)" min="0" max="10" step="0.1" value="0">
            <input type="number" id="max_rating" name="max_rating" placeholder="Máximo (10)" min="0" max="10" step="0.1" value="10">
        </div>

        <label>Rango de Años:</label>
        <div class="filter-group">
            <input type="number" id="min_year" name="min_year" placeholder="Desde (1900)" min="1900" max="2024" value="2000">
            <input type="number" id="max_year" name="max_year" placeholder="Hasta (2024)" min="1900" max="2024" value="2024">
        </div>

        <input type="submit" value="🎬 Buscar Películas">
    </form>

    <div class="tips">
        <strong>💡 Consejos:</strong>
        <ul>
            <li>Prueba con: "avengers", "star wars", "batman"</li>
            <li>Usa menos filtros si no encuentras resultados</li>
            <li>La primera búsqueda puede ser más lenta</li>
        </ul>
    </div>
</body>
</html>
"""

HTML_RESULTS_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Resultados de IMDb</title>
    <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.11.5/css/jquery.dataTables.css">
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; background-color: #f4f4f4; }
        h1 { text-align: center; color: #f5c518; }
        .container { max-width: 1400px; margin: auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        table.dataTable thead th { background-color: #f5c518; color: black; }
        .movie-image { max-width: 80px; border-radius: 5px; }
        td { vertical-align: middle; }
        .generos { font-size: 0.9em; color: #666; }
        .rating-high { color: #00a000; font-weight: bold; }
        .rating-medium { color: #ffa500; font-weight: bold; }
        .rating-low { color: #ff0000; font-weight: bold; }
        .no-results { text-align: center; padding: 40px; color: #666; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎬 Resultados para "{{ busqueda }}"</h1>
        {% if peliculas %}
        <table id="moviesTable" class="display" style="width:100%">
            <thead>
                <tr>
                    <th>Poster</th>
                    <th>Título</th>
                    <th>Año</th>
                    <th>Rating</th>
                    <th>Duración</th>
                    <th>Géneros</th>
                    <th>Link</th>
                </tr>
            </thead>
            <tbody>
                {% for m in peliculas %}
                <tr>
                    <td>
                        {% if m.imagen_url %}
                        <img src="{{ m.imagen_url }}" alt="{{ m.titulo }}" class="movie-image">
                        {% else %}
                        <div style="width:80px; height:120px; background:#eee; display:flex; align-items:center; justify-content:center; color:#999;">No image</div>
                        {% endif %}
                    </td>
                    <td>{{ m.titulo }}</td>
                    <td>{{ m.año }}</td>
                    <td class="{% if m.rating_num >= 8 %}rating-high{% elif m.rating_num >= 6 %}rating-medium{% else %}rating-low{% endif %}">
                        {{ m.rating_num }}/10
                    </td>
                    <td>{{ m.duracion }}</td>
                    <td class="generos">{{ m.generos|join(', ') if m.generos else 'N/A' }}</td>
                    <td>
                        {% if m.url %}
                        <a href="{{ m.url }}" target="_blank" style="color: #f5c518; font-weight: bold;">🔗 IMDb</a>
                        {% else %}
                        N/A
                        {% endif %}
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        {% else %}
        <div class="no-results">
            <h2>😞 No se encontraron películas</h2>
            <p>Prueba con:</p>
            <ul>
                <li>Menos filtros</li>
                <li>Otra búsqueda (ej: "avengers", "star wars")</li>
                <li>Verificar la conexión a internet</li>
            </ul>
            <a href="/" style="color: #f5c518;">← Volver a buscar</a>
        </div>
        {% endif %}
    </div>

    {% if peliculas %}
    <script type="text/javascript" charset="utf8" src="https://code.jquery.com/jquery-3.5.1.js"></script>
    <script type="text/javascript" charset="utf8" src="https://cdn.datatables.net/1.11.5/js/jquery.dataTables.js"></script>
    <script>
        $(document).ready(function() {
            $('#moviesTable').DataTable({
                "language": {
                    "url": "//cdn.datatables.net/plug-ins/1.11.5/i18n/es-ES.json"
                },
                "order": [[ 3, "desc" ]],
                "pageLength": 25
            });
        });
    </script>
    {% endif %}
</body>
</html>
"""


@app.route('/')
def index():
    return render_template_string(HTML_FORM_TEMPLATE)


@app.route('/scrape', methods=['POST'])
def scrape():
    busqueda = request.form.get('busqueda', 'avengers')
    cantidad_str = request.form.get('cantidad', '10')
    min_rating_str = request.form.get('min_rating', '0')
    max_rating_str = request.form.get('max_rating', '10')
    min_year_str = request.form.get('min_year', '2000')
    max_year_str = request.form.get('max_year', '2024')

    cantidad = int(cantidad_str) if cantidad_str.isdigit() else 10
    min_rating = float(min_rating_str) if min_rating_str else 0.0
    max_rating = float(max_rating_str) if max_rating_str else 10.0
    min_year = int(min_year_str) if min_year_str and min_year_str.isdigit() else 2000
    max_year = int(max_year_str) if max_year_str and max_year_str.isdigit() else 2024

    scraper = None
    try:
        scraper = IMDbScraperSelenium(headless=False)  # Cambiado a False para debugging
        peliculas = scraper.scrape_movies(busqueda, cantidad, min_rating, max_rating, min_year, max_year)
        return render_template_string(HTML_RESULTS_TEMPLATE, peliculas=peliculas, busqueda=busqueda)
    except Exception as e:
        return f"<h1>Error durante el scraping</h1><p>{e}</p><a href='/'>Volver</a>"
    finally:
        if scraper:
            scraper.close()


if __name__ == "__main__":
    if not FLASK_AVAILABLE:
        print("Flask no está instalado. Por favor, instálalo para usar la interfaz web:")
        print("pip install Flask")
    else:
        url = "http://127.0.0.1:5000"
        print(f"Iniciando servidor web en {url}")
        print("Abre tu navegador y ve a esa dirección para usar la aplicación.")
        webbrowser.open_new(url)
        app.run(debug=False, port=5000)