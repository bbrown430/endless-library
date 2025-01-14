# endless-library

endless-library is a tool to easily download and send books to a Kindle, featuring a search menu, Goodreads list imports, and an intuitive CLI menu.

## Features

- Download (and send) books from Goodreads link
    - Profile lists such as 'Want to Read', 'Read' (e.g. https://www.goodreads.com/review/list/12345678?shelf=to-read)
        - **NOTE: Account must be public**
    - Listopia lists (e.g. https://www.goodreads.com/list/show/1.Best_Books_Ever)
    - Book series (e.g. https://www.goodreads.com/series/73758-the-hunger-games)
- Download (and send) books by searching
 
## Installation
1. Extract all files into a folder (can delete the .gitignore)
2. Open a terminal in the folder
3. Install the required dependencies using
```bash
pip install -r requirements.txt
```
4. Rename `example_config.json` to `config.json`, and populate with the proper information
   - "mode"
        - "download" to only download books
           - **NOTE: if using "download" mode, you do not need to configure the email settings**
        - "kindle" to download books, and email to Kindle
   - "email_sender"
        - the email address being used to send the emails
        - **NOTE: this email address must be under your [approved email addresses](https://www.amazon.com/gp/help/customer/display.html?nodeId=GX9XLEVV8G4DB28H)**
   - "email_receiver"
        - the email address of the Kindle device you want to send e-books to
        - **NOTE: this email address can be found [here](https://www.amazon.com/sendtokindle/email)**
    - "email_password"
        - the app password of the Gmail account under "email_sender"
        - **NOTE: an app password can be generated [here](https://support.google.com/accounts/answer/185833?hl=en)** 

## Usage

Run `endless-library.py` by double clicking, or by opening a terminal in the root folder and typing

```bash
python endless-library.py
```

## Screenshots
<img src="https://i.ibb.co/rfy3KC3/Screenshot-2024-01-01-213351.png" alt="cli screenshot" width="540"/>


## Known Issues / Shortcomings
- Some .epub files will be rejected when sent to Kindle. I haven't determined what causes some .epubs to be unsupported, but when an error occurs, you will receive an email titled "There was a problem with the document(s) you sent to Kindle." This is not a shortcoming of this program, rather, the Kindle's .epub processing. 
- Email sending only supports Gmail accounts.

## Future Features
- Email support outside of Gmail accounts.
- Documented testing
