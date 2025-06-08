# Interfejs graficzny (frontend)

## Przegląd
Interfejs użytkownika to aplikacja Vue 3, która zapewnia interfejs pulpitu nawigacyjnego do tworzenia dynamicznych
wizualizacji danych. Najważniejsze funkcje obejmują:
- kreator zapytań do tworzenia niestandardowych zapytań dotyczących wykresów
- dynamiczne renderowanie wykresów przy użyciu Chart.js
- interfejs nawigacyjny oparty na zakładkach
- wyświetlanie tabel danych z funkcją sortowania i eksportowania
- ciemny motyw interfejsu użytkownika z responsywnym szablonem

## Podstawowe komponenty

### 1. App.vue
- Komponent główny zawierający globalne style CSS
- Definiuje ciemny motyw przy użyciu zmiennych CSS
- Zapewnia spójną stylistykę dla:
  - Typografii
  - Komponentów układu
  - Elementów formularza
  - Przycisków
  - Kart
  - Tabel
  - Okien modalnych
- Implementuje breakpointy responsywnego szablonu

### 2. MainComponent.vue
- Główny komponent układu
- Dzieli widok na dwa panele:
  1. **Panel wykresów**: wyświetla wizualizacje i tabele danych
  2. **Panel kreatora**: zawiera interfejs z zakładkami dla narzędzi
- Zarządza przepływem danych między kreatorem zapytań a komponentami wizualizacji

### 3. TabsComponent.vue
- System nawigacji zakładkami
- Funkcje:
  - Przyciski nagłówków zakładek
  - Dynamiczne renderowanie komponentów na podstawie wybranej zakładki
  - Płynne przejścia

### 4. QueryBuilder.vue
- Centralny komponent do tworzenia zapytań danych
- Sekcje obejmują:
  - Konfiguracja osi X
  - Zbiory danych osi Y (wiele)
  - Filtry
  - Filtry zagregowane
  - Opcje sortowania
  - Wybór typu wykresu
  - Ustawienia ograniczeń
- System walidacji formularzy
- Obsługa wysyłania żądań API

### 5. DynamicChart.vue
- Komponent renderowania wykresów przy użyciu Chart.js
- Funkcje:
  - Dynamiczna aktualizacja wykresów po zmianie właściwości
  - Responsywny element canvas
  - Czyszczenie instancji wykresów po odmontowaniu
  - Obsługa wielu typów wykresów
- Akceptuje:
  - `chartPayload`: Dane i konfiguracja wykresu
  - `chartNames`: Etykiety i tytuły osi

### 6. TableBuilder.vue
- Komponent wyświetlania tabeli danych
- Funkcjonalność:
  - Sortowalne kolumny
  - Eksport do formatu JSON/CSV
  - Responsywny projekt tabeli
  - Dynamiczne ładowanie danych
- Właściwości:
  - `table`: Dane nagłówka i wiersza
  - `fullPayload`: Oryginalne dane żądania

### 7. XAxis.vue
- Dedykowany komponent do konfiguracji osi X
- Wykorzystuje DbSelect do wyboru tabeli/pola
- Trzyczęściowa konfiguracja:
  1. Wybór tabeli
  2. Wybór pola
  3. Nazewnictwo aliasów pól

### 8. YAxisDatasetItem.vue
- Komponent wielokrotnego użytku dla zestawów danych osi Y
- Opcje konfiguracji:
  - Wybór tabeli
  - Wybór pola
  - Metoda agregacji
  - Alias pola
  - Etykieta wyświetlania

### 9. DatabaseInserts.vue
- Komponent interfejsu wyszukiwania
- Funkcje:
  - Ujednolicone pole wyszukiwania
  - Działania specyficzne dla punktu końcowego
  - Wyszukiwanie zbiorcze we wszystkich punktach końcowych
  - Wyświetlanie wyników z obsługą błędów
  - Stany ładowania
- Integruje się z:
  - Google Scholar
  - Scopus API
  - Scopus Scraper

## Przepływ danych
1. Użytkownik tworzy zapytanie w `QueryBuilder`
2. Zweryfikowana zawartość przesyłana do API
3. Dane odpowiedzi przekazywane do:
   - `DynamicChart` w celu wizualizacji
   - `TableBuilder` w celu wyświetlenia w formie tabeli
4. Użytkownik może eksportować dane za pomocą `TableBuilder`

## System motywów
- Zmienne CSS kontrolują wszystkie aspekty stylizacji
- Ciemny motyw z 3 poziomami tła
- Spójna paleta kolorów dla:
  - Kolorów podstawowych/drugorzędnych/akcentujących
  - Hierarchii tekstu
  - Stanów obramowania
  - Głębokości cienia
- Zmienne odstępów i promieni zapewniają spójność interfejsu użytkownika

## Responsywny projekt
- Podejście „mobile first”
- Punkty przełamania:
  - 768 pikseli: dostosowuje układ i rozmiary czcionek
  - 480 pikseli: optymalizuje wypełnienie kart i odstępy modalne
- Elastyczne komponenty:
  - Kolumny układają się w stos na urządzeniach mobilnych
  - Zmniejszenie rozmiaru czcionki w tabeli

## Kluczowe zależności
- Vue 3 (Composition API)
- Chart.js + vue-chartjs
- Narzędzia VueUse
- Niestandardowy komponent DbSelect (współdzielony)
- Fetch API do komunikacji z zapleczem

## Zarządzanie stanem
- Reaktywność na poziomie komponentów przy użyciu Vue ref/reactive
- Przekazywanie danych między komponentami oparte na właściwościach
- Obserwatorzy aktualizacji pól zależnych
- Walidacja formularzy z wyświetlaniem błędów

## Interakcja API
- Wszystkie punkty końcowe kierują do `http://127.0.0.1:5000`
- Główne punkty końcowe:
  - `/dynamic-chart/data` (POST) - Dane wykresu
  - `/dynamic-chart/export/{format}` (POST) - Eksport danych
  - `/filter-options/*` - Dynamiczne opcje filtrowania
  - Punkty końcowe wyszukiwania Scholar/Scopus

## Konwencje interfejsu użytkownika
- Spójne sekcje oparte na kartach
- Jednolite odstępy w formularzach (--space-lg gaps)
- Standaryzowane style/rozmiary przycisków
- Responsywne nagłówki tabel
- Ograniczona szerokość kontenerów (maks. 1200 pikseli)
