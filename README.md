# Project Overview

This project is a set of Python scripts designed to scrape data from LinkedIn and Apollo.io, send cold emails, and schedule meetings on Google Calendar. The scripts use Selenium for automation, Groq API for email generation, and Gmail/Google Calendar APIs for email and calendar management.

## Prerequisites

To run this project, you will need the following:

- Python 3.x
- Google Chrome browser and the compatible ChromeDriver
- Groq API Key: Required for the `Email_Generation_and_sending.py` script.
- Google API Credentials: Needed to access Gmail and Google Calendar services. You will need a `credentials.json` file, which can be downloaded from the Google Cloud Console.

## Installation

First, you need to install the required Python libraries. You can use the `requirements.txt` file:

```bash
pip install -r requirements.txt

```

## Configuration

To run the project properly, some configuration files are required.

### 1. `setup.ini`

This file is for LinkedIn login credentials and connection request settings.

- In the `[LinkedIn]` section, enter your LinkedIn username and password.
- In the `[Target]` section, enter the LinkedIn profile URL you want to target.
- In the `[Settings]` section, set `include_note` to `yes` or `no`, and write the message to send with the connection request.

Example file content:

```ini
[LinkedIn]
username = your_linkedin_username
password = your_linkedin_password

[Target]
profile_url = https://www.linkedin.com/in/target-profile/

[Settings]
include_note = yes
message = Hi, I'd like to connect with you on LinkedIn!


```
### 2. `config.json`

This file is for the Apollo.io scraper. Here, you can configure the name of the CSV file where leads will be exported.

Example file content:

```json
{
  "email": "your_apollo_login_email",
  "password": "your_apollo_login_password",
  "start_url": "Empty",
  "export_file_name": "apollo_leads.csv"
}
```

### 3. `.env` (Environment Variables)

You haven’t provided a `.env` file, but for security reasons, it’s better to store sensitive information like the Groq API key and other keys in it. 

Create a `.env` file and store your Groq API key like this:

```env
GROQ_API_KEY="gsk_your_groq_api_key"
```

## Scripts Description

### ApolloScraper.py
- This script scrapes leads from Apollo.io.
- It asks the user for filters like Job Title and Location to create a dynamic search URL.
- Supports manual login and CAPTCHA solving.
- Saves the scraped data (`first_name`, `last_name`, `job_title`, `company_name`, `location`, `email_address1`, `email_address2`, `linkedin_url`) into the CSV file named in `config.json`.

### Connect_and_message.py
- This script automatically sends connection requests on LinkedIn.
- Reads credentials and target URL from `setup.ini`.
- Navigates to the target profile and looks for the Connect button.
- If `include_note` is set to yes, it sends a connection request with a custom message.
- If the Connect button is not found, it tries to follow the profile instead.

### Emain_Extractor_Linkedin.py and demo.py
- `Emain_Extractor_Linkedin.py` contains a LinkedIn class used to extract emails from LinkedIn profiles.
- The `selenium_login` method logs into LinkedIn.
- The `singleScan_selenium` method extracts `.com` emails from the profile’s contact info page and returns them along with the name.
- `demo.py` is a simple demonstration of the `Emain_Extractor_Linkedin.py` class.

