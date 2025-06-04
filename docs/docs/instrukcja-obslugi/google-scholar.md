---
title: "Google Scholar"
description: "Instrukcja dot. konfigurowania modułu Google Scholar"
keywords: 
  - google scholar
  - scraping
---

# Google Scholar

Moduł pobierający dane z Google Scholara. Jego zaletą jest znikoma konfiguracja. Niestety ma znaczące 
wady, zwłaszcza w porównaniu do modułów Scopusa:
- najmniejsza ilość dostępnych informacji,
- potrzeba posiadania dużej ilości serwerów proxy (Google bardzo szybko wykrywa scrapery).

## Konfiguracja

### Proxy (serwery pośredniczące)
Pobieranie danych z Google Scholara wymaga dużej ilości serwerów proxy. Serwery te możemy przekazać aplikacji
za pomocą przełącznika `-p`:

```shell
python3 main.py --google-scholar -p http://some-proxy.org:31283 -p http://some-other-proxy.net:8080 "python3 C++"
```

### User-Agent i adres bazowy

:::info

Ten krok nie jest wymagany podczas codziennego użytkowania. Zmiana adresu bazowego jest przydatna głównie 
dla programistów.

:::

Klient użytkownika oraz adres bazowy możemy ustawiać za pomocą zmiennych środowiskowych (np. za pomocą pliku .env):

```
GOOGLE_SCHOLAR_BASE=https://scholar.google.com
GOOGLE_SCHOLAR_USER_AGENT=saturday/1.0
```