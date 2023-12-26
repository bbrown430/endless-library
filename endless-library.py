import requests
import sys
import os.path
import json
from bs4 import BeautifulSoup  

def cook_soup(url):  
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup
    else:
        sys.exit(f"Failed to retrieve the page. Status code: {response.status_code}")

        
def search_query(search_term):
    #TODO only epub for now
    base_url = "https://annas-archive.org/search?index=&q="
    formatted_search = search_term.replace(" ", "+")
    url_ending = "&ext=epub&sort="
    full_url = base_url + formatted_search + url_ending
    
    return full_url


def scrape_book_list(search_term):
    url = search_query(search_term)
    
    soup = cook_soup(url)
    
    books = soup.find_all('div', class_="h-[125] flex flex-col justify-center")
    
    #TODO add validation of book found
    """for book in books:
        title = book.find('h3').string
        link = book.find('a')["href"]
        full_link = "https://annas-archive.org" + link"""
    
    book = books[0]
    title = book.find('h3').string
    link = book.find('a')["href"]
    
    return link

def get_download_link(url):
    base_url = "https://libgen.li/ads.php?md5="
    
    tag = url.split("/")[2]
    
    full_link = base_url + tag
    print(full_link)
    
    soup = cook_soup(full_link)
    link_container = soup.find("td", {"bgcolor": "#A9F5BC"})
    download_link = link_container.find("a")["href"]
    
    print(download_link)

""""
def scrape_book(url):
    soup = cook_soup(url)

    download_div = soup.find("div", {"id": "md5-panel-downloads"})
    
    link_lists = download_div.find_all("ul")
    
    free_links = link_lists[1]
    
    print("test")
"""

def scrape_posters(url):
    movieposters = []
    showposters = []
    
    if ("theposterdb.com" in url) and ("set" in url):
        soup = cook_soup(url)
    else:
        sys.exit("Poster set not found. Check the link you are inputting.")
    
    # find the poster grid
    poster_div = soup.find('div', class_='row d-flex flex-wrap m-0 w-100 mx-n1 mt-n1')

    # find all poster divs
    posters = poster_div.find_all('div', class_='col-6 col-lg-2 p-1')

    # loop through the poster divs
    for poster in posters:
        # get if poster is for a show or movie
        media_type = poster.find('a', class_="text-white", attrs={'data-toggle': 'tooltip', 'data-placement': 'top'})['title']
        # get high resolution poster image
        overlay_div = poster.find('div', class_='overlay')
        poster_id = overlay_div.get('data-poster-id')
        poster_url = "https://theposterdb.com/api/assets/" + poster_id
        # get metadata
        title_p = poster.find('p', class_='p-0 mb-1 text-break').string

        if media_type == "Show":
            title = title_p.split(" (")[0]                   
            if " - " in title_p:
                split_season = title_p.split(" - ")[1]
            else:
                split_season = "Cover"
            
            showposter = {}
            showposter["title"] = title
            showposter["url"] = poster_url
            showposter["season"] = split_season
            showposters.append(showposter)

        if media_type == "Movie":
            title_split = title_p.split(" (")
            if len(title_split[1]) != 5:
                title = title_split[0] + " (" + title_split[1]
            else:
                title = title_split[0]
            year = title_split[-1].split(")")[0]
                
            movieposter = {}
            movieposter["title"] = title
            movieposter["url"] = poster_url
            movieposter["year"] = int(year)
            movieposters.append(movieposter)
    
    return movieposters, showposters


if __name__ == "__main__":
    search_term = "the winners fredrik"
    book_url = scrape_book_list(search_term)
    book = get_download_link(book_url)
    
    