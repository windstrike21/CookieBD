import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException

# Configurar las opciones del navegador
chrome_options = Options()
chrome_options.add_argument("--headless")  # Ejecutar en modo headless (sin GUI)

# Configurar el servicio de ChromeDriver
service = Service('/usr/local/bin/chromedriver')  # Ruta a ChromeDriver

# Función para obtener cookies de un sitio
def obtener_cookies(url):
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Establecer tiempo de espera
    driver.set_page_load_timeout(30)  # Aumentar el tiempo de espera a 30 segundos
    
    try:
        driver.get(url)
        cookies = driver.get_cookies()
    except TimeoutException:
        print(f"TimeoutException: La página {url} tardó demasiado en cargar.")
        cookies = []  # Si falla, devolvemos una lista vacía
    finally:
        driver.quit()

    cookies_list = []
    for cookie in cookies:
        cookie_info = {
            'name': cookie.get('name'),
            'value': cookie.get('value'),
            'domain': cookie.get('domain'),
            'path': cookie.get('path'),
            'expiry': cookie.get('expiry'),
            'httpOnly': cookie.get('httpOnly'),
            'secure': cookie.get('secure'),
            'url': url  # Agregar la URL de donde proviene la cookie
        }
        cookies_list.append(cookie_info)
    
    return cookies_list

# Lista de URLs para visitar
urls = [
    'https://www.falabella.com.pe/falabella-pe/',
    'https://www.wong.pe/',
    'https://linio.falabella.com.pe/linio-pe',
    'https://simple.ripley.com.pe/',
    'https://www.plazavea.com.pe/',
    'https://www.adidas.pe/',
    'https://platanitos.com/',
    'https://www.sodimac.com.pe/sodimac-pe',
    'https://www.promart.pe/',
    'https://www.loginstore.com/'
]

# Recolectar cookies de todas las URLs
cookies_totales = []
for url in urls:
    cookies_totales.extend(obtener_cookies(url))

# Convertir la lista de cookies a un DataFrame y ordenar columnas
cookies_df = pd.DataFrame(cookies_totales)

# Reordenar las columnas (atributos)
columnas_ordenadas = ['name', 'value', 'domain', 'path', 'expiry', 'httpOnly', 'secure', 'url']
cookies_df = cookies_df[columnas_ordenadas]

# Guardar el DataFrame en un archivo CSV
cookies_df.to_csv('cookies_recopiladas_ordenadas.csv', index=False)

print("Cookies recopiladas y guardadas en 'cookies_recopiladas_ordenadas.csv'")
