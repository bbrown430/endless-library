import re

class Book:
    def __init__(self, book_html, website):
        self.parse_html(book_html, website)
    
    def filepath_prep(self, title):
        restricted_characters = r'[\/:*?"<>|]'
        if title is None:
            title = "no_title"
        if ":" in title:
            split_title = title.split(":")
            title = split_title[0]
        self.title = re.sub(restricted_characters, '', title)
        self.filename = self.title + ".epub"
        self.filepath = "downloads/" + self.filename
    
    # parses html to determine book metadata    
    def parse_html(self, book_html, website):
        if website == "anna":
            title = book_html.find('h3').string
            link = book_html.find('a')["href"]
            self.md5 = link.split("/")[2]
            self.author = book_html.find("div", class_="max-lg:line-clamp-[2] lg:truncate leading-[1.2] lg:leading-[1.35] max-lg:text-sm italic").string
            metadata = book_html.find("div", class_="line-clamp-[2] leading-[1.2] text-[10px] lg:text-xs text-gray-500").string
            split_metadata = metadata.split(",")
            self.language = split_metadata[0]
            self.size = split_metadata[2].strip()
            self.genre = split_metadata[3].split("(")[1].split(")")[0]
        if website == "profile":
            title = book_html.select_one('td.field.title a[title]').text.strip()
            if "\n" in title:
                split_title = title.split("\n")
                title = split_title[0]
            author = book_html.select_one('td.field.author a[href]').text
        if website == "listopia":
            title = book_html.find('span', {'itemprop': 'name'}).text
            author = book_html.find('span', {'itemprop': 'author'}).text
            filtered_author = author.replace("\n", "")
            author = filtered_author
            if "(" in title:
                split_title = title.split(" (")[0]
                title = split_title
            if "(" in author:
                split_author = filtered_author.split(" (")[0]
                author = split_author
        if " Jr." in author:
            temp_author = author.replace(" Jr.", "")
            author = temp_author
        self.author = author
        
        self.filepath_prep(title)

    def update_metadata(self, abs_book):
        title = abs_book.title
        self.author = abs_book.author
        self.filepath_prep(title)

    
    # returns a string fomatted "'book' by 'author'"
    def string(self):
        return f"{self.title} by {self.author}"