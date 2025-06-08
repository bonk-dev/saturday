# API Elsevier (Scopus) 

Moduł pobierający dane z API Elsevieru korzysta z publicznego, udokumentowanego API. Dostęp jest przyznawany
na podstawie kluczy API wygenerowanych przez użytkownika oraz na podstawie źródłowego adresu IP.

Moduł znajduje się w katalogu [fetcher/scopus](https://github.com/bonk-dev/saturday/tree/main/fetcher/scopus).

## Dokumentacja API

Dokumentacja API Elsevieru jest dostępna na stronie: [https://dev.elsevier.com/api_docs.html](https://dev.elsevier.com/api_docs.html).

Klucze można wygenerować tutaj: [https://dev.elsevier.com/apikey/manage](https://dev.elsevier.com/apikey/manage).

## Pobieranie danych

Program wykorzystuje jeden punkt końcowy API do pobierania danych:

```http request title="Pobieranie strony z wynikami z API"
GET https://api.elsevier.com/content/search/scopus?query=TITLE-ABS-KEY(python)&view=COMPLETE&start=0&count=25
```

Gdzie:
- `count`: maksymalna liczba pozycji w odpowiedzi (twardy limit określony przez API to `25`)
- `start`: wartość pozwalająca pominąć wcześniejsze pozycje (paginacja).

Typy danych pobierane z API dostępne są w pliku
[fetcher/scopus/models.py](https://github.com/bonk-dev/saturday/blob/main/fetcher/scopus/models.py).