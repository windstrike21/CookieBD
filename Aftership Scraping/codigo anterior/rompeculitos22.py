from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import csv
import time

# Path to the chromedriver (update with your path)
chrome_driver_path = "/home/user/Escritorio/CookieBD/chromedriver"

# Set up Selenium WebDriver
service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service)

# Open the Aftership website
driver.get("https://www.aftership.com/brands?region=PE&sort=rank")

# Prepare the CSV file
csv_file = open('ecommerce_urls.csv', 'w', newline='', encoding='utf-8')
csv_writer = csv.writer(csv_file)
csv_writer.writerow(['Ecommerce Name', 'URL'])

# Give some time to load the page
time.sleep(3)

# Get all e-commerce links from the list
ecommerce_items = driver.find_elements(By.CSS_SELECTOR, "ol.ais-Hits-list li.ais-Hits-item a")

# Extract the name and href (URL) of each item
for item in ecommerce_items:
    try:
        # Get the e-commerce store name from the 'title' attribute
        ecommerce_name = item.get_attribute('title')
        
        # Get the href (URL) from the 'href' attribute
        ecommerce_url = item.get_attribute('href')
        
        # Print and write to CSV
        print(f'{ecommerce_name}: {ecommerce_url}')
        csv_writer.writerow([ecommerce_name, ecommerce_url])

    except Exception as e:
        print(f"Error: {e}")
        continue

# Close the driver and CSV file
csv_file.close()
driver.quit()

