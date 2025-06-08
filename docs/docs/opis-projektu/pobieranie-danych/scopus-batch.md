# Bramka eksportu Scopus

Moduł pobierający dane za pomocą bramki eksportu, z której korzysta interfejs webowy Scopusa.
Dostęp jest przyznawany na podstawie ciasteczek (sesji) użytkownika oraz na podstawie źródłowego adresu IP.

Moduł znajduje się w katalogu [fetcher/scopus_batch](https://github.com/bonk-dev/saturday/tree/main/fetcher/scopus_batch).

## Wymagane ciasteczka

Lista wymaganych przez Scopusa ciasteczek:
- `AWSELB`
- `SCOPUS_JWT`
- `SCSessionID`
- `scopusSessionUUID`

## Punkty końcowe

Nie istnieje publiczna dokumentacja punktów końcowych bramki eksportu. To, w jaki sposób interfejs webowy Scopusa korzysta
z tej bramki, zostało wydedukowane na podstawie analizy ruchu sieciowego.

### Wyszukiwanie publikacji po słowach kluczowych

```http request title="Żądanie zwracające odpowiedź z listą identyfikatorów znalezionych publikacji. Format ciała żądania: JSON"
POST https://www.scopus.com/api/documents/search/eids
{
    "documentClassificationEnum": "primary",
    "itemcount": 5,
    "offset": 0,
    "query": "TITLE-ABS-KEY(python)",
    "sort": 'plf-f'
}
```
Maksymalna liczba identyfikatorów zwróconych w jednej odpowiedzi (parametr `itemcount`) to `2000`.

Przykładowa odpowiedź:
```json title="Odpowiedź na POST /api/documents/search/eids"
"response": {
    "numFound": 1455,
    "docs": [
        "2-s2.0-85216271415",
        "2-s2.0-105003577803",
        "2-s2.0-105003654530",
        "2-s2.0-105003921873",
        "2-s2.0-105003970001"
    ]
}
```

:::tip

`numFound` zwraca liczbę wszystkich znalezionych w bazie publikacji, a nie liczbę zwróconych wyników.

::: 

### Eksport danych o publikacji

Za pomocą bramki można wyeksportować dane o maksymalnie stu publikacjach na jedno żądanie. Obsługiwane formaty to:
- CSV
- RIS
- BibTex
- tekst.

W eksporcie do CSV znajduje się najwięcej informacji, dlatego właśnie ten format jest wykorzystywany przez program.

```http request title="Żądanie zwracające dane o publikacjach. Format ciała żądania: JSON"
POST https://www.scopus.com/gateway/export-service/export?batch_id=aaaaaa_0_0
{
    "eids": [
        "2-s2.0-85216271415",
        "2-s2.0-105003577803",
        "2-s2.0-105003654530",
        "2-s2.0-105003921873",
        "2-s2.0-105003970001"
    ],
    "fileType": "CSV",
    "fieldGroupIdentifiers": ["titles", "authors", "doi", "..."],
    "keyEvent": {
        "sessionId": "SC_SESSION_ID cookie value",
        "transactionId": "SC_SESSION_ID:1"
        "origin": "resultsList",
        "zone": "resultsListHeader",
        "primary": "",
        "totalDocs": 1455
    },
    "locale": "en-US",
    "hideHeaders": false
}
```
Parametry:
- `eids` - lista identyfikatorów EID publikacji
- `fileType` - format eksportu
- `fieldGroupIdentifiers` - lista pól, które mają się pojawić w pliku CSV
- `keyEvent` - obiekt opisujący zdarzenie w interfejsie webowym; nie ma wpływu na eksport
- `locale` - język
- `hideHeaders` - w pliku CSV: jeżeli `false`, pojawi się wiersz nagłówkowy Title, Authors, DOI itd. Jeżeli `true`, 
   ten wiersz nie zostanie dodany.

### Odświeżenie tokenu JWT

Do komunikacji z bramką potrzebny jest m.in. token JWT, który jest wysyłany jako ciasteczko (w nagłówku `Cookie`) 
o nazwie `SCOPUS_JWT`. Jest on ważny przez około 15/20 minut. Po upływie tego czasu (mierzonego od utworzenia tokenu)
należy go odświeżyć za pomocą poniższego żądania. 

:::note

Aplikacja nie sprawdza ważności tokenu. Token jest odświeżany, gdy któreś żądanie zwróci odpowiedź o kodzie statusu 403.

:::

```http request title="Żądanie odświeżające token JWT"
GET https://www.scopus.com/api/auth/refresh-scopus-jwt
```

Po pomyślnym odświeżeniu serwer zwróci odpowiedź o kodzie 200, z nagłówkiem `Set-Cookie` zawierającym nowy token.
Jeżeli odświeżenie nie powiodło się, serwer zwróci odpowiedź z przekierowaniem (kod 3xx).

## Wstępne parsowanie CSV

Po wyeksportowaniu danych moduł parsuje plik CSV za pomocą wbudowanego modułu `csv`. Logika odpowiedzialna za parsowanie
znajduje się w pliku 
[fetcher/scopus_batch/parser.py](https://github.com/bonk-dev/saturday/tree/main/fetcher/scopus_batch/parser.py).

Parser oczekuje całego, kompletnego pliku. Wywoła on błąd, gdy wiersz nagłówkowy nie będzie się zgadzał z oczekiwanym.