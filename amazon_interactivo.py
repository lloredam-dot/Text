"""
Scraper Interactivo de Amazon - VERSIÓN MEJORADA
Ejecutar: python amazon_interactivo.py
"""

import asyncio
import json
from datetime import datetime
import subprocess
import sys


# --- VERIFICACIÓN DE DEPENDENCIAS ---
def verificar_playwright():
    """Verifica si Playwright y sus navegadores están instalados, e intenta instalarlos si no lo están."""
    try:
        from playwright.async_api import async_playwright
        print("✓ Playwright detectado.")
        # Aunque la librería esté, los navegadores podrían faltar.
        print("Verificando navegadores (esto puede tardar un momento si es la primera vez)...")
        subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True, capture_output=True)
        print("✓ Navegador Chromium listo.")
        return True
    except ImportError:
        print("✗ Playwright no está instalado. Intentando instalar...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "playwright"])
            print("✓ Playwright instalado. Ahora instalando navegadores...")
            subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])
            print("✓ Navegador Chromium listo.")
            return True
        except Exception as e:
            print(f"✗ Falló la instalación automática: {e}")
            print("\nPor favor, instala Playwright manualmente en tu terminal:")
            print("  1. pip install playwright")
            print("  2. playwright install chromium")
            return False
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"✗ Error al instalar el navegador de Playwright: {e}")
        print("  Por favor, ejecuta 'playwright install chromium' en tu terminal.")
        return False


class AmazonScraper:
    def __init__(self):
        self.productos = []
        self.seleccionados = []

    async def scrape_productos(self, busqueda, cantidad=20):
        """Scrapea productos de Amazon con selectores mejorados"""
        print(f"\n[BUSQUEDA] Buscando: {busqueda}")
        print(f"[INFO] Cantidad: {cantidad} productos\n")

        from playwright.async_api import async_playwright
        async with async_playwright() as p:
            # Abrir navegador con configuración mejorada
            browser = await p.chromium.launch(
                headless=False,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor'
                ]
            )

            # Crear contexto con user-agent personalizado
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            )

            page = await context.new_page()

            # Ir a Amazon
            url = f"https://www.amazon.es/s?k={busqueda.replace(' ', '+')}"
            print(f"[NAVEGACIÓN] Accediendo a: {url}")

            try:
                await page.goto(url, timeout=60000, wait_until='domcontentloaded')
                print("[OK] Página cargada")
            except Exception as e:
                print(f"[ERROR] No se pudo cargar la página: {e}")
                await browser.close()
                return []

            # Aceptar cookies con múltiples selectores
            cookie_selectors = [
                '#sp-cc-accept',
                '#a-autoid-0',
                'input[data-action-type="DISMISS"]',
                '.a-button-primary[aria-labelledby*="cookie"]'
            ]

            for selector in cookie_selectors:
                try:
                    await page.click(selector, timeout=2000)
                    print("[OK] Cookies aceptadas")
                    break
                except:
                    continue

            # Esperar productos con timeout más largo
            try:
                await page.wait_for_selector('[data-component-type="s-search-result"]', timeout=15000)
                print("[OK] Productos detectados en la página")
            except Exception as e:
                print(f"[ERROR] No se encontraron productos: {e}")
                # Intentar hacer scroll para cargar productos
                await page.evaluate("window.scrollTo(0, 500);")
                await asyncio.sleep(2)

            # Extraer productos
            elements = await page.query_selector_all('[data-component-type="s-search-result"]')
            print(f"[INFO] Encontrados {len(elements)} elementos\n")
            scraped_count = 0

            for i, elem in enumerate(elements[:cantidad]):
                try:
                    # TÍTULO - MÚLTIPLES ESTRATEGIAS
                    titulo = "Sin título"

                    # Estrategia 1: Selector específico dentro del elemento de producto
                    titulo_selectors = [
                        'h2 a span',  # Selector más común
                        'span.a-size-medium',  # Clase de tamaño medio
                        'span.a-text-normal',  # Texto normal
                        'h2 span',  # Span dentro de h2
                        'a span',  # Span dentro de enlace
                        '.a-size-base-plus'  # Clase base plus
                    ]

                    for selector in titulo_selectors:
                        try:
                            titulo_elem = await elem.query_selector(selector)
                            if titulo_elem:
                                titulo_text = await titulo_elem.inner_text()
                                if titulo_text and len(titulo_text) > 5:  # Verificar que tenga contenido
                                    titulo = titulo_text
                                    break
                        except:
                            continue

                    # Estrategia 2: Buscar por atributos ARIA
                    if titulo == "Sin título":
                        try:
                            aria_elem = await elem.query_selector('[aria-label]')
                            if aria_elem:
                                aria_label = await aria_elem.get_attribute('aria-label')
                                if aria_label and len(aria_label) > 10:
                                    titulo = aria_label
                        except:
                            pass

                    # Estrategia 3: Buscar cualquier texto que parezca un título
                    if titulo == "Sin título":
                        try:
                            # Obtener todo el texto del elemento y tomar la primera línea significativa
                            all_text = await elem.inner_text()
                            lines = [line.strip() for line in all_text.split('\n') if line.strip()]
                            for line in lines:
                                if len(line) > 10 and not any(
                                        word in line.lower() for word in ['€', 'eur', 'precio', 'rating']):
                                    titulo = line
                                    break
                        except:
                            pass

                    # PRECIO - Estrategias mejoradas
                    precio = "N/A"
                    precio_num = 0

                    # Selectores de precio
                    precio_selectors = [
                        '.a-price-whole',
                        '.a-price .a-offscreen',
                        '.a-price[data-a-size="xl"]',
                        '.a-text-price',
                        '[aria-label*="precio"]'
                    ]

                    for p_selector in precio_selectors:
                        try:
                            precio_elem = await elem.query_selector(p_selector)
                            if precio_elem:
                                precio_text = await precio_elem.inner_text()
                                if precio_text:
                                    # Limpiar y convertir precio
                                    cleaned_price = precio_text.replace('€', '').replace(',', '.').strip()
                                    try:
                                        precio_num = float(cleaned_price)
                                        precio = f"{precio_num:.2f}".replace('.', ',') + " EUR"
                                        break
                                    except:
                                        continue
                        except:
                            continue

                    # Si no encontramos precio con selectores, buscar en el texto
                    if precio == "N/A":
                        try:
                            elem_text = await elem.inner_text()
                            import re
                            price_match = re.search(r'(\d+[.,]\d{2})\s*€', elem_text)
                            if price_match:
                                precio_num = float(price_match.group(1).replace(',', '.'))
                                precio = f"{precio_num:.2f} EUR".replace('.', ',')
                        except:
                            pass

                    # RATING - Estrategias mejoradas
                    rating_text = "Sin valoración"
                    rating_num = 0
                    num_reviews = 0

                    # Selectores de rating
                    rating_selectors = [
                        '.a-icon-alt',
                        '[aria-label*="estrellas"]',
                        '.a-size-base',
                        '.a-icon-star'
                    ]

                    for r_selector in rating_selectors:
                        try:
                            rating_elem = await elem.query_selector(r_selector)
                            if rating_elem:
                                rating_content = await rating_elem.inner_text() if not r_selector.startswith(
                                    '[') else await rating_elem.get_attribute('aria-label')
                                if rating_content and 'estrellas' in rating_content.lower():
                                    rating_text = rating_content
                                    # Extraer número de rating
                                    import re
                                    rating_match = re.search(r'(\d+[.,]\d+)', rating_content)
                                    if rating_match:
                                        rating_num = float(rating_match.group(1).replace(',', '.'))
                                    break
                        except:
                            continue

                    # RESEÑAS
                    try:
                        reviews_text = await elem.inner_text()
                        import re
                        reviews_match = re.search(r'(\d+[,.]?\d*)\s*(reseñas|valoraciones|opiniones)', reviews_text,
                                                  re.IGNORECASE)
                        if reviews_match:
                            num_reviews = int(reviews_match.group(1).replace('.', '').replace(',', ''))
                    except:
                        num_reviews = 0

                    # URL
                    url_completa = ""
                    link_selectors = ['h2 a', 'a.a-link-normal', 'a[href*="/dp/"]']

                    for l_selector in link_selectors:
                        try:
                            link_elem = await elem.query_selector(l_selector)
                            if link_elem:
                                link = await link_elem.get_attribute('href')
                                if link and not link.startswith('http'):
                                    url_completa = f"https://www.amazon.es{link}"
                                elif link:
                                    url_completa = link
                                break
                        except:
                            continue

                    # --- NAVEGAR A LA PÁGINA DEL PRODUCTO PARA DETALLES ---
                    features = []
                    reviews = []
                    if url_completa:
                        print(f"    -> Visitando página de producto para obtener detalles...")
                        product_page = await context.new_page()
                        await product_page.goto(url_completa, timeout=45000, wait_until='domcontentloaded')

                        # Extraer características (bullet points)
                        try:
                            feature_elements = await product_page.query_selector_all('#feature-bullets ul li span.a-list-item')
                            for feature_elem in feature_elements:
                                feature_text = await feature_elem.inner_text()
                                if feature_text:
                                    features.append(feature_text.strip())
                        except Exception as e:
                            print(f"      [WARN] No se pudieron extraer las características: {e}")

                        # Extraer comentarios/reseñas
                        try:
                            review_elements = await product_page.query_selector_all('[data-hook="review-collapsed"]')
                            for review_elem in review_elements[:5]: # Limitar a 5 para no sobrecargar
                                review_text = await review_elem.inner_text()
                                if review_text:
                                    reviews.append(review_text.strip())
                        except Exception as e:
                            print(f"      [WARN] No se pudieron extraer las reseñas: {e}")

                        await product_page.close()
                    else:
                        print("    -> [WARN] No se encontró URL para este producto, no se pueden obtener detalles.")

                    producto = {
                        'id': i + 1,
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
                    print(f"{i + 1}. {titulo[:70]}...")
                    print(f"   Precio: {precio} | Rating: {rating_text}")
                    if features:
                        print(f"   ✓ {len(features)} características encontradas.")
                    if reviews:
                        print(f"   ✓ {len(reviews)} reseñas encontradas.")

                except Exception as e:
                    print(f"\n[ERROR] Error procesando producto {i + 1}: {e}\n")
                    # Debug: mostrar HTML del elemento para diagnóstico
                    try:
                        elem_html = await elem.inner_html()
                        print(f"[DEBUG] HTML del elemento: {elem_html[:200]}...")
                    except:
                        pass

            # Cerrar
            await context.close()
            await browser.close()

        print(f"\n[OK] Scraping completado: {scraped_count} productos procesados.")
        return self.productos

    def mostrar_productos(self):
        """Muestra lista de productos"""
        if not self.productos:
            print("[ERROR] No hay productos para mostrar")
            return

        print("\n" + "=" * 80)
        print("PRODUCTOS ENCONTRADOS")
        print("=" * 80)

        for p in self.productos:
            print(f"\n[{p['id']}] {p['titulo'][:70]}")
            print(f"    Precio: {p['precio']} EUR")
            print(f"    Rating: {p['rating']} ({p['num_reviews']} reseñas)")
            if p['features']:
                print(f"    Feature: {p['features'][0][:80]}...") # Mostrar primera característica
            if p['reviews']:
                print(f"    Review: '{p['reviews'][0][:80]}...'") # Mostrar primera reseña

    def seleccionar_interactivo(self):
        """Permite seleccionar productos interactivamente"""
        if not self.productos:
            print("[ERROR] No hay productos para seleccionar")
            return

        print("\n" + "=" * 80)
        print("SELECCION INTERACTIVA")
        print("=" * 80)
        print("\nOpciones:")
        print("  - Ingresa numeros separados por comas (ej: 1,3,5)")
        print("  - Ingresa 'todos' para seleccionar todos")
        print("  - Ingresa 'mejor' para seleccionar el mejor valorado")
        print("  - Ingresa 'barato' para seleccionar el mas barato")
        print("  - Ingresa 'precio' para filtrar por rango de precios")
        print("  - Ingresa 'salir' para terminar\n")

        while True:
            opcion = input(">>> ").strip().lower()

            if opcion == 'salir':
                break

            elif opcion == 'todos':
                self.seleccionados = self.productos.copy()
                print(f"[OK] Seleccionados {len(self.seleccionados)} productos")

            elif opcion == 'mejor':
                productos_con_rating = [p for p in self.productos if p['rating_num'] > 0]
                if productos_con_rating:
                    mejor = max(productos_con_rating, key=lambda x: (x['rating_num'], x['num_reviews']))
                    self.seleccionados = [mejor]
                    print(f"[OK] Seleccionado: {mejor['titulo'][:60]}")
                    print(f"    Rating: {mejor['rating']}")
                else:
                    print("[ERROR] No hay productos con valoraciones válidas")

            elif opcion == 'barato':
                validos = [p for p in self.productos if p['precio_num'] > 0]
                if validos:
                    barato = min(validos, key=lambda x: x['precio_num'])
                    self.seleccionados = [barato]
                    print(f"[OK] Seleccionado: {barato['titulo'][:60]}")
                    print(f"    Precio: {barato['precio']} EUR")
                else:
                    print("[ERROR] No hay productos con precio valido")

            elif opcion == 'precio':
                try:
                    min_str = input("  Precio mínimo (dejar en blanco para no tener mínimo): ").strip()
                    max_str = input("  Precio máximo (dejar en blanco para no tener máximo): ").strip()

                    min_price = float(min_str) if min_str else 0
                    max_price = float(max_str) if max_str else float('inf')

                    if min_price > max_price:
                        print("[ERROR] El precio mínimo no puede ser mayor que el máximo.")
                        continue

                    productos_filtrados = [
                        p for p in self.productos
                        if p['precio_num'] > 0 and min_price <= p['precio_num'] <= max_price
                    ]

                    if productos_filtrados:
                        self.seleccionados = productos_filtrados
                        print(f"\n[OK] Se han seleccionado {len(self.seleccionados)} productos entre {min_price:.2f} y {max_price:.2f} EUR.")
                    else:
                        print("\n[INFO] No se encontraron productos en ese rango de precios.")
                except ValueError:
                    print("[ERROR] Por favor, ingresa un número válido para el precio.")

            else:
                # Intentar parsear números
                try:
                    ids = [int(x.strip()) for x in opcion.split(',')]
                    self.seleccionados = [p for p in self.productos if p['id'] in ids]

                    if self.seleccionados:
                        print(f"[OK] Seleccionados {len(self.seleccionados)} productos:")
                        for p in self.seleccionados:
                            print(f"  - {p['titulo'][:60]}")
                    else:
                        print("[ERROR] No se encontraron productos con esos IDs")

                except:
                    print("[ERROR] Opcion no valida")

            # Mostrar seleccionados actuales
            if self.seleccionados:
                total = sum(p['precio_num'] for p in self.seleccionados)
                print(f"\n[CARRITO] {len(self.seleccionados)} productos - Total: {total:.2f} EUR")

    def guardar_seleccion(self):
        """Guarda los productos seleccionados"""
        if not self.seleccionados:
            print("[INFO] No hay productos seleccionados para guardar")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Guardar todos los productos
        filename_all = f'productos_todos_{timestamp}.json'
        with open(filename_all, 'w', encoding='utf-8') as f:
            json.dump(self.productos, f, ensure_ascii=False, indent=2)

        # Guardar seleccionados
        filename_sel = f'productos_seleccionados_{timestamp}.json'
        with open(filename_sel, 'w', encoding='utf-8') as f:
            json.dump(self.seleccionados, f, ensure_ascii=False, indent=2)

        # Crear resumen
        total = sum(p['precio_num'] for p in self.seleccionados)
        resumen = {
            'fecha': timestamp,
            'total_productos': len(self.productos),
            'productos_seleccionados': len(self.seleccionados),
            'total_precio': total,
            'productos': self.seleccionados
        }

        filename_resumen = f'resumen_compra_{timestamp}.json'
        with open(filename_resumen, 'w', encoding='utf-8') as f:
            json.dump(resumen, f, ensure_ascii=False, indent=2)

        print(f"\n[OK] Guardado:")
        print(f"  - Todos: {filename_all}")
        print(f"  - Seleccionados: {filename_sel}")
        print(f"  - Resumen: {filename_resumen}")

    def mostrar_resumen(self):
        """Muestra resumen de la selección"""
        if not self.seleccionados:
            print("\n[INFO] No hay productos seleccionados")
            return

        print("\n" + "=" * 80)
        print("RESUMEN DE COMPRA")
        print("=" * 80)

        total = 0
        for i, p in enumerate(self.seleccionados, 1):
            print(f"\n{i}. {p['titulo'][:70]}")
            print(f"   Precio: {p['precio']} EUR")
            if p['features']:
                print(f"   Características:")
                for feat in p['features'][:3]: # Mostrar hasta 3
                    print(f"     - {feat[:100]}")
            if p['reviews']:
                print(f"   Última reseña: '{p['reviews'][0][:150]}...'")

            print(f"   URL: {p['url'][:60]}...")
            if p['precio_num'] > 0:
                total += p['precio_num']

        print("\n" + "-" * 80)
        print(f"TOTAL: {total:.2f} EUR")
        print("=" * 80)


async def main():
    """Función principal"""
    print("\n" + "=" * 80)
    print("SCRAPER INTERACTIVO DE AMAZON - VERSIÓN MEJORADA")
    print("=" * 80)

    # Verificar dependencias
    if not verificar_playwright():
        print("\n[ERROR] No se pudieron satisfacer las dependencias. Saliendo del programa.")
        return

    # Configuración
    busqueda_input = input("\n¿Qué quieres buscar? (default: guitarra electrica): ").strip()
    busqueda = busqueda_input or "guitarra electrica"

    try:
        cantidad_input = input("¿Cuántos productos quieres ver? [20]: ").strip()
        cantidad = int(cantidad_input) if cantidad_input else 20
    except:
        cantidad = 20

    # Crear scraper
    scraper = AmazonScraper()

    # Scrapear
    await scraper.scrape_productos(busqueda, cantidad)

    if not scraper.productos:
        print("\n[ERROR] No se pudieron extraer productos. Verifica:")
        print("  - Tu conexión a internet")
        print("  - Que Amazon.es esté accesible")
        print("  - Los términos de búsqueda")
        return

    # Mostrar productos
    scraper.mostrar_productos()

    # Selección interactiva
    scraper.seleccionar_interactivo()

    # Mostrar resumen
    scraper.mostrar_resumen()

    # Guardar
    scraper.guardar_seleccion()

    print("\n[OK] Proceso completado!")


if __name__ == "__main__":
    asyncio.run(main())