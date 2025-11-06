"""
Amazon Scraper Module using Playwright (Sync version)
"""
import time
import re
from playwright.sync_api import sync_playwright


class AmazonScraper:
    def __init__(self, headless=True):
        self.productos = []
        self.headless = headless

    def scrape_productos(self, busqueda, cantidad=20, min_price=0, max_price=float('inf')):
        """Scrapea productos de Amazon de forma síncrona."""
        print(f"\n[BUSQUEDA] Buscando: {busqueda}")
        print(f"[INFO] Cantidad: {cantidad} productos | Rango: {min_price}-{max_price} EUR\n")

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            )
            page = context.new_page()

            url = f"https://www.amazon.es/s?k={busqueda.replace(' ', '+')}"
            print(f"[NAVEGACIÓN] Accediendo a: {url}")

            try:
                page.goto(url, timeout=60000, wait_until='domcontentloaded')
                print("[OK] Página cargada")
            except Exception as e:
                print(f"[ERROR] No se pudo cargar la página: {e}")
                browser.close()
                return []

            # Aceptar cookies
            cookie_selector = '#sp-cc-accept'
            try:
                page.click(cookie_selector, timeout=5000)
                print("[OK] Cookies aceptadas")
            except Exception:
                print("[INFO] No se encontró el botón de cookies o ya estaban aceptadas.")

            # Esperar productos
            try:
                page.wait_for_selector('[data-component-type="s-search-result"]', timeout=15000)
                print("[OK] Productos detectados")
            except Exception as e:
                print(f"[ERROR] No se encontraron productos: {e}")
                browser.close()
                return []

            elements = page.query_selector_all('[data-component-type="s-search-result"]')
            print(f"[INFO] Encontrados {len(elements)} elementos. Procesando hasta {cantidad}...\n")

            scraped_count = 0
            for i, elem in enumerate(elements):
                if scraped_count >= cantidad:
                    break

                try:
                    # Título
                    titulo_elem = elem.query_selector('h2 a span')
                    titulo = titulo_elem.inner_text() if titulo_elem else "Sin titulo"

                    # Precio
                    precio = "N/A"
                    precio_num = 0
                    precio_elem = elem.query_selector('.a-price-whole')
                    if precio_elem:
                        precio_text = precio_elem.inner_text()
                        cleaned_price = precio_text.replace('.', '').replace(',', '.').strip()
                        try:
                            precio_num = float(cleaned_price)
                            precio = f"{precio_num:.2f}".replace('.', ',') + " EUR"
                        except ValueError:
                            pass

                    # --- FILTRADO POR PRECIO ---
                    if not (min_price <= precio_num <= max_price):
                        continue  # Saltar este producto si está fuera del rango

                    # Rating
                    rating_text = "Sin valoración"
                    rating_num = 0
                    rating_elem = elem.query_selector('.a-icon-alt')
                    if rating_elem:
                        rating_content = rating_elem.inner_text()
                        if rating_content and 'estrellas' in rating_content:
                            rating_text = rating_content
                            match = re.search(r'(\d+[,.]\d+)', rating_content)
                            if match:
                                rating_num = float(match.group(1).replace(',', '.'))

                    # Reseñas
                    num_reviews = 0
                    reviews_elem = elem.query_selector('.a-size-base.s-underline-text')
                    if reviews_elem:
                        try:
                            num_reviews = int(reviews_elem.inner_text().replace('.', '').replace(',', ''))
                        except (ValueError, TypeError):
                            pass

                    # URL
                    url_completa = ""
                    link_elem = elem.query_selector('h2 a')
                    if link_elem:
                        link = link_elem.get_attribute('href')
                        if link:
                            url_completa = f"https://www.amazon.es{link}" if not link.startswith('http') else link

                    # --- NAVEGAR A LA PÁGINA DEL PRODUCTO PARA DETALLES ---
                    features = []
                    reviews = []
                    if url_completa:
                        print(f"    -> Visitando página de producto para obtener detalles...")
                        product_page = context.new_page()
                        try:
                            product_page.goto(url_completa, timeout=45000, wait_until='domcontentloaded')

                            # Extraer características
                            feature_elements = product_page.query_selector_all('#feature-bullets ul li span.a-list-item')
                            for feature_elem in feature_elements:
                                features.append(feature_elem.inner_text().strip())

                            # Extraer comentarios
                            review_elements = product_page.query_selector_all('[data-hook="review-collapsed"]')
                            for review_elem in review_elements[:3]:  # Limitar a 3
                                reviews.append(review_elem.inner_text().strip())

                        except Exception as e:
                            print(f"      [WARN] No se pudieron obtener detalles: {e}")
                        finally:
                            product_page.close()

                    producto = {
                        'id': scraped_count + 1,
                        'titulo': titulo.strip(),
                        'precio': precio,
                        'precio_num': precio_num,
                        'rating': rating_text,
                        'rating_num': rating_num,
                        'num_reviews': num_reviews,
                        'url': url_completa,
                        'features': features,
                        'reviews': reviews
                    }

                    self.productos.append(producto)
                    scraped_count += 1
                    print(f"  ✓ Producto {scraped_count}: {titulo[:60]}... | Precio: {precio}")

                except Exception as e:
                    print(f"\n[ERROR] Error procesando un producto: {e}\n")

            browser.close()

        print(f"\n[OK] Scraping completado: {len(self.productos)} productos procesados.")
        return self.productos