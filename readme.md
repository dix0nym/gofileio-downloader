# gofile.io-downloader

Simple file downloader for gofile.io folders in Python.

## Installation

```
# clone repo 
$ git clone https://github.com/dix0nym/gofileio-downloader

# or, only download single file
$ wget https://raw.githubusercontent.com/dix0nym/gofileio-downloader/main/downloader.py

# install required pip packages
$ pip install -r requirements.txt
# or as command
$ pip install requests tqdm
```

## Usage

```bash
$ python .\downloader.py -h
usage: downloader.py [-h] [-u USER_AGENT] URL

Gofile.io downloader

positional arguments:
  URL                   url to download - e.g. https://gofile.io/d/XXXXXX

options:
  -h, --help            show this help message and exit
  -u USER_AGENT, --user-agent USER_AGENT
                        custom user-agent-string
```

## How does it work?

1. Creating a user account via gofile.io REST API
2. Use REST API to obtain file listing by account token and contentId
3. Parse API response and download files