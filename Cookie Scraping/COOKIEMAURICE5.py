import pandas as pd
import csv
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import socket
import ssl

# Configuraci�n de Chrome para Ubuntu
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

# Path de ChromeDriver en Ubuntu (ajusta si es necesario)
webdriver_path = '/home/user/Escritorio/CookieBD/chromedriver'

# Aumentar el tiempo de espera de carga de la p�gina
page_load_timeout = 60  # 60 segundos

# Leer el archivo Excel con las URLs
df_urls = pd.read_excel('ecommerce_urls_10000.xlsx', sheet_name='Tabla1')

# Funci�n para obtener la IP del servidor de una URL
def get_server_ip(url):
    try:
        domain = url.split('/')[2]
        return socket.gethostbyname(domain)
    except Exception as e:
        print(f"Error al obtener la IP del servidor para {url}: {e}")
        return "No Data"

# Funci�n para obtener detalles del certificado SSL
def get_ssl_certificate_details(url):
    try:
        domain = url.split('/')[2]
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443)) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                issuer = cert.get('issuer')
                not_after = cert.get('notAfter')
                return issuer, not_after
    except Exception as e:
        print(f"Error al obtener el certificado SSL para {url}: {e}")
        return "No Data", "No Data"

# Funci�n para extraer cookies, headers HTTP y otros detalles de seguridad
def extract_cookies_and_headers(url):
    # Crear el servicio con el path del ChromeDriver
    service = Service(webdriver_path)
    
    # Usar Selenium para obtener cookies
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Configurar tiempos de espera
    driver.set_page_load_timeout(page_load_timeout)

    start_time = time.time()  # Tiempo inicial
    try:
        driver.get(url)
        cookies = driver.get_cookies()
    except Exception as e:
        print(f"Error al cargar la p�gina {url}: {e}")
        cookies = []
    response_time = time.time() - start_time  # Tiempo de respuesta

    # Obtener cabeceras HTTP usando requests
    try:
        response = requests.get(url, verify=False)  # SSL verification disabled
        headers = response.headers
    except requests.exceptions.SSLError:
        print(f"Advertencia: No se pudo verificar el certificado SSL para {url}. Continuando sin SSL.")
        headers = {}
    except Exception as e:
        print(f"Error al hacer la solicitud a {url}: {e}")
        headers = {}

    # Extraer informaci�n adicional del HTML
    try:
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        meta_tags = soup.find_all('meta')  # Analizar meta-tags
    except Exception as e:
        print(f"Error al analizar el HTML de {url}: {e}")
        meta_tags = []

    # Obtener detalles del certificado SSL
    ssl_issuer, ssl_expiry = get_ssl_certificate_details(url)

    # Verificar si la p�gina usa HTTPS
    is_https = "Yes" if url.startswith("https") else "No"

    # Obtener el contenido de localStorage y sessionStorage
    try:
        local_storage = driver.execute_script("return JSON.stringify(window.localStorage);")
        session_storage = driver.execute_script("return JSON.stringify(window.sessionStorage);")
    except Exception as e:
        print(f"Error al obtener localStorage o sessionStorage en {url}: {e}")
        local_storage, session_storage = "No Data", "No Data"

    # Cerrar el navegador
    driver.quit()

    return {
        "cookies": cookies,
        "headers": headers,
        "meta_tags": meta_tags,
        "ssl_issuer": ssl_issuer,
        "ssl_expiry": ssl_expiry,
        "response_time": response_time,
        "is_https": is_https,
        "local_storage": local_storage,
        "session_storage": session_storage,
        "server_ip": get_server_ip(url)
    }

# Crear un archivo CSV para almacenar cookies y otros datos
with open('extracted_cookies_with_headers.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    # Escribir el encabezado del archivo CSV
    writer.writerow(['URL', 'cookie_name', 'cookie_value', 'domain', 'path', 'expiry', 'secure', 'httpOnly', 'sameSite', 'size', 
                     'server', 'HSTS', 'X-Frame-Options', 'CSP', 'meta_tags', 'server_ip', 'SSL_Issuer', 'SSL_Expiry', 'HTTPS', 
                     'Response_Time', 'localStorage', 'sessionStorage'])

    # Iterar sobre las URLs y extraer cookies
    for index, row in df_urls.iterrows():
        url = row['URL']
        if pd.notna(url):  # Si hay una URL v�lida
            data = extract_cookies_and_headers(url)
            
            # Obtener cabeceras HTTP relevantes
            headers = data['headers']
            server = headers.get('Server', 'No Data')
            hsts = headers.get('Strict-Transport-Security', 'No Data')
            x_frame_options = headers.get('X-Frame-Options', 'No Data')
            csp = headers.get('Content-Security-Policy', 'No Data')
            
            # Escribir cada cookie en el CSV
            for cookie in data['cookies']:
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
                    len(str(cookie.get('value'))),  # Tama�o del valor de la cookie
                    server,
                    hsts,
                    x_frame_options,
                    csp,
                    ', '.join([meta.attrs.get('content', 'No Content') for meta in data['meta_tags'] if 'content' in meta.attrs]),  # Meta tags
                    data['server_ip'],
                    data['ssl_issuer'],
                    data['ssl_expiry'],
                    data['is_https'],
                    data['response_time'],
                    data['local_storage'],
                    data['session_storage']
                ])

print("Extracci�n completada. Los datos se guardaron en 'extracted_cookies_with_headers.csv'.")
