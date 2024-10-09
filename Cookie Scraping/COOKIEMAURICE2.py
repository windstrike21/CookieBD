import pandas as pd
import csv
import requests  # Para obtener headers HTTP
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup  # Para analizar contenido HTML
import certifi

# Configuración de Chrome para Ubuntu
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

# Path de ChromeDriver en Ubuntu (ajusta si es necesario)
webdriver_path = '/home/user/Escritorio/CookieBD/chromedriver'

# Leer el archivo Excel con las URLs
df_urls = pd.read_excel('ecommerce_urls_10000.xlsx', sheet_name='Tabla1')

# Función para extraer cookies de una URL y cabeceras HTTP
def extract_cookies_and_headers(url):
    # Crear el servicio con el path del ChromeDriver
    service = Service(webdriver_path)
    
    # Usar Selenium para obtener cookies
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get(url)
    cookies = driver.get_cookies()
    
    # Obtener cabeceras HTTP usando requests, desactivando la verificación SSL
    response = requests.get(url, verify=certifi.where())  # Certifi para gestionar certificados
    headers = response.headers
    
    # Extraer información adicional del HTML
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    meta_tags = soup.find_all('meta')  # Podrías analizar meta-tags de seguridad
    
    driver.quit()
    return cookies, headers, meta_tags

# Crear un archivo CSV para almacenar cookies y otros datos
with open('extracted_cookies_with_headers.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    # Escribir el encabezado del archivo CSV
    writer.writerow(['URL', 'cookie_name', 'cookie_value', 'domain', 'path', 'expiry', 'secure', 'httpOnly', 'sameSite', 'size', 
                     'server', 'HSTS', 'X-Frame-Options', 'CSP', 'meta_tags'])

    # Iterar sobre las URLs y extraer cookies
    for index, row in df_urls.iterrows():
        url = row['URL']
        if pd.notna(url):  # Si hay una URL válida
            cookies, headers, meta_tags = extract_cookies_and_headers(url)
            
            # Obtener cabeceras HTTP relevantes
            server = headers.get('Server', 'No Data')
            hsts = headers.get('Strict-Transport-Security', 'No Data')
            x_frame_options = headers.get('X-Frame-Options', 'No Data')
            csp = headers.get('Content-Security-Policy', 'No Data')
            
            # Escribir cada cookie en el CSV
            for cookie in cookies:
                writer.writerow([
                    url,
                    cookie.get('name'),
                    cookie.get('value'),
                    cookie.get('domain'),
                    cookie.get('path'),
                    cookie.get('expiry'),
                    cookie.get('secure'),
                    cookie.get('httpOnly'),
                    cookie.get('sameSite'),
                    len(str(cookie.get('value'))),  # Tamaño del valor de la cookie
                    server,
                    hsts,
                    x_frame_options,
                    csp,
                    ', '.join([meta.attrs.get('content', 'No Content') for meta in meta_tags if 'content' in meta.attrs])  # Meta tags de la página
                ])

print("Extracción completada. Los datos se guardaron en 'extracted_cookies_with_headers.csv'.")
