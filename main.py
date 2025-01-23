import logging
from playwright.async_api import async_playwright
import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI
from fastapi.responses import JSONResponse  
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles 
from PIL import Image, ImageDraw, ImageFont  
import random
import asyncio
import json
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async
from bs4 import BeautifulSoup
import requests


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

COOKIE_FILE = "cookies.json"

USER_AGENTS = [
    # Chrome on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.5615.49 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.5672.127 Safari/537.36",
    # Edge on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.1901.183 Safari/537.36 Edg/115.0.1901.183",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.5672.64 Safari/537.36 Edg/113.0.5672.64",
    # Older Chrome (to mimic outdated browsers)
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    # Opera on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.1901.183 Safari/537.36 OPR/102.0.4719.43",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 OPR/77.0.4054.172"
]

app.mount("/static", StaticFiles(directory="static"), name="static")


async def fetch_zillow_page(address):
    try:
        async with async_playwright() as p:
            # Select a random user agent
            user_agent = random.choice(USER_AGENTS)

            # Launch a Chromium browser instance with necessary arguments
            browser = await p.chromium.launch(
                headless=True, 
                args=["--no-sandbox", "--disable-gpu"]
            )
            context = await browser.new_context(
                user_agent=user_agent,  # Set user agent
                locale="en-US",  # Simulate a US-based user
                timezone_id="America/New_York",  # Set timezone
                viewport={"width": 1920, "height": 1080}  # Set viewport size
            )

            # Load cookies from cookies.json
            with open(COOKIE_FILE, "r") as f:
                cookies = json.load(f)
            await context.add_cookies(cookies)

            page = await context.new_page()

            # Enable stealth mode to avoid detection
            await stealth_async(page)

            # Build the search URL
            search_url = f"https://www.zillow.com/homes/{address.replace(' ', '-')}_rb/"
            print(f"Navigating to {search_url} with User-Agent: {user_agent}")

            # Simulate random delay before navigation
            random_delay = random.uniform(5, 8)
            print(f"Sleeping for {random_delay:.2f} seconds before navigating...")
            await asyncio.sleep(random_delay)

            # Navigate to the Zillow page
            await page.goto(search_url)

            # Wait for a random time to mimic human interaction
            random_delay = random.uniform(5, 7)
            print(f"Sleeping for {random_delay:.2f} seconds after loading the page...")
            await page.wait_for_timeout(int(random_delay * 1000))  # Convert seconds to milliseconds

            # Get the HTML content of the page
            content = await page.content()
            print("Page content fetched successfully.")
            await browser.close()
            return content
    except Exception as e:
        print(f"Error occurred: {e}")
        return None

async def scrape_zillow_image(address):
    # Simulate random delay before starting the scrape
    random_delay = random.uniform(5, 7)
    print(f"Sleeping for {random_delay:.2f} seconds before starting scrape...")
    await asyncio.sleep(random_delay)

    # Fetch the page content
    html_content = await fetch_zillow_page(address)
    if html_content:
        # Extract the image URL from the page content
        image_url = extract_image_url(html_content)
        if image_url:
            print(f"Image URL found: {image_url}")
            # Download the image using the extracted URL
            download_image(image_url, address)
        else:
            print("No image found for the given address")
    else:
        print("Failed to fetch the page")

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
        html_content = fetch_zillow_page(address)
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