import cloudscraper
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.by import By
import pickle
import time
import os
import csv

# Ruta donde se guardarán las cookies
COOKIES_PATH = "cookies.pkl"
# Ruta del archivo CSV
CSV_PATH = 'ecommerce_urls_full.csv'
# Lista de proxies gratuitos (utiliza solo si es necesario)
PROXY = 'http://51.158.68.68:8811'  # Ejemplo de un proxy gratuito

# Intentar hacer scraping con CloudScraper
def scrape_with_cloudscraper(page_number):
    try:
        scraper = cloudscraper.create_scraper()
        current_url = f"https://www.aftership.com/brands/page/{page_number}?region=PE&sort=rank"
        print(f"Usando CloudScraper para la página: {current_url}")
        response = scraper.get(current_url)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            return soup
        else:
            print("CloudScraper falló en evitar la verificación de Cloudflare.")
            return None
    except Exception as e:
        print(f"Error en CloudScraper: {e}")
        return None

# Guardar cookies para futuras sesiones
def save_cookies(driver, path):
    with open(path, "wb") as file:
        pickle.dump(driver.get_cookies(), file)

# Cargar cookies guardadas
def load_cookies(driver, path):
    if os.path.exists(path):
        with open(path, "rb") as file:
            cookies = pickle.load(file)
            for cookie in cookies:
                driver.add_cookie(cookie)
    else:
        print(f"Archivo de cookies no encontrado: {path}")

# Inicializar undetected-chromedriver con opciones de proxy (si es necesario)
def init_driver(use_proxy=False):
    options = uc.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    # Si se quiere usar un proxy, agregarlo aquí
    if use_proxy:
        options.add_argument(f'--proxy-server={PROXY}')
        print(f"Usando el proxy: {PROXY}")

    driver = uc.Chrome(options=options)
    return driver

# Resolver CAPTCHA manualmente y reutilizar cookies
def solve_captcha_and_save_cookies(driver, page_number):
    current_url = f"https://www.aftership.com/brands/page/{page_number}?region=PE&sort=rank"
    print(f"Resuelve el CAPTCHA manualmente para: {current_url}")
    driver.get(current_url)
    input("Resuelve el CAPTCHA y presiona Enter cuando hayas terminado...")
    save_cookies(driver, COOKIES_PATH)

# Extraer los datos de la página
def extract_data(driver, csv_writer, page_number):
    current_url = f"https://www.aftership.com/brands/page/{page_number}?region=PE&sort=rank"
    driver.get(current_url)
    time.sleep(3)
    
    ecommerce_items = driver.find_elements(By.CSS_SELECTOR, "ol.ais-Hits-list li.ais-Hits-item a")
    if not ecommerce_items:
        return False

    for item in ecommerce_items:
        try:
            ecommerce_name = item.get_attribute('title')
            ecommerce_url = item.get_attribute('href')
            print(f'{ecommerce_name}: {ecommerce_url}')
            csv_writer.writerow([ecommerce_name, ecommerce_url])
        except Exception as e:
            print(f"Error: {e}")
            continue
    return True

# Intentar hacer scraping usando Selenium con undetected-chromedriver
def scrape_with_selenium(page_number):
    driver = init_driver(use_proxy=False)  # Cambia a True si deseas usar el proxy
    
    # Intentar cargar cookies guardadas
    try:
        load_cookies(driver, COOKIES_PATH)
    except Exception as e:
        print(f"Error cargando cookies: {e}")

    # Si las cookies no son válidas, resolver el CAPTCHA manualmente
    solve_captcha_and_save_cookies(driver, page_number)
    
    # Abrir archivo CSV para escribir los datos
    with open(CSV_PATH, 'w', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['Ecommerce Name', 'URL'])

        while True:
            success = extract_data(driver, csv_writer, page_number)
            if not success:
                print(f"No se encontraron más elementos en la página {page_number}. Fin de la iteración.")
                break
            page_number += 1

    driver.quit()

# Proceso principal que combina ambos métodos
def main():
    page_number = 319

    # Primero intenta con CloudScraper
    soup = scrape_with_cloudscraper(page_number)
    if soup is None:
        # Si CloudScraper falla, intentar con Selenium
        scrape_with_selenium(page_number)
    else:
        # Si CloudScraper funciona, extraer los datos usando BeautifulSoup
        ecommerce_items = soup.select("ol.ais-Hits-list li.ais-Hits-item a")
        with open(CSV_PATH, 'w', newline='', encoding='utf-8') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(['Ecommerce Name', 'URL'])
            
            for item in ecommerce_items:
                ecommerce_name = item.get('title')
                ecommerce_url = item.get('href')
                print(f'{ecommerce_name}: {ecommerce_url}')
                csv_writer.writerow([ecommerce_name, ecommerce_url])

if __name__ == "__main__":
    main()
