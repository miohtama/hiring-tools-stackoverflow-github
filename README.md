This script will scrape user profile data from StackOverflow. It uses Google Spreadsheet for both input (profile links) and output (reputation value).
It mainly works around Google Spreadsheet internal `IMPORTXML` scraping limitations (throttle), 
plus does a lot of normalisation and cleaning that you cannot do in a spreadsheet.

We use [gspread](https://github.com/burnash/gspread) and bunch of well-known Python ecosystem libraries.

# Input

User give links to their StackOverflow.com profiles. The challenge is the following

* Some users enter crap when they do not have a profile. Fo idea how this is possible, because the job description was published for SO.com users only.

* There are story links like  https://stackoverflow.com/users/story/5038322

* There are CV links like https://stackoverflow.com/users/story/12861492?view=Cv and https://stackoverflow.com/cv/dougmolina

We need to normalise all this.

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

Share the spreadsheet with the service account email.

Everything is hardcoded in the script, so running it is just:
```sh
python soscrape.py
```

# Other 

I did not know that you can have a score less than 10 if you have a question or an answer on StackOverflow. 
I went and voted up those users to make my data look better.