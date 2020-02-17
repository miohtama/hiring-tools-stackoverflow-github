"""Scrape SO.com scores.

Read SO.com links from the Google Spreadsheet, scrape reputation on the profile page and write value back to the Google Spreadsheet.



"""

import requests
import json
import gspread
from lxml import html
from oauth2client.service_account import ServiceAccountCredentials

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

#: Column contains SO.com profile link in a format like https://stackoverflow.com/users/4650364/rohit-verma
SO_PROFILE_LINK_COLUMN = "AD"

#: The column where we store scraped user repution
SO_SCORE_COLUMN = "S"

# To dig the reputation on the page
XPATH = "//div[@title='reputation']//*[contains(concat(' ', normalize-space(@class), ' '), ' fs:title ')]/text()"

credentials = ServiceAccountCredentials.from_json_keyfile_name('service-account.json', scope)
# credentials = json.load(open("service-account.json", "rt"))
# 
gc = gspread.authorize(credentials)

file = gc.open("Backend Candidate form responses")
print("Available sheets", file.worksheets())

# Open a worksheet from spreadsheet with one shot
wks = file.get_worksheet(1)

# https://github.com/burnash/gspread
row = 340

# acell returns empty value when we run over the end of spreadsheet
while True:
    
    # Like AD340
    pointer = f"{SO_PROFILE_LINK_COLUMN}{row}"
    print(pointer)
    profile_link = wks.acell(pointer).value

    # Scraping 101 https://docs.python-guide.org/scenarios/scrape/
    page = requests.get(profile_link)
    tree = html.fromstring(page.content)
    reputation = tree.xpath(XPATH)
    print("Profile", profile_link, "rep", reputation)
    row += 1

    if row > 10:
        break

# Fetch a cell range
cell_list = wks.range('A1:B7')