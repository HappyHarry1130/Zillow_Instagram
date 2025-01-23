import requests

def get_final_url(initial_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    with requests.Session() as session:
        response = session.get(initial_url, headers=headers)
        
        # Check if the response status code is 403
        if response.status_code == 403:
            print("Access forbidden. You may need to check your User-Agent or use a different IP.")
        else:
            print(f"Status Code: {response.status_code}")
        
        return response.url

initial_url = "https://www.zillow.com/homes/15503-SW-T5-Rd,-Beverly,-TX_rb/"
final_url = get_final_url(initial_url)
print(final_url)