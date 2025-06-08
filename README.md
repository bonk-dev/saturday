# saturday
A Python 3 app designed to scrape science publication metadata from various sources like: 
- Scopus 
  - Elsevier API
  - Scopus' website export gateway
- Google Scholar

## Build
1. Install [just](https://github.com/casey/just?tab=readme-ov-file#installation)
2. Run `just all` - the artifacts will be in the `dist/` directory.

All available recipes:
```shell
$ just -l
Available recipes:
    all  # Build everything
    cli  # Build the Python CLI into an exe
    docs # Build Docusaurus docs
    env  # Copy .env.sample to dist/.env
    gui  # Build backend + frontend into an exe
```

## Usage
### Command-line
```shell
$ python3 main.py
usage: main.py [-h] [-a] [-p PROXY] [--debug-proxy DEBUG_PROXY] [-g] [-s]
               [--scopus-api-output SCOPUS_API_OUTPUT] [-b] [--scopus-batch-file SCOPUS_BATCH_FILE]
               [--scopus-batch-output SCOPUS_BATCH_OUTPUT] [--ssl-insecure]
               search_query

Science publication metadata scraper

positional arguments:
  search_query          Generic search query to use when scraping metadata

options:
  -h, --help            show this help message and exit
  -a, --all             Use all methods (google-scholar, scopus)
  -p, --proxy PROXY     HTTP(S) proxy address, example: -p http://127.0.0.1:8080 -p
                        http://127.0.0.2:1234. Not used when making requests to IP-authenticated
                        services (Elsevier, Scopus, etc.)
  --debug-proxy DEBUG_PROXY
                        HTTP(S) proxy address, used for ALL requests, including ones made to
                        services based on IP authentication (Elsevier, Scopus)
  -g, --google-scholar  Use Google Scholar for scraping metadata
  -s, --scopus-api      Use Scopus API for scraping metadata
  --scopus-api-output SCOPUS_API_OUTPUT
                        Path to a file where raw data fetched from Elsevier API will be saved. File
                        type: JSON.
  -b, --scopus-batch    Use Scopus batch export for scraping metadata
  --scopus-batch-file SCOPUS_BATCH_FILE
                        Use a local .CSV dump instead of exporting from Scopus
  --scopus-batch-output SCOPUS_BATCH_OUTPUT
                        Path to a file where raw data fetched from Scopus batch export will be
                        saved. File type: CSV.
  --ssl-insecure        Do not verify upstream server SSL/TLS certificates
```

#### All scrapers
```shell
$ python3 main.py --all "python3 C++" 
```
#### Scopus (batch gateway)
```shell
$ python3 main.py --scopus-batch "python3 C++" 
```

#### Scopus (batch gateway, save dump to file)
```shell
$ python3 main.py --scopus-batch --scopus-batch-output "/tmp/sc-batch.csv" "python3 C++" 
```

#### Scopus (batch gateway) and Google Scholar
```shell
$ python3 main.py --scopus-batch --google-scholar "python3 C++" 
```

## Tests
Currently, only the `fetchers` module contains automated unit tests:
```shell
$ python -m unittest discover fetcher/tests
...........
----------------------------------------------------------------------
Ran 11 tests in 0.200s

OK
```

## Setup
### Python requirements
In order to install required Python packages:
- (optionally) set up a venv: ```python -m venv .venv && source .venv/bin/activate```
- install packages: ```pip install -r requirements.txt```

### Environment variables
Some fetcher modules require additional setup (API keys, cookies etc.).
Here are the required steps for all implemented fetchers.

### Elsevier (Scopus) API

#### SCOPUS_API_KEY
In order to use the Elsevier API a key is required. You can create 
such key (which is linked to your account) on [https://dev.elsevier.com/apikey/manage](https://dev.elsevier.com/apikey/manage).

After acquiring the API key, it needs to be supplied with an environment
variable: `SCOPUS_API_KEY`.
The app supports .env files (see `.env.sample`).

#### SCOPUS_API_BASE
The app also supports using a different API endpoint, which can be controlled
with the `SCOPUS_API_BASE` environment variable (or in .env).

#### Example .env
```
SCOPUS_API_BASE=https://api.elsevier.com
SCOPUS_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Scopus batch export
Scopus batch export is an alternative method to the official Elsevier API.
It uses the endpoints utilized by the Scopus website, allowing the user to export
more data at once, while also skipping the weekly limit enforced by the Elsevier API.

The downside is it is harder to set up. Instead of a single, long-lived API key, a cookie
dump from the user's browser is needed. These cookies are short-lived and need to be refreshed
once in a while (implemented in the app).

The required coookies are:
- `SCSessionID`
- `scopusSessionUUID`
- `AWSELB`
- `SCOPUS_JWT`

#### Example .env
```
SCOPUS_BATCH_BASE=https://www.scopus.com
SCOPUS_BATCH_COOKIE_FILE=/tmp/scopus-batch-cookies
SCOPUS_BATCH_COOKIE_JWT_DOMAIN=.scopus.com
SCOPUS_BATCH_USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.3
```

After creating the file, the user needs to supply the path to the app with
an environment variable (or the .env file): `SCOPUS_BATCH_COOKIE_FILE`.
For example `SCOPUS_BATCH_COOKIE_FILE=/tmp/scopus-cookies`.

#### SCOPUS_BATCH_BASE
This env variable allows the user to change the base URI of the endpoints used
by the scraper module. Default value: `https://www.scopus.com`.

For example, if you change this to https://example.org, then the scraper
will send a request to `https://example.org/api/documents/search/eids` 
and **NOT** to `https://www.scopus.com/api/documents/search/eids` when searching
for documents to export.

#### SCOPUS_BATCH_COOKIE_FILE
This env variable allows the user to set the path to a file containing the user's
authentication cookies.

The cookies are to be supplied as sent by browser in the `Cookie:` header. 
This means, that a user can copy and paste the `Cookie:` header value 
into a file, and use it as is (unexpected cookies will be ignored).

Example file:
```
SCSessionID=cookie_val; scopusSessionUUID=cookie_val2; AWSELB=cookie_val3; SCOPUS_JWT=cookie_val4
```

#### SCOPUS_BATCH_COOKIE_JWT_DOMAIN
This env variable controls the `Domain` parameter of the `SCOPUS_JWT` cookie.
Default value: `.scopus.com`.
`SCOPUS_JWT` needs to have the correct `Domain` value, because it's refreshed
periodically (by the `Set-Cookie` header) and the [HTTPX](https://github.com/encode/httpx)
client won't accept a cookie with a different domain, than previously set.

#### SCOPUS_BATCH_USER_AGENT
This env variable is used by the app to set the correct `User-Agent` header
when sending requests to the Scopus' endpoints.

It is important to use the user's web-browser `User-Agent` value, because
using anything different **will** trigger Cloudflare anti-bot mechanisms.

### Google Scholar
This fetcher module doesn't require any authentication cookies or keys, but
a user can configure the base URI for requests and the User-Agent to be used
by the HTTP(S) client.

Also, a user can supply a proxy server to use while scraping with 
the `--proxy` option (see [Usage](#usage)).

#### GOOGLE_SCHOLAR_BASE
This env variable allows the user to change the base URI of the endpoints used
by the scraper module. Default value: `https://scholar.google.com`.

For example, if you change this to `https://example.org`, then the scraper
will send a request to `https://example.org/scholar?q=...` 
and **NOT** to `https://scholar.google.com/scholar?q=...` when searching
for publications.

#### GOOGLE_SCHOLAR_USER_AGENT
This env variable is used by the app to set the `User-Agent` header
when sending requests to the Google Scholar website.

#### Example .env
```
GOOGLE_SCHOLAR_BASE=https://scholar.google.com
GOOGLE_SCHOLAR_USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36
```