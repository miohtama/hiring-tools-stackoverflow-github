# Preface

Here are scripts that I use to rank software developer candidates.

* The scripts communicate with Google Spreadsheet using [the spreadsheet API](https://github.com/burnash/gspread)

* All candidates have inputted their data, including StackOverflow and Github profile links in Google Spreadsheets

* These scripts will go through the candidate data and query SO and GH APIs for more candidate information

* The results are stored back in the Google spreadsheet result column

* Currently the scripts scrape **Stackoverflow Reputation** and **Github repository count**

* A scorecard script will rank all candidates based by [the given scorecard formula]()

# Normalising human input

The scripts will handle various cases of different inputs that we get from candidates on Google Forms.

## Normalising StackOverflow profile links

User give links to their StackOverflow.com profiles. The challenge is the following

* Some users enter crap when they do not have a profile. Fo idea how this is possible, because the job description was published for SO.com users only.

* There are story links like  https://stackoverflow.com/users/story/5038322

* There are CV links like https://stackoverflow.com/users/story/12861492?view=Cv and https://stackoverflow.com/cv/dougmolina

* Some people (recruitment agencies) give links to StackOverflow company pages

## Normalising Github profiles

* Some people enter `https://github.com` because they do not have Github profile

# Get Google service account credentials

Use Signed credentials (Service account). [It is like 100 steps to hell to get one](https://gspread.readthedocs.io/en/latest/oauth2.html#using-signed-credentials).

The resulting `service-accont.json` file should look like:

```json
{
    "type": "service_account",
    "project_id": "stackoverflow-scraper",
    "private_key_id": "...",
    "private_key": "-----BEGIN PRIVATE KEY-----xxxx-----END PRIVATE KEY-----\n",
    "client_email": "scraper@stackoverflow-scraper.iam.gserviceaccount.com",
    "client_id": "...",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/scraper%40stackoverflow-scraper.iam.gserviceaccount.com"
  }
```

# Install

Install Python 3.8+. E.g:

```bash
pyenv install 3.8.1
pyenv global 3.8.1
```

Set up virtualenv

```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

# Run

## Scraping StackOveflow reputation scores

Share the spreadsheet with the service account email.

Everything is hardcoded in the script, so running it is just:

```sh
python soscrape.py
```

## Scraping Github repository counts

You need to get Github API token from Github personal token panel.

```sh
GITHUB_USERNAME=miohtama GITHUB_TOKEN=xxx python githubscape.py
```

## Scoring candidates

StackOverflow and Github data must be fetched first.

This script will read all row data from the Google Spreadsheet, run it through the scorecard formula and store the score back.

```sh
python uodatecandidatescoring.py
```

```
Updating row 393 candidate E**** N**** score 3
Updating row 394 candidate S**** R**** score 1
Updating row 395 candidate Y**** K**** score 6
Done, score summaries for this batch
```

# License

MIT