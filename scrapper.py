import logging
from playwright.async_api import async_playwright
import asyncio
import random
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

chrome_options = Options()
# chrome_options.add_argument("--headless")
driver = webdriver.Chrome(options=chrome_options)

def search_zillow(address):
    base_url = "https://www.zillow.com/homes/"
    search_url = f"{base_url}{address.replace(' ', '-')}_rb/"
    driver.get(search_url)
    time.sleep(5)  # Wait for the page to load
    return driver.page_source

def extract_image_url(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    image_element = soup.select_one('div#search-detail-lightbox div div div section div div:nth-of-type(2) div:nth-of-type(2) div div:nth-of-type(1) div div:nth-of-type(2) li:nth-of-type(1) figure button picture img')
    if image_element:
        return image_element['src']
    return None

def download_image(image_url, address):
    response = requests.get(image_url)
    if response.status_code == 200:
        filename = f"{address.replace(' ', '_')}.jpg"
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"Image saved as {filename}")
    else:
        print("Failed to download image")

def scrape_zillow_image(address):
    html_content = search_zillow(address)
    image_url = extract_image_url(html_content)
    if image_url:
        download_image(image_url, address)
    else:
        print("No image found for the given address")
    driver.quit()



address = "15503 SW T5 Rd, Beverly, WA"
scrape_zillow_image(address)
