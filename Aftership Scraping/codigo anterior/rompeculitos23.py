from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import csv
import time

# Path to the chromedriver (modificar con tu ruta)
chrome_driver_path = '/home/user/Escritorio/CookieBD/chromedriver'

# Set up Selenium WebDriver
service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service)

# Crear un archivo CSV para almacenar los datos
csv_file = open('ecommerce_urls_full.csv', 'w', newline='', encoding='utf-8')
csv_writer = csv.writer(csv_file)
csv_writer.writerow(['Ecommerce Name', 'URL'])

# Tiempo para que cargue la página
time.sleep(3)

# Función para extraer los elementos de una página
def extract_data():
    # Encontrar todos los links de las tiendas de la página actual
    ecommerce_items = driver.find_elements(By.CSS_SELECTOR, "ol.ais-Hits-list li.ais-Hits-item a")

    # Extraer el nombre de la tienda y la URL de cada uno
    for item in ecommerce_items:
        try:
            ecommerce_name = item.get_attribute('title')  # Nombre del ecommerce
            ecommerce_url = item.get_attribute('href')  # URL del ecommerce

            # Imprimir en consola y escribir en el archivo CSV
            print(f'{ecommerce_name}: {ecommerce_url}')
            csv_writer.writerow([ecommerce_name, ecommerce_url])
        
        except Exception as e:
            print(f"Error: {e}")
            continue

# Bucle para recorrer todas las páginas incrementando el número
page_number = 147
while True:
    # Generar la URL con el número de página actual
    current_url = f"https://www.aftership.com/brands/page/{page_number}?region=PE&sort=rank"
    print(f"Analizando página: {page_number} -> {current_url}")
    
    # Abrir la página
    driver.get(current_url)
    time.sleep(3)  # Esperar para que la página cargue completamente
    
    # Extraer datos de la página actual
    extract_data()

    # Verificar si hay más elementos en la página
    ecommerce_items = driver.find_elements(By.CSS_SELECTOR, "ol.ais-Hits-list li.ais-Hits-item a")
    
    if not ecommerce_items:
        print(f"No se encontraron más elementos en la página {page_number}. Fin de la iteración.")
        break  # Salir del bucle si no hay más elementos

    # Incrementar el número de página para pasar a la siguiente
    page_number += 1

# Cerrar el archivo CSV y el navegador
csv_file.close()
driver.quit()
