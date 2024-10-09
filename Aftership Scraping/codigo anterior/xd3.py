import os
import undetected_chromedriver as uc
import time
import csv
import pickle
from selenium.webdriver.common.by import By

# Ruta donde guardaremos y cargaremos las cookies
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
    if os.path.exists(path):
        with open(path, "rb") as file:
            cookies = pickle.load(file)
            for cookie in cookies:
                driver.add_cookie(cookie)
    else:
        print(f"Archivo de cookies no encontrado: {path}")

# Función para iniciar el proceso con cookies (si las tienes)
def start_with_cookies(driver):
    # Intentar cargar cookies, si no hay archivo o hay error, se continua sin cookies
    driver.get('https://www.aftership.com')
    load_cookies(driver, COOKIES_PATH)
    driver.get('https://www.aftership.com/brands/page/15?region=PE&sort=rank')
    time.sleep(3)  # Esperar a que las cookies se apliquen

# Función para extraer datos de la página
def extract_data(driver, csv_writer):
    ecommerce_items = driver.find_elements(By.CSS_SELECTOR, "ol.ais-Hits-list li
