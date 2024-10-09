from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import csv

# Setup webdriver (make sure to have the correct driver installed for your browser)
chrome_driver_path = "/home/user/Escritorio/CookieBD/chromedriver"
service = Service(executable_path=chrome_driver_path)
driver = webdriver.Chrome(service=service)

# Open the website
driver.get("https://www.aftership.com/brands?region=PE&sort=rank")

# Create a CSV to store data
csv_file = open('ecommerce_urls.csv', 'w', newline='', encoding='utf-8')
csv_writer = csv.writer(csv_file)
csv_writer.writerow(['Ecommerce Name', 'URL'])

# Loop through the first 200 items
for page in range(1, 3):  # Loop through the first 2 pages (you can expand this)
    items = driver.find_elements(By.CSS_SELECTOR, "a[class*='rt-Link']")

    for item in items:
        ecommerce_name = item.get_attribute("title")
        ecommerce_url = item.get_attribute("href")
        print(f"Extracted: {ecommerce_name}, {ecommerce_url}")
        csv_writer.writerow([ecommerce_name, ecommerce_url])
    
    # Go to next page
    next_button = driver.find_element(By.LINK_TEXT, str(page + 1))
    next_button.click()

# Close the driver and CSV file
driver.quit()
csv_file.close()
