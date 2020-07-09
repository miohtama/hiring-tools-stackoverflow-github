"""Score candidates and store the results in the spreadsheet based on our scorecard formula.
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
from scorecard import Scorer

#: Which tab 0....n contains our processing data
RESPONSE_TAB = 1

SCORE_COLUMN = "H"

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
row = 447

# How long is our spreadsheet
row_count = wks.row_count

scorer = Scorer()

headers = wks.row_values(1)

# acell returns empty value when we run over the end of spreadsheet
while row <= row_count:

    # Like AD340
    try:
        row_data = wks.row_values(row)

        # Like AD340
        output_pointer = f"{SCORE_COLUMN}{row}"
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

    # Make a header -> value dictionary out of line we read from Google sheet
    line = dict(zip(headers, row_data))

    tags = scorer.get_tags_for_candidate(line)
    candidate_scoring = scorer.score_candidate(line, tags)
    score = sum(candidate_scoring.values())

    # Use str() to avoid some random date conversions
    print("Updating row", row, "candidate", line["Your name"], "score", score)
    wks.update_acell(output_pointer, str(score))


print("Done, score summaries for this batch")
scorer.print_scores()