This script will scrape user profile data from StackOverflow. It uses Google Spreadsheet for both input and output.
It mainly works around Google Spreadsheet internal `IMPORTXML` scraping limitations.

# Get credentials

Use Signed credentials (Service account). [It is like 100 unnecessary steps](https://gspread.readthedocs.io/en/latest/oauth2.html#using-signed-credentials). 

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