---
sidebar_position: 5
---

# Podsumowanie

Projekt ten jest aplikacją napisana w języku Python 3 (wymagająca co najmniej wersji 3.10), zaprojektowaną 
do wyodrębniania i przetwarzania metadanych (takich jak tytuł, autorzy, streszczenie, sponsorzy itp.) 
z publikacji naukowych pochodzących z platform takich jak Scopus (przy użyciu dwóch różnych metod) 
i Google Scholar (poprzez scraping HTML).

## Kluczowe cechy
- **Gromadzenie danych z wielu źródeł:**  
  Program gromadzi metadane publikacji z wielu źródeł, wykorzystując zarówno oficjalne, jak i nieoficjalne 
  interfejsy API HTTP oraz scraping HTML.
- **Wykorzystane technologie:**
  Główne biblioteki obejmują HTTPX dla żądań HTTP(S) i BeautifulSoup4 dla scrapingu HTML.
- **Ujednolicenie formatów:**  
  Narzędzie obsługuje różne formaty danych zwracane przez różne źródła (np. JSON z interfejsów API, CSV 
  z nieoficjalnych eksportów i częściowo przetworzone słowniki Python z HTML scrapingu). Ujednolica te 
  formaty, przetwarzając i przechowując wszystkie metadane w ustrukturyzowanej bazie danych SQLite.
- **Wydajny eksport:**
  Po skonsolidowaniu danych w bazie danych można je łatwo eksportować lub przeszukiwać w celu dalszej analizy.

## Rozbudowa projektu
- **Modułowa konstrukcja modułu pobierającego dane:**
  Aplikacja została zaprojektowana z myślą o modułowości. Programiści mogą dodawać nowe źródła danych, tworząc dodatkowe 
  moduły pobierające dane, które są zgodne z oczekiwanym formatem wejścia/wyjścia. Moduły te mogą korzystać z 
  interfejsów API, scrapingu HTML lub innych protokołów i muszą jedynie dostarczać metadane w formie, która może być 
  przetworzona i zunifikowana z istniejącym schematem bazy danych.
- **Dostosowanie schematu bazy danych:**  
  Jeśli wymagane są nowe typy metadanych lub źródła publikacji, programiści mogą rozszerzyć schemat SQLite 
  zapewniając płynną integrację nowych danych.
- **Konfiguracja wiersza poleceń i środowiska:**
  Konfiguracja za pomocą argumentów wiersza poleceń i zmiennych środowiskowych ułatwia wprowadzanie nowych opcji 
  lub punktów integracji dla przyszłych źródeł, czy też formatów eksportu.

## Wnioski
Takie podejście zapewnia kompleksowe pokrycie metadanych publikacji, nawet ze źródeł o ograniczonej lub braku 
obsługi API, oraz zapewnia solidny, ujednolicony backend do dalszych badań lub analiz.

Programiści mogą w łatwy sposób rozszerzać lub dostosowywać projekt, aby obsługiwał nowe naukowe bazy danych, formaty 
wyjściowe lub procesy przetwarzania.