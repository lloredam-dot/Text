"""
Scraper Interactivo de Amazon con Selenium y Flask
Ejecutar: python amazon_interactivo_imp.py
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


class AmazonScraperSelenium:
    def __init__(self, headless=False):
        self.productos = []
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
        """Maneja cookies y popups emergentes"""
        print("🔄 Manejando cookies y popups...")
        cookie_selectors = ["#sp-cc-accept", "#a-autoid-0"]
        for selector in cookie_selectors:
            try:
                cookie_btn = WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                cookie_btn.click()
                print("✅ Cookies aceptadas")
                time.sleep(1)
                return True
            except (TimeoutException, ElementClickInterceptedException):
                continue
        return False

    def extract_product_data(self, element, index):
        """Extrae datos de un producto individual"""
        try:
            titulo = "Sin título"
            titulo_selectors = ["h2 a span", "h2 span", "span.a-size-medium", "span.a-text-normal", ".a-size-base-plus"]
            for selector in titulo_selectors:
                try:
                    titulo_elem = element.find_element(By.CSS_SELECTOR, selector)
                    titulo_text = titulo_elem.text.strip()
                    if titulo_text and len(titulo_text) > 5:
                        titulo = titulo_text
                        break
                except NoSuchElementException:
                    continue

            precio = "N/A"
            precio_num = 0.0
            precio_selectors = [".a-price-whole", ".a-price .a-offscreen"]
            for selector in precio_selectors:
                try:
                    precio_elem = element.find_element(By.CSS_SELECTOR, selector)
                    precio_text = precio_elem.text.strip()
                    if precio_text:
                        cleaned_price = re.sub(r'[^\d,.]', '', precio_text).replace(',', '.')
                        precio_num = float(cleaned_price)
                        precio = f"{precio_num:.2f} €".replace('.', ',')
                        break
                except (NoSuchElementException, ValueError):
                    continue

            rating_text = "Sin valoración"
            rating_num = 0.0
            try:
                rating_elem = element.find_element(By.CSS_SELECTOR, ".a-icon-alt")
                rating_text = rating_elem.get_attribute('textContent').strip()
                rating_match = re.search(r'(\d+[.,]\d+)', rating_text)
                if rating_match:
                    rating_num = float(rating_match.group(1).replace(',', '.'))
            except NoSuchElementException:
                pass

            num_reviews = 0
            try:
                reviews_elem = element.find_element(By.CSS_SELECTOR, "span[aria-label*='valoraciones']")
                num_reviews = int(re.sub(r'[^\d]', '', reviews_elem.text))
            except NoSuchElementException:
                pass

            url_completa = ""
            try:
                link_elem = element.find_element(By.CSS_SELECTOR, 'h2 a')
                url_completa = link_elem.get_attribute('href')
            except NoSuchElementException:
                pass

            imagen_url = ""
            try:
                img_elem = element.find_element(By.CSS_SELECTOR, 'img.s-image')
                imagen_url = img_elem.get_attribute('src')
            except NoSuchElementException:
                pass

            return {
                'id': index + 1, 'titulo': titulo, 'precio': precio, 'precio_num': precio_num,
                'rating': rating_text, 'rating_num': rating_num, 'num_reviews': num_reviews,
                'url': url_completa, 'imagen_url': imagen_url, 'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"❌ Error extrayendo producto {index + 1}: {e}")
            return None

    def scrape_productos(self, busqueda, cantidad=20, min_price=0.0, max_price=float('inf')):
        """Scrapea productos de Amazon con filtro de precio"""
        print(f"\n🔍 BUSQUEDA: {busqueda}")
        print(f"📦 Objetivo: {cantidad} productos")
        if min_price > 0 or max_price < float('inf'):
            print(f"💰 Rango de precios: {min_price:.2f}€ - {max_price:.2f}€")

        try:
            url = f"https://www.amazon.es/s?k={busqueda.replace(' ', '+')}"
            self.driver.get(url)
            WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            self.handle_cookies_and_popups()
            WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-component-type="s-search-result"]')))

            elements = self.driver.find_elements(By.CSS_SELECTOR, '[data-component-type="s-search-result"]')
            if not elements:
                return []

            productos_procesados = 0
            for i, elem in enumerate(elements):
                if productos_procesados >= cantidad:
                    break
                producto = self.extract_product_data(elem, i)
                if producto and min_price <= producto['precio_num'] <= max_price:
                    self.productos.append(producto)
                    productos_procesados += 1
            return self.productos
        except Exception as e:
            print(f"❌ Error durante el scraping: {e}")
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
    <title>Amazon Scraper</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 600px; margin: 40px auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px; }
        h1 { text-align: center; }
        form { display: flex; flex-direction: column; }
        input[type=text], input[type=number] { padding: 10px; margin-bottom: 15px; border-radius: 5px; border: 1px solid #ccc; }
        input[type=submit] { padding: 10px 20px; background-color: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; }
    </style>
</head>
<body>
    <h1>Amazon Scraper</h1>
    <form action="/scrape" method="post">
        <label for="busqueda">Producto:</label>
        <input type="text" id="busqueda" name="busqueda" value="guitarra electrica">
        
        <label for="cantidad">Cantidad de productos a analizar:</label>
        <input type="number" id="cantidad" name="cantidad" value="20">
        
        <label>Rango de Precios (EUR):</label>
        <input type="number" id="min_price" name="min_price" placeholder="Mínimo (ej: 50)">
        <input type="number" id="max_price" name="max_price" placeholder="Máximo (ej: 500)">
        
        <input type="submit" value="Iniciar Scraping">
    </form>
</body>
</html>
"""

HTML_RESULTS_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Resultados de Scraping</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; margin: 0; background-color: #f0f2f5; }
        .container { max-width: 1200px; margin: 20px auto; padding: 20px; background-color: #fff; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        h1 { text-align: center; color: #1c1e21; border-bottom: 1px solid #ddd; padding-bottom: 10px; }
        .product-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 20px; }
        .product-card { border: 1px solid #ddd; border-radius: 8px; overflow: hidden; transition: box-shadow 0.2s; }
        .product-card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
        .product-card img { width: 100%; height: 200px; object-fit: cover; }
        .product-info { padding: 15px; }
        .product-title { font-size: 1rem; font-weight: 600; height: 3.2em; overflow: hidden; }
        .product-price { font-size: 1.2rem; font-weight: bold; color: #b12704; margin: 10px 0; }
        .product-rating { font-size: 0.9rem; color: #555; }
        .product-link { display: block; text-align: center; padding: 10px; background-color: #007bff; color: #fff; text-decoration: none; font-weight: 600; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Resultados para "{{ busqueda }}"</h1>
        <div class="product-grid">
            {% for p in productos %}
            <div class="product-card">
                <a href="{{ p.url }}" target="_blank"><img src="{{ p.imagen_url }}" alt="{{ p.titulo }}"></a>
                <div class="product-info">
                    <div class="product-title">{{ p.titulo }}</div>
                    <div class="product-price">{{ p.precio }}</div>
                    <div class="product-rating">{{ p.rating }} ({{ p.num_reviews }} reseñas)</div>
                </div>
                <a href="{{ p.url }}" class="product-link" target="_blank">Ver en Amazon</a>
            </div>
            {% endfor %}
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_FORM_TEMPLATE)

@app.route('/scrape', methods=['POST'])
def scrape():
    busqueda = request.form.get('busqueda', 'guitarra electrica')
    cantidad_str = request.form.get('cantidad', '20')
    min_price_str = request.form.get('min_price', '0')
    max_price_str = request.form.get('max_price')

    cantidad = int(cantidad_str) if cantidad_str.isdigit() else 20
    min_price = float(min_price_str) if min_price_str and min_price_str.isdigit() else 0.0
    max_price = float(max_price_str) if max_price_str and max_price_str.isdigit() else float('inf')

    scraper = None
    try:
        scraper = AmazonScraperSelenium(headless=True)
        productos = scraper.scrape_productos(busqueda, cantidad, min_price, max_price)
        return render_template_string(HTML_RESULTS_TEMPLATE, productos=productos, busqueda=busqueda)
    except Exception as e:
        return f"<h1>Error durante el scraping</h1><p>{e}</p>"
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
