import undetected_chromedriver as uc
import time
import csv
import pickle
from selenium.webdriver.common.by import By

# Ruta donde guardaremos y cargaSremos las cookies
COOKIES_PATH = "cookies.pkl"

# Configuración del driver con undetected-chromedriver para evitar detección
def init_driver():
    options = uc.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    driver = uc.Chrome(options=options)
    return driver

# Guardar cookies después de resolver el CAPTCHA
def save_cookies(driver, path):
    with open(path, "wb") as file:
        pickle.dump(driver.get_cookies(), file)

# Cargar cookies para evitar el CAPTCHA en futuras ejecuciones
def load_cookies(driver, path):
    with open(path, "rb") as file:
        cookies = pickle.load(file)
        for cookie in cookies:
            driver.add_cookie(cookie)

# Función para iniciar el proceso con cookies (si las tienes)
def start_with_cookies(driver):
    # Intentar cargar cookies, si no hay archivo o hay error, se continua sin cookies
    try:
        driver.get('https://www.aftership.com')
        load_cookies(driver, COOKIES_PATH)
        driver.get('https://www.aftership.com/brands/page/15?region=PE&sort=rank')
        time.sleep(3)  # Esperar a que las cookies se apliquen
    except Exception as e:
        print(f"Error cargando cookies: {e}")

# Función para extraer datos de la página
def extract_data(driver, csv_writer):
    ecommerce_items = driver.find_elements(By.CSS_SELECTOR,"ol.ais-Hits-list li.ais-Hits-item a")
    
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

# Proceso principal
def main():
    driver = init_driver()

    # Intentar iniciar con cookies guardadas si existen
    start_with_cookies(driver)

    # Crear un archivo CSV para almacenar los datos
    with open('ecommerce_urls_full.csv', 'w', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['Ecommerce Name', 'URL'])
        
        page_number = 217
        
        while True:
            current_url = f"https://www.aftership.com/brands/page/{page_number}?region=PE&sort=rank"
            print(f"Analizando página: {page_number} -> {current_url}")
            
            driver.get(current_url)
            time.sleep(3)  # Esperar a que la página cargue
            
            # Extraer los datos
            has_items = extract_data(driver, csv_writer)
            
            if not has_items:
                print(f"No se encontraron más elementos en la página {page_number}. Fin de la iteración.")
                break  # Terminar si no hay más elementos
            
            page_number += 1

    # Guardar cookies para la próxima vez
    save_cookies(driver, COOKIES_PATH)

    # Cerrar el navegador
    driver.quit()

# Ejecutar el código principal
if __name__ == "__main__":
    main()
