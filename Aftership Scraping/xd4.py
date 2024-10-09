import cloudscraper
import csv
from bs4 import BeautifulSoup

# Crear una instancia del scraper
scraper = cloudscraper.create_scraper()

# Crear archivo CSV
csv_file = open('ecommerce_urls_full.csv', 'w', newline='', encoding='utf-8')
csv_writer = csv.writer(csv_file)
csv_writer.writerow(['Ecommerce Name', 'URL'])

# Número de la página inicial
page_number = 348

while True:
    current_url = f"https://www.aftership.com/brands/page/{page_number}?region=PE&sort=rank"
    print(f"Analizando página: {page_number} -> {current_url}")
    
    # Obtener contenido de la página usando CloudScraper
    response = scraper.get(current_url)
    
    # Analizar el contenido con BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Extraer los elementos necesarios
    ecommerce_items = soup.select("ol.ais-Hits-list li.ais-Hits-item a")
    
    if not ecommerce_items:
        print(f"No se encontraron más elementos en la página {page_number}. Fin de la iteración.")
        break
    
    # Extraer nombre y URL de cada item
    for item in ecommerce_items:
        try:
            ecommerce_name = item.get('title')
            ecommerce_url = item.get('href')
            print(f'{ecommerce_name}: {ecommerce_url}')
            csv_writer.writerow([ecommerce_name, ecommerce_url])
        except Exception as e:
            print(f"Error: {e}")
            continue
    
    # Incrementar el número de página
    page_number += 1

# Cerrar archivo CSV
csv_file.close()
