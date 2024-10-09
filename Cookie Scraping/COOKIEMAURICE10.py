import pandas as pd
import csv
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException  # Para manejar el timeout
import time

# Configuraci�n de Chrome para Ubuntu
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

# Path de ChromeDriver en Ubuntu (ajusta si es necesario)
webdriver_path = '/home/user/Escritorio/CookieBD/chromedriver'

# Reducir el tiempo de espera de carga de la p�gina
page_load_timeout = 10  # Reducido a 10 segundos para que sea m�s r�pido

# Leer el archivo Excel con las URLs (sin prefijos)
df_urls = pd.read_excel('ecommerce_urls_10000.xlsx', sheet_name='Tabla1')

# Solicitar al usuario desde qu� fila empezar
start_row = int(input("Ingrese el n�mero de fila desde donde desea empezar: "))

# Funci�n para intentar cargar la URL con https:// y https://www.
def attempt_load_url(driver, base_url):
    urls_to_try = [f"https://{base_url}", f"https://www.{base_url}"]

    for url in urls_to_try:
        try:
            print(f"Intentando cargar la URL: {url}")
            driver.get(url)  # Intentar cargar la URL
            return url  # Si se carga correctamente, devolver la URL que funcion�
        except TimeoutException:
            print(f"Timeout: La URL {url} no funcion�, intentando la siguiente.")
        except Exception as e:
            print(f"Error al cargar la p�gina {url}: {e}")
    
    return None  # Si ninguna URL funciona, devolver None

# Funci�n para extraer cookies, headers HTTP y otros detalles de seguridad
def extract_cookies_and_headers(base_url):
    # Crear el servicio con el path del ChromeDriver
    service = Service(webdriver_path)
    
    # Usar Selenium para obtener cookies
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Configurar tiempos de espera
    driver.set_page_load_timeout(page_load_timeout)

    cookies = []
    headers = {}
    is_https = "No"
    final_url = None

    try:
        # Intentar cargar la URL con o sin 'www.'
        final_url = attempt_load_url(driver, base_url)
        if final_url is not None:
            is_https = "Yes" if final_url.startswith("https") else "No"
            cookies = driver.get_cookies()  # Obtener las cookies
        else:
            print(f"Ninguna versi�n de la URL {base_url} carg� correctamente.")

    except Exception as e:
        print(f"Error al cargar la p�gina {base_url}: {e}")
    finally:
        driver.quit()

    if final_url is not None:
        # Obtener cabeceras HTTP usando requests si la URL carg� correctamente
        try:
            response = requests.get(final_url, verify=False)  # SSL verification disabled
            headers = response.headers
        except requests.exceptions.SSLError:
            print(f"Advertencia: No se pudo verificar el certificado SSL para {final_url}. Continuando sin SSL.")
        except Exception as e:
            print(f"Error al hacer la solicitud a {final_url}: {e}")

    return {
        "cookies": cookies,
        "headers": headers,
        "is_https": is_https
    }

# Crear un archivo CSV para almacenar cookies y otros datos
with open('extracted_cookies_with_headers.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    # Escribir el encabezado del archivo CSV
    writer.writerow(['URL', 'cookie_name', 'cookie_value', 'domain', 'path', 'expiry', 'secure', 'httpOnly', 'sameSite', 'size', 
                     'server', 'HSTS', 'X-Frame-Options', 'CSP', 'HTTPS'])

    # Iterar sobre las URLs base y extraer cookies, empezando desde la fila especificada
    for index, row in df_urls.iterrows():
        if index >= start_row:  # Empezar desde la fila indicada por el usuario
            base_url = row['URL']
            if pd.notna(base_url):  # Si hay una URL v�lida
                data = extract_cookies_and_headers(base_url)
                
                # Obtener cabeceras HTTP relevantes
                headers = data['headers']
                server = headers.get('Server', 'No Data')
                hsts = headers.get('Strict-Transport-Security', 'No Data')
                x_frame_options = headers.get('X-Frame-Options', 'No Data')
                csp = headers.get('Content-Security-Policy', 'No Data')
                
                # Escribir cada cookie en el CSV
                for cookie in data['cookies']:
                    writer.writerow([
                        base_url,
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
                        data['is_https']
                    ])

print("Extracci�n completada. Los datos se guardaron en 'extracted_cookies_with_headers.csv'.")
