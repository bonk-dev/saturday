---
title: "Interfejs graficzny"
description: "Poradnik po interfejsie graficzny,"
keywords: 
  - web
  - przeglądarka
  - graficzny
  - wykresy
---

# Interfejs graficzny (webowy)

Jedną z opcji korzystania z programu jest interfejs graficzny. Za jego pomocą można pobierać dane oraz tworzyć wykresy.

## Uruchamianie

Interfejs graficzny można uruchomić zarówno za pomocą zbudowanego pliku `gui.exe`, jak i za pomocą skryptu.

Zbudowany plik nie wymaga instalacji żadnych innych programów. Wystarczy dwa razy kliknąć plik:

<video controls preload='metadata' class="saturday-video" aria-hidden="true">
    <source src={require('./assets/gui-7.webm').default} />
</video>

Następnie należy w przeglądarce otworzyć adres: [http://127.0.0.1:5000/ui](http://127.0.0.1:5000/ui).

## Pobieranie danych

Pobieranie danych jest dostępne w zakładce "Fetch data". Po wpisaniu kwerendy możemy wybrać pobieranie jednym 
z modułów albo wszystkimi.

![Zrzut ekranu pokazujący zakładę "Fetch data"](./assets/gui-1.webp)
<p class="text--italic" aria-hidden="true">Zrzut ekranu pokazujący zakładę "Fetch data"</p>

## Wykresy

Za pomocą interfejsu graficznego można tworzyć różne wykresy, na podstawie pobranych wcześniej danych.

### Przykład

Aby stworzyć wykres przedstawiający ilość publikacji w zależności od autora, należy na początek ustawić
oś X tak, aby przedstawiała autorów (oraz identyfikujące ich pole, np. imię i nazwisko).

![Zrzut ekranu pokazujący ustawienia osi X](./assets/gui-2.webp)
<p class="text--italic" aria-hidden="true">Zrzut ekranu pokazujący ustawienia osi X</p>

Następnie trzeba skonfigurować oś Y tak, aby znajdowała się na niej liczba artykułów. Do tego służy funkcja `count`.

![Zrzut ekranu pokazujący ustawienia osi Y](./assets/gui-3.webp)
<p class="text--italic" aria-hidden="true">Zrzut ekranu pokazujący ustawienia osi Y</p>

Należy jeszcze wybrać typ wykresu (przykładowo słupkowy), oraz opcjonalnie ustawić limit na osi X oraz sortowanie.

![Zrzut ekranu pokazujący dodatkowe ustawienia](./assets/gui-4.webp)
<p class="text--italic" aria-hidden="true">Zrzut ekranu pokazujący dodatkowe ustawienia</p>

Na koniec trzeba nadać nazwę wykresowi i nacisnąć przycisk "Submit Query".

![Zrzut ekranu pokazujący dodatkowe ustawienia #2](./assets/gui-5.webp)
<p class="text--italic" aria-hidden="true">Zrzut ekranu pokazujący dodatkowe ustawienia #2</p>

Po chwili powinien pojawić się wykres oraz odpowiadająca mu tabela danych.

![Zrzut ekranu przedstawiający wygenerowany wykres](./assets/gui-6.webp)
<p class="text--italic" aria-hidden="true">Zrzut ekranu przedstawiający wygenerowany wykres</p>
