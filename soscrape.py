"""Scrape SO.com scores.

Read SO.com links from the Google Spreadsheet, scrape reputation on the profile page and write value back to the Google Spreadsheet.
"""

import time
import requests
import json
import gspread
from lxml import html
from oauth2client.service_account import ServiceAccountCredentials


#: Column contains SO.com profile link in a format like https://stackoverflow.com/users/4650364/rohit-verma
SO_PROFILE_LINK_COLUMN = "T"

#: The column where we store scraped user repution
SO_SCORE_COLUMN = "I"

#: Which tab 0....n contains our processing data
RESPONSE_TAB = 1

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
row = 449

# How long is our spreadsheet
row_count = wks.row_count

# acell returns empty value when we run over the end of spreadsheet
while row <= row_count:

    # Like AD340
    try:
        input_pointer = f"{SO_PROFILE_LINK_COLUMN}{row}"
        profile_link = wks.acell(input_pointer).value

        # Like AD340
        output_pointer = f"{SO_SCORE_COLUMN}{row}"
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

    if profile_link in ("https://stackoverflow.com", "https://stackoverflow.com/"):
        print("Smart cookie")
        wks.update_acell(output_pointer, "0")
        continue

    if "/companies/" in profile_link:
        print("Somebody submitted a StackOverlow company page", profile_link)
        wks.update_acell(output_pointer, "0")
        continue

    # Transform user story links to SO.com profile links if possible
    if "view=Cv" in profile_link or "story" in profile_link:
        # Normalise https://stackoverflow.com/users/story/12861492?view=Cv
        # https://stackoverflow.com/users/story/5038322
        print("Transforming", profile_link)
        page = requests.get(profile_link)
        tree = html.fromstring(page.content)
        if len(tree.cssselect("a[data-shortcut='P']")) >= 1:
            real_profile_link = "https://stackoverflow.com/" + tree.cssselect("a[data-shortcut='P']")[0].get("href")
        elif len(tree.cssselect(".network-account a")) >= 1:
            # https://stackoverflow.com/story/lucasbadico
            real_profile_link = tree.cssselect(".network-account a")[0].get("href")
        else:
            print("Did not have real user profile")
            wks.update_acell(output_pointer, "0")
            continue

        print("Transformed", profile_link, real_profile_link)
        profile_link = real_profile_link
    elif profile_link.startswith("https://stackoverflow.com/cv/"):
        # Then there is a CV link...
        # https://stackoverflow.com/cv/dougmolina
        page = requests.get(profile_link)
        tree = html.fromstring(page.content)
        print("Transforming", profile_link)
        if len(tree.cssselect("#stackexchange-accounts a")) >= 1:
            real_profile_link = tree.cssselect("#stackexchange-accounts a")[0].get("href")
            print("Transformed", profile_link, real_profile_link)
            profile_link = real_profile_link
        else:
            # No SO.com profile, though has CV. Whyyy???
            # https://stackoverflow.com/cv/pratu
            print("Did not have real user profile")
            wks.update_acell(output_pointer, "0")
            continue

    if not profile_link:
        print("Missing profile", input_pointer)
        continue

    if not profile_link.startswith("https://stackoverflow.com"):
        # User did not complete the form correctly
        print("Bad profile", profile_link)
        wks.update_acell(output_pointer, "0")
        continue

    resp = requests.get(profile_link)
    if resp.status_code != 200:
        # User does not have account, posts a crap link
        print("Bad URL", profile_link)
        reputation = 0
    else:
        tree = html.fromstring(resp.content)
        print("Scraping profile", profile_link, "row", row)
        # Get the CSS selector using DOM inspector in the browser
        reputation = tree.cssselect("div[title='reputation'] .fs-title")[0].text

    print("Got rep", reputation)

    # Use str() to avoid some random date conversions
    wks.update_acell(output_pointer, str(reputation))

