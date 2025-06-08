---
title: "Interfejs konsolowy"
description: "Poradnik po interfejsie konsolowym"
keywords: 
  - CLI
  - konsola
---

# Interfejs konsolowy

Jedną z opcji korzystania z programu jest interfejs konsolowy. Za jego pomocą można jedynie pobierać dane z modułów.

## Dostępne przełączniki
```shell
$ python3 main.py -h
usage: main.py [-h] [-a] [-p PROXY] [--debug-proxy DEBUG_PROXY] [-g] [-s]
               [--scopus-api-output SCOPUS_API_OUTPUT] [-b]
               [--scopus-batch-file SCOPUS_BATCH_FILE]
               [--scopus-batch-output SCOPUS_BATCH_OUTPUT] [--ssl-insecure]
               search_query

Science publication metadata scraper

positional arguments:
  search_query          Generic search query to use when scraping metadata

options:
  -h, --help            show this help message and exit
  -a, --all             Use all methods (google-scholar, scopus)
  -p, --proxy PROXY     HTTP(S) proxy address, example: -p http://127.0.0.1:8080
                        -p http://127.0.0.2:1234. Not used when making requests
                        to IP-authenticated services (Elsevier, Scopus, etc.)
  --debug-proxy DEBUG_PROXY
                        HTTP(S) proxy address, used for ALL requests, including
                        ones made to services based on IP authentication
                        (Elsevier, Scopus)
  -g, --google-scholar  Use Google Scholar for scraping metadata
  -s, --scopus-api      Use Scopus API for scraping metadata
  --scopus-api-output SCOPUS_API_OUTPUT
                        Path to a file where raw data fetched from Elsevier API
                        will be saved. File type: JSON.
  -b, --scopus-batch    Use Scopus batch export for scraping metadata
  --scopus-batch-file SCOPUS_BATCH_FILE
                        Use a local .CSV dump instead of exporting from Scopus
  --scopus-batch-output SCOPUS_BATCH_OUTPUT
                        Path to a file where raw data fetched from Scopus batch
                        export will be saved. File type: CSV.
  --ssl-insecure        Do not verify upstream server SSL/TLS certificates
```

## Przykłady

### Wszystkie moduły
```shell
$ python3 main.py --all "python3 C++" 
```

### API Elsevier (Scopus)
```shell
$ python3 main.py --scopus-api "python3 C++" 
```

### Scopus (bramka eksportu)
```shell
$ python3 main.py --scopus-batch "python3 C++" 
```

### Scopus (bramka eksportu, zrzut .CSV do pliku)
```shell
$ python3 main.py --scopus-batch --scopus-batch-output "/tmp/sc-batch.csv" "python3 C++" 
```

### Scopus (bramka eksportu) i Google Scholar
```shell
$ python3 main.py --scopus-batch --google-scholar "python3 C++" 
```