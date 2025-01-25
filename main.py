import logging
import os
import json
import random
import asyncio
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from PIL import Image, ImageDraw, ImageFont, UnidentifiedImageError
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async
from bs4 import BeautifulSoup
import requests
from instagrapi import Client
from instagrapi.exceptions import ChallengeRequired, UnknownError
from dotenv import load_dotenv
from pydantic import BaseModel

# FastAPI setup
app = FastAPI()
COOKIE_FILE = Path("cookies.json")
STATIC_DIR = Path("static")
load_dotenv()
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.5615.49 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.5672.127 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.1901.183 Safari/537.36 Edg/115.0.1901.183",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.5672.64 Safari/537.36 Edg/113.0.5672.64",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.1901.183 Safari/537.36 OPR/102.0.4719.43",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 OPR/77.0.4054.172"
]

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://zillow-instagram.vercel.app", "http://45.79.156.12:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ImageUploadRequest(BaseModel):
    image_path: str
    caption: str

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Ensure static directory exists
if not STATIC_DIR.exists():
    STATIC_DIR.mkdir(parents=True)

# Function to fetch Zillow page content
async def fetch_zillow_page(address):
    try:
        async with async_playwright() as p:
            user_agent = random.choice(USER_AGENTS)
            browser = await p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-gpu"])
            context = await browser.new_context(
                user_agent=user_agent,                
                locale="en-US",  
                timezone_id="America/New_York", 
                viewport={"width": 1920, "height": 1080} 
            )

            if COOKIE_FILE.exists():
                with COOKIE_FILE.open("r") as f:
                    cookies = json.load(f)
                await context.add_cookies(cookies)
            else:
                raise RuntimeError("cookies.json file is missing!")

            page = await context.new_page()
            await stealth_async(page)
            search_url = f"https://www.zillow.com/homes/{address.replace(' ', '-')}_rb/"
            logging.info(f"Navigating to: {search_url}")

            random_delay = random.uniform(5, 8)
            print(f"Sleeping for {random_delay:.2f} seconds before navigating...")
            await asyncio.sleep(random_delay)
            
            await page.goto(search_url)

            random_delay = random.uniform(5, 8)
            print(f"Sleeping for {random_delay:.2f} seconds before navigating...")
            await asyncio.sleep(random_delay)
            content = await page.content()
            await browser.close()
            return content
    except Exception as e:
        logging.exception("Failed to fetch Zillow page")
        return None

# Function to extract image URL
def extract_image_url(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    print(soup)
    image_element = soup.select_one('div#search-detail-lightbox div div div section div div:nth-of-type(2) div:nth-of-type(2) div div:nth-of-type(1) div div:nth-of-type(2) li:nth-of-type(1) figure button picture img')
    if image_element:
        logging.info(f"Extracted image URL: {image_element['src']}")
        return image_element['src']
    logging.warning("No image URL found in the page content.")
    return None

# Function to download image
def download_image(image_url, address):
    try:
        response = requests.get(image_url, stream=True)
        if response.status_code == 200 and response.headers.get("Content-Type", "").startswith("image/"):
            image_path = STATIC_DIR / f"{address.replace(' ', '_')}.jpg"
            with open(image_path, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            logging.info(f"Image saved as {image_path}")
            return True
        else:
            logging.error("Failed to download image or invalid content type.")
            return False
    except Exception as e:
        logging.exception(f"Error downloading image: {e}")
        return False

# Function to validate the downloaded image
def validate_image(image_path):
    try:
        with Image.open(image_path) as img:
            img.verify()
        logging.info(f"Image {image_path} is valid.")
        return True
    except UnidentifiedImageError:
        logging.error(f"Downloaded file is not a valid image: {image_path}")
        return False


def overlay_text_on_image(image_path, text, y_pos=780, font_size=50, text_color=(5, 255, 100)):
    new_image = Image.open(image_path)
    template = Image.open("template.png")  
    replacement_area = (113, 190, 980, 730)

 
    new_image_resized = new_image.resize(
        (replacement_area[2] - replacement_area[0], replacement_area[3] - replacement_area[1])
    )
    template.paste(new_image_resized, replacement_area)
    len_text = len(text)
    if len_text >20:
        font_size = 35
    draw = ImageDraw.Draw(template)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
    except IOError:
        print("Font file not found, using default font.")
        font = ImageFont.load_default()

    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = (text_bbox[2] - text_bbox[0] ) *1.22
    position = (replacement_area[0] + (replacement_area[2] - replacement_area[0]) // 2 - text_width // 2, y_pos)


    draw.text(position, text.upper(), fill=text_color, font=font)

    if template.mode == 'RGBA':
        template = template.convert('RGB')

    return template

@app.post("/scrape-image")
async def scrape_image(address: str):
    try:
        if not address.strip():
            return JSONResponse(content={"message": "Invalid address provided"}, status_code=400)

        html_content = await fetch_zillow_page(address)
        if not html_content:
            return JSONResponse(content={"message": "Failed to fetch Zillow page"}, status_code=500)

        image_url = extract_image_url(html_content)
        if image_url:
            if not download_image(image_url, address):
                return JSONResponse(content={"message": "Failed to download image"}, status_code=500)

            image_path = STATIC_DIR / f"{address.replace(' ', '_')}.jpg"
            if validate_image(image_path):
                overlayed_image = overlay_text_on_image(image_path, address)
                overlayed_image_path = STATIC_DIR / f"{address.replace(' ', '_')}_overlayed.jpg"
                overlayed_image.save(overlayed_image_path)

                return JSONResponse(content={
                    "message": "Image downloaded and overlayed successfully",
                    "image_url": image_url,
                    "downloadable_url": f"/static/{address.replace(' ', '_')}_overlayed.jpg"
                })
            else:
                return JSONResponse(content={"message": "Downloaded file is not a valid image"}, status_code=500)
        else:
            return JSONResponse(content={"message": "No image found for the given address"}, status_code=404)
    except Exception as e:
        logging.exception(f"Error processing request for address {address}")
        return JSONResponse(content={"message": "Internal server error"}, status_code=500)
    
async def upload_to_instagram(image_path, caption):
    # cl= Client()
    media = cl.photo_upload_to_story(image_path, caption)
    logging.info(f"Uploaded successfully! Media ID: {media.pk}")
s
@app.post("/upload-image")
async def upload_image(request: ImageUploadRequest):
    try:
        print(request.image_path, request.caption)
        await upload_to_instagram(request.image_path, request.caption)
        return JSONResponse(content={"message": "Image uploaded successfully"}, status_code=200)
    except Exception as e:
        logging.exception("Error uploading image to Instagram")
        return JSONResponse(content={"message": "Failed to upload image"}, status_code=500)

if __name__ == "__main__":
    cl = Client()
    username = os.getenv("INSTAGRAM_USERNAME")
    password = os.getenv("INSTAGRAM_PASSWORD")

    try:
        cl.login(username, password)
    except ChallengeRequired as e:
        # Handle the challenge
        print("A challenge is required. Please check your email for the verification code.")
        verification_code = input("Enter the verification code: ")
        
        # Resolve the challenge
        try:
            cl.challenge_resolve(e.challenge, verification_code)
            cl.login(username, password)  # Retry login after resolving the challenge
        except UnknownError as ue:
            print(f"Unknown error occurred: {ue}")
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
