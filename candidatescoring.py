"""Score candidates in the spreadsheet based on our formula.

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
row = 50

# How long is our spreadsheet
row_count = wks.row_count


def one_point_if_not_empty(x):
  if x.strip():
    return 1
  else:
    return 0


def calculate_checkbox_match_likeness(value):
  """Used to determinate likeness with the tech stack.

  E.g.

    Node.js, PostgreSQL, Redis, MongoDB, Websockets, Docker, Amazon Web Services, Bash/UNIX scripting
    -> likeness=9, score=2

    Node.js, Docker
    -> likeness=1, score=0
  """

  # Google spreadsheet separates values by command
  return len(value.split(","))

def score_by_checkbox_matches(thresholds):
  """Give a different amount of points to the candidate how many checkboxes matches on the form"""

  def _inner(value):
    likeness = calculate_checkbox_match_likeness(value)

    for threshold, score in thresholds:
      if likeness => threshold:
        return score
    return 0

  return _inner


def score_by_value_threshold(thresholds):
  """Give a different amount of points if the candidates number value exceeds a threshold level"""

  def _inner(value):
    value = int(value)

    for threshold, score in thresholds:
      if value => threshold:
        return score
    return 0

  return _inner

# Scoring formula for TypeScript full stack candidates
scoring = {

  # Has homepage
  "Homepage / portfolio / blog / Twitter / link": one_point_if_not_empty,

  # Has worked with hacker programming languages
  "Have you worked with any of the following programming languages?": one_point_if_not_empty,

  # Have you managed application deployments with any of the following technologies?
  "Have you managed application deployments with any of the following technologies?": score_by_checkbox_matches([(8, 2). (4, 1)]),

  "List of open source projects you have contributed in": one_point_if_not_empty,

  # Github repo count is proxy for opensource contributions - max 2 points
  "Github repo count": score_by_value_threshold([(50, 2), (10, 1)]),

  # StackOverflow rep is proxy for good communicator and helpful problem solver - max 2 points
  "StackOverflow rep": score_by_value_threshold([(500, 2), (20, 1)]),
}


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

    print("Parsed", parsed.hostname, parsed.path)
    if parsed.hostname == "gist.github.com":
      # Somebody made a link to some of his gist
      profile_name = parsed.path.rstrip("/").split("/")[-2]
    else:
      profile_name = parsed.path.rstrip("/").split("/")[-1]


    print('Scraping repo data for Github user', profile_name)
    endpoint = f"https://api.github.com/users/{profile_name}"
    data = session.get(endpoint).json()

    repos = data["public_repos"]

    print("Row", row, "got repos", repos)

    # For some reason Google Spreadsheet thinks the number is a date if we not stringify it first
    wks.update_acell(output_pointer, str(repos))

