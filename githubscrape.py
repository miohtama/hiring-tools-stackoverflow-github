"""Scrape Github.com repo counts.

Read Github profle links from the Google Spreadsheet, use Github API to pull out the repo count of the user and write value back to the Google Spreadsheet.
"""

import os
import requests
import time
import requests
import json
import gspread
from urllib.parse import urlparse
from lxml import html
from oauth2client.service_account import ServiceAccountCredentials


#: Column contains SO.com profile link in a format like https://stackoverflow.com/users/4650364/rohit-verma
PROFILE_LINK_COLUMN = "N"

#: The column where we store scraped user repution
REPO_COUNT_SCORE_COLUMN = "D"

#: Which tab 0....n contains our processing data
RESPONSE_TAB = 1

#: Read these settings from environment variables
github_username = os.environ["GITHUB_USERNAME"]
github_token = os.environ["GITHUB_TOKEN"]

# Get the spreadsheet open for our service account in readwrite mode
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name('service-account.json', scope)
gc = gspread.authorize(credentials)

# Find out survey spreadsheet
file = gc.open("Full stack candidate form (Responses)")
print("Available sheets", file.worksheets())  # What tabs we have on file

# Open a worksheet from spreadsheet with one shot
wks = file.get_worksheet(RESPONSE_TAB)

# We start at row 2
row = 2

# How long is our spreadsheet
row_count = wks.row_count

# USE HTTP 1.1 keep-alive with Requests lib for some more speed
session = requests.Session()
session.auth = (github_username, github_token)

# acell returns empty value when we run over the end of spreadsheet
while row <= row_count:

    # Like AD340
    try:
        input_pointer = f"{PROFILE_LINK_COLUMN}{row}"
        profile_link = wks.acell(input_pointer).value

        # Like AD340
        output_pointer = f"{REPO_COUNT_SCORE_COLUMN}{row}"
        existing_value = wks.acell(output_pointer).value
    except gspread.exceptions.APIError as e:
        # gspread.exceptions.APIError: {'code': 429, 'message': "Quota exceeded for quota group 'ReadGroup' and limit 'Read requests per user per 100 seconds' of service 'sheets.googleapis.com' for consumer 'project_number:'.", 'status': 'RESOURCE_EXHAUSTED', 'details': [{'@type': 'type.googleapis.com/google.rpc.Help', 'links': [{'description': 'Google developer console API key', 'url': 'https://console.developers.google.com/project/15247561015/apiui/credential'}]}]}
        if e.response.status_code == 429:
            print("Waiting, let's not overload Google")
            time.sleep(30)
            continue
        else:
            raise

    row += 1

    # Don't scape
    if existing_value:
        print(output_pointer, "has already value", existing_value)
        continue

    if profile_link == "https://github.com":
        print("Smart cookie")
        wks.update_acell(output_pointer, 0)
        continue

    parsed = urlparse(profile_link)

    # "https://api.github.com/users/" + "miohtama", "/public_repos"
    profile_name = parsed.path.rstrip("/").split("/")[-1]
    print('Scraping repo data for Github user', profile_name)
    endpoint = f"https://api.github.com/users/{profile_name}"
    data = session.get(endpoint).json()

    repos = data["public_repos"]

    print("Got repos", repos)

    # For some reason Google Spreadsheet thinks the number is a date if we not stringify it first
    wks.update_acell(output_pointer, str(repos))

