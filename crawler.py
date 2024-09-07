# Importar librerias necesarias
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# Configurar las opciones del navegador
chrome_options = Options()
chrome_options.add_argument("--headless")  # Ejecutar en modo headless (sin GUI)

# Configurar el servicio de ChromeDriver
service = Service('/usr/local/bin/chromedriver')  # Ruta a ChromeDriver

# Iniciar el navegador
driver = webdriver.Chrome(service=service, options=chrome_options)

# Navegar a la página web
url = 'https://www.falabella.com.pe/falabella-pe/'  # Cambia esto por la URL de tu interés
driver.get(url)

# Extraer cookies
cookies = driver.get_cookies()

# Crear una lista para almacenar las cookies
cookies_list = []

# Guardar todas las propiedades de las cookies en la lista
for cookie in cookies:
    cookie_info = {
        'name': cookie.get('name'),
        'value': cookie.get('value'),
        'domain': cookie.get('domain'),
        'path': cookie.get('path'),
        'expiry': cookie.get('expiry'),
        'httpOnly': cookie.get('httpOnly'),
        'secure': cookie.get('secure'),
    }
    cookies_list.append(cookie_info)

# Convertir la lista de cookies en un DataFrame
cookies_df = pd
