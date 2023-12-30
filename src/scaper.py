import requests
from bs4 import BeautifulSoup
import time

class Scraper:
    # returns HTML from a website into a parseable format
    def cook_soup(self, url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        error_count = 0
        while True:
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                return soup
            elif response.status_code == 500:
                error_count += 1
                print("Internal Server Error! Retrying in 2 seconds...")
                time.sleep(2)
            elif response.status_code == 429:
                error_count += 1
                print("Moving too fast! Retrying in 10 seconds...")
                time.sleep(10)
            else:
                error_count += 1
                print(f"Failed to retrieve the page. Status code: {response.status_code}")
                time.sleep(1)

            if error_count == 5:
                raise Exception("Failed to retrieve the page after 5 attempts")
    
    def scrape(self):
        raise NotImplementedError("Subclasses must implement the scrape method")
