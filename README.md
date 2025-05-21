# saturday
A Python 3 app designed to scrape science publication metadata from various sources like: 
- Scopus 
  - Elsevier API
  - Scopus' website export gateway
- Google Scholar

## Usage
### Command-line
```shell
$ python3 main.py
usage: main.py [-h] [-a] [-p PROXY] [-g] [-s] [-b] [--scopus-batch-file SCOPUS_BATCH_FILE] [--ssl-insecure] search_query

Science publication metadata scraper

positional arguments:
  search_query          Generic search query to use when scraping metadata

options:
  -h, --help            show this help message and exit
  -a, --all             Use all methods (google-scholar, scopus)
  -p, --proxy PROXY     HTTP(S) proxy address, example: -p http://127.0.0.1:8080 -p http://127.0.0.2:1234
  -g, --google-scholar  Use Google Scholar for scraping metadata
  -s, --scopus-api      Use Scopus API for scraping metadata
  -b, --scopus-batch    Use Scopus batch export for scraping metadata
  --scopus-batch-file SCOPUS_BATCH_FILE
                        Use a local .CSV dump instead of exporting from Scopus
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

#### Scopus (batch gateway) and Google Scholar
```shell
$ python3 main.py --scopus-batch --google-scholar "python3 C++" 
```