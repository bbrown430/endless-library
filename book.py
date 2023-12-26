from bs4 import BeautifulSoup  

class Book:
    def __init__(self, book_html):
        self.title = None
        self.md5 = None
        self.author = None
        self.language = None
        self.size = None
        self.filename = None
        self.filepath = None
        self.parse_html(book_html)
        
    def parse_html(self, book_html):
        self.title = book_html.find('h3').string
        link = book_html.find('a')["href"]
        self.md5 = link.split("/")[2]
        self.author = book_html.find("div", class_="max-lg:line-clamp-[2] lg:truncate leading-[1.2] lg:leading-[1.35] max-lg:text-sm italic").string
        metadata = book_html.find("div", class_="line-clamp-[2] leading-[1.2] text-[10px] lg:text-xs text-gray-500").string
        split_metadata = metadata.split(",")
        self.language = split_metadata[0]
        self.size = split_metadata[2]
        self.filename = split_metadata[3]
    
    def print_metadata(self):
        return f"{self.title} / {self.author} / {self.language} / {self.size}"