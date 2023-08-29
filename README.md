# Vulnerability JIRA Integration

Foobar is a Python library for dealing with word pluralization.

## Installation

use ```make install``` to install project requirements
or
```pip install -r requirements.txt```

## Usage

Before running the python script ```python src/main.py```, variables and secrets need to be configured
```
├── src
│   ├── config.py (Loads the toml file)
│   ├── main.py (Main script)
│   ├── io_helpers.py (Use to write/read files)
├── data
│   ├── vulnerabilities.json (Store previous vulnerabilities)
├── .env (Store API keys and secrets)
├── config.toml (Store URLS and board names)
├── Makefile
├── requirements.txt
├── README
└── .gitignore
```

***The following files need to be setup prior to running the script***
**(1) .env file - create one in root dir**
```
tenable_access_key = ""
tenable_secret_key = ""
jira_token = "" (Your JIRA API token)
jira_email = "" (Email for JIRA account that admintered the token and has Admin privileges)
 ```

**(1) config.toml file**
```
[jira]
    key = "YOUR_PROJECT_KEY"
    url = "https://YOUR_DOMAIN.atlassian.net"
```