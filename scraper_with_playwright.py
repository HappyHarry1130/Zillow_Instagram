import asyncio
import random
import json
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async
from bs4 import BeautifulSoup
import requests

# List of user agents to rotate
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

COOKIE_FILE = "cookies.json"  # Path to your cookies.json file

async def fetch_zillow_page(address):
    try:
        async with async_playwright() as p:
            # Select a random user agent
            user_agent = random.choice(USER_AGENTS)

            # Launch a Chromium browser instance with necessary arguments
            browser = await p.chromium.launch(
                # headless=True, 
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


def extract_image_url(html_content):
    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    print("Parsing HTML content...", soup)
    # Find the first image element
    image_element = soup.select_one('div#search-detail-lightbox div div div section div div:nth-of-type(2) div:nth-of-type(2) div div:nth-of-type(1) div div:nth-of-type(2) li:nth-of-type(1) figure button picture img')
    if image_element:
        return image_element['src']
    return None


def download_image(image_url, address):
    try:
        response = requests.get(image_url)
        if response.status_code == 200:
            # Save the image to the current directory
            filename = f"{address.replace(' ', '_')}.jpg"
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"Image saved as {filename}")
        else:
            print("Failed to download image")
    except Exception as e:
        print(f"Error downloading image: {e}")


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


# Test function to run locally
def test_scrape_zillow():
    address = "15503 SW T5 Rd, Beverly, WA"  # Replace with your test address
    asyncio.run(scrape_zillow_image(address))


if __name__ == "__main__":
    test_scrape_zillow()
