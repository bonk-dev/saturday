# Budowanie

Dla użytkowników końcowych nawet instalacja Pythona mogłaby być niepraktyczna, dlatego stworzony został prosty
system budowania oparty na [just](https://github.com/casey/just).

Moduł CLI jest pakowany do pliku `cli.exe` a moduł webowy do `gui.exe` (backend i frontend). Jest to realizowane
za pomocą [PyInstallera](https://pyinstaller.org/).

Generowana jest również wersja dokumentacji przeznaczona na środowisko produkcyjne.