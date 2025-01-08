import argparse
import os
import re
import sys

from src.io_utils import IOUtils

class Book:
    def __init__(self, filepath):
        restricted_characters = r'[\/:*?"<>|]'
        filename_formatted =  re.sub(restricted_characters, '', os.path.basename(filepath))[:123].replace('.epub', '')
        self.title = filename_formatted
        self.attachment_name = filename_formatted + ".epub"
        self.filepath = filepath

def main():
    parser = argparse.ArgumentParser(description='Send book to Kindle')
    parser.add_argument('file', type=str, help='File to send')
    args = parser.parse_args()
    if not args.file.endswith('.epub'):
        print('File must be an EPUB')
        sys.exit(1)
    book = Book(args.file)
    IOUtils().send_email(book)

if __name__ == '__main__':
    main()
