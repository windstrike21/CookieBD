import pandas as pd
import csv
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException  # Para manejar el timeout
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

# Funci�n para extraer cookies, headers HTTP y otros detalles de seguridad
def extract_cookies_and_headers(url):
    # Crear el servicio con el path del ChromeDriver
    service = Service(webdriver_path)
    
    # Usar Selenium para obtener cookies
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Configurar tiempos de espera
    driver.set_page_load_timeout(page_load_timeout)

    start_time = time.time()  # Tiempo inicial
    cookies = []
    headers = {}
    local_storage, session_storage = "No Data", "No Data"
    is_https = "No"
    response_time = 0

    try:
        driver.get(url)
        cookies = driver.get_cookies()
        response_time = time.time() - start_time  # Tiempo de respuesta
        is_https = "Yes" if url.startswith("https") else "No"
        
        # Obtener el contenido de localStorage y sessionStorage
        local_storage = driver.execute_script("return JSON.stringify(window.localStorage);")
        session_storage = driver.execute_script("return JSON.stringify(window.sessionStorage);")

    except TimeoutException:
        print(f"Timeout: La p�gina {url} no carg� en {page_load_timeout} segundos. Continuando con la siguiente URL.")
    except Exception as e:
        print(f"Error al cargar la p�gina {url}: {e}")
    finally:
        driver.quit()

    # Obtener cabeceras HTTP usando requests
    try:
        response = requests.get(url, verify=False)  # SSL verification disabled
        headers = response.headers
    except requests.exceptions.SSLError:
        print(f"Advertencia: No se pudo verificar el certificado SSL para {url}. Continuando sin SSL.")
    except Exception as e:
        print(f"Error al hacer la solicitud a {url}: {e}")

    return {
        "cookies": cookies,
        "headers": headers,
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
                     'server', 'HSTS', 'X-Frame-Options', 'CSP', 'server_ip', 'HTTPS', 
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
                    data['server_ip'],
                    data['is_https'],
                    data['response_time'],
                    data['local_storage'],
                    data['session_storage']
                ])

print("Extracci�n completada. Los datos se guardaron en 'extracted_cookies_with_headers.csv'.")
