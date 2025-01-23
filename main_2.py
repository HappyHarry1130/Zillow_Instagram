import logging
from playwright.async_api import async_playwright
from selenium.webdriver.chrome.options import Options  # Import Options
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from fastapi import FastAPI, Query  # 
from fastapi.responses import JSONResponse  
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles 
from PIL import Image, ImageDraw, ImageFont  
from io import BytesIO
import random 

app = FastAPI()  
origins = [
    "http://localhost:3000",  
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

app.mount("/static", StaticFiles(directory="static"), name="static")

def search_zillow(address):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.6834.83 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
        # "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
    ]
    
    # Select a random user-agent
    random_user_agent = random.choice(user_agents)
    chrome_options.add_argument(f"user-agent={random_user_agent}") 
    chrome_options.add_argument("--no-sandbox")  
    chrome_options.add_argument("--disable-dev-shm-usage")  
    chrome_options.add_argument("--disable-gpu")  
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")  
    chrome_options.add_argument("--disable-infobars") 
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-extensions")  
    chrome_options.add_argument("--enable-features=NetworkService,NetworkServiceInProcess") 
    # chrome_options.add_argument('--proxy-server=socks5://sean123:ps123456@156.235.23.114:2340')  # Added proxy server
    # chrome_options.binary_location = "/usr/bin/google-chrome"   

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    base_url = "https://www.zillow.com/homes/"
    search_url = f"{base_url}{address.replace(' ', '-')}_rb/"
    driver.get(search_url)
    time.sleep(15)  
    return driver.page_source

def extract_image_url(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    print(soup)
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

def overlay_text_on_image(image, text, y_pos=780, font_size=20):
    if isinstance(image, str):
        new_image = Image.open(image)  
    else:
        new_image = image.copy()  

    template = Image.open("1.png")
    replacement_area = (113, 190, 980, 730)  

    new_image_resized = new_image.resize((replacement_area[2] - replacement_area[0], 
                                           replacement_area[3] - replacement_area[1]))

    template.paste(new_image_resized, replacement_area)
    draw = ImageDraw.Draw(template)
    
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except IOError:
        font = ImageFont.load_default()
    
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    position = (replacement_area[0] + (replacement_area[2] - replacement_area[0]) // 2 - text_width // 2, y_pos)
    text_color = (5, 255, 100)
    draw.text(position, text, fill=text_color, font=font)

    if template.mode == 'RGBA':
        template = template.convert('RGB')

    return template  

@app.post("/scrape-image")  
async def scrape_image(address: str):  
    try:
        html_content = search_zillow(address)
        image_url = extract_image_url(html_content)
        if image_url:
            download_image(image_url, address)
            new_image = Image.open(f"{address.replace(' ', '_')}.jpg")  
            print('loaded')
            overlayed_image = overlay_text_on_image(new_image, address)  
            

            overlayed_image_path = f"static/{address.replace(' ', '_')}_overlayed.jpg"
            overlayed_image.save(overlayed_image_path)  
            
            downloadable_url = f"/static/{address.replace(' ', '_')}_overlayed.jpg"
            return JSONResponse(content={"message": "Image downloaded and overlayed successfully", "image_url": image_url, "downloadable_url": downloadable_url})
        else:
            return JSONResponse(content={"message": "No image found for the given address"}, status_code=404)
    except Exception as e:
        logging.error(f"Error processing request for address {address}: {str(e)}")  
        return JSONResponse(content={"message": str(e)}, status_code=500)

if __name__ == "__main__":  
    uvicorn.run(app, host="0.0.0.0", port=8000)