# Google Scholar

Moduł pobierania danych znajduje się 
w [fetcher/gscholar](https://github.com/bonk-dev/saturday/tree/main/fetcher/gscholar).

Pozyskiwanie informacji o publikacjach opiera się na me scrapingu stron HTML oraz pobieraniu plików w formacie bibtex.

## Przygotowanie sesji

Przed rozpoczęciem pozyskiwania danych, klient włącza wyświetlanie linków do plików cytowania w formacie bibtex.
Pozwala to na zaoszczędzenie jednego żądania na każdą pozycję na pojedynczej stronie wyszukiwania.

Na początek wysyłane jest żądanie o stronę ustawień, z której odczytywane są potrzebne parametry:
```http request title="Strona ustawień/preferencji"
GET https://scholar.google.com/scholar_settings?hl=en&as_sdt=0,5
```

Odczytywanie parametrów:
```python
s = BeautifulSoup(settings_page_r.text, 'html.parser')
form_e = s.find('form', attrs={'id': 'gs_bdy_frm'})
scisig_e = form_e.find('input', attrs={'name': 'scisig'})
scisig = scisig_e.attrs['value']

inst_e = (s
          .find('div', attrs={'id': 'gs_settings_liblinks_lst'})
          .find('input', attrs={'name': 'inst'}))
inst_val = inst_e.attrs['value']
```

Następnie wysyłane jest żądanie POST do `/scholar_setprefs`, z wartością parametru `scis` ustawioną na `yes`, co włącza
wyświetlanie linków do plików bibtex:

```http request title="Wysyłanie nowych ustawień"
POST https://scholar.google.com/scholar_setprefs?scis=yes&[...]
```

```python
await self._session.get(f'{self._base}/scholar_setprefs', params={
            'scisig': scisig,
            'xsrf': '',
            'as_sdt': '0,5',
            'scis': 'yes',  # add BibTex citation links
            'scisf': '4',
            'hl': 'en',
            'lang': 'all',
            'instq': '',
            'inst': inst_val,
            'boi_access': '1',
            'has_boo_access': '1',
            'has_casa_opt_in': '1',
            'save': ''
        })
```

## Scrapowanie HTML

Wyszukiwarka zwraca po dziesięć pozycji na stronę. Każda strona ma niezmienną strukturę HTML, co ułatwia pobieranie
danych. Klient wysyła następujące żądanie, aby pobrać daną stronę:

```http request title="Pobieranie pojedynczej strony z wynikami wyszukiwania"
GET https://scholar.google.com/scholar?start=0&q=python3&hl=en&as_sdt=0,5&as_vis=1
```
Gdzie:
- `start` oznacza pozycję, od której ma zaczynać się strona; 
- `q` to wyszukiwana fraza; 
- `hl` to język; 
- `as_vis` ustawione na jeden wyklucza pozycje "cytat".

Na początku klient sprawdza, czy w kodzie strony znajduje się formularz o id = `gs_captcha_f`. Jeżeli tak, to Google
wykryło naszego klienta jako bota. W takim momencie klient zmienia serwer pośredniczący na następny z listy. Jeżeli nie
ma pozostałych, nieużytych wcześniej serwerów to klient kończy pracę.

Każda pozycja na stronie zawiera się w elemencie, którego atrybut klasy jest ustawiony na `gs_r gs_or gs_scl`.

Przykładowa pozycja:
```html
<div class="gs_r gs_or gs_scl" data-cid="QhDl7b8ZhqwJ" data-did="QhDl7b8ZhqwJ" data-lid="" data-aid="QhDl7b8ZhqwJ"
     data-rp="0">
    <div class="gs_ri"><h3 class="gs_rt" ontouchstart="gs_evt_dsp(event)"><span class="gs_ctc"><span class="gs_ct1">[PDF]</span><span
            class="gs_ct2">[PDF]</span></span> <a id="QhDl7b8ZhqwJ"
                                                  href="http://static.softwaresuggest.com.s3.amazonaws.com/ssguides/1604480172_Python_read%20(1).pdf"
                                                  data-clk="hl=en&amp;sa=T&amp;oi=ggp&amp;ct=res&amp;cd=0&amp;d=12431652133523492930&amp;ei=VGlDaJqQHZLXieoPwNDK0Qk"
                                                  data-clk-atid="QhDl7b8ZhqwJ"><b>Python</b></a></h3>
        <div class="gs_a">W <b>Python</b>&nbsp;- <b>Python </b>releases for windows, 2021 -
            static.softwaresuggest.com.s3&nbsp;…
        </div>
        <div class="gs_rs">• <b>Python</b> was designed for readability, and has some similarities to the English
            language with <br>
            influence from mathematics.• <b>Python</b> uses new lines to complete a command, as opposed …
        </div>
        <div class="gs_fl gs_flb"><a href="javascript:void(0)" class="gs_or_sav gs_or_btn" role="button">
            <svg viewBox="0 0 15 16" class="gs_or_svg">
                <path d="M7.5 11.57l3.824 2.308-1.015-4.35 3.379-2.926-4.45-.378L7.5 2.122 5.761 6.224l-4.449.378 3.379 2.926-1.015 4.35z"></path>
            </svg>
            <span class="gs_or_btn_lbl">Save</span></a> <a href="javascript:void(0)" class="gs_or_cit gs_or_btn gs_nph"
                                                           role="button" aria-controls="gs_cit" aria-haspopup="true">
            <svg viewBox="0 0 15 16" class="gs_or_svg">
                <path d="M6.5 3.5H1.5V8.5H3.75L1.75 12.5H4.75L6.5 9V3.5zM13.5 3.5H8.5V8.5H10.75L8.75 12.5H11.75L13.5 9V3.5z"></path>
            </svg>
            <span>Cite</span></a> <a
                href="/scholar?cites=12431652133523492930&amp;as_sdt=2005&amp;sciodt=0,5&amp;hl=en">Cited by 119</a> <a
                href="/scholar?q=related:QhDl7b8ZhqwJ:scholar.google.com/&amp;scioq=python&amp;hl=en&amp;as_sdt=0,5">Related
            articles</a> <a href="/scholar?cluster=12431652133523492930&amp;hl=en&amp;as_sdt=0,5" class="gs_nph">All 30
            versions</a> <a
                href="https://scholar.googleusercontent.com/scholar.bib?q=info:QhDl7b8ZhqwJ:scholar.google.com/&amp;output=citation&amp;scisdr=CgL8tDnCEMTS5YFttKQ:AAZF9b8AAAAAaENrrKRxlAx44kBSs0GnuPx1YsE&amp;scisig=AAZF9b8AAAAAaENrrIUEmQ9R2G61TAmYH0-fnQE&amp;scisf=4&amp;ct=citation&amp;cd=0&amp;hl=en"
                class="gs_nta gs_nph">Import into BibTeX</a> 
            <a href="javascript:void(0)" title="More" class="gs_or_mor" role="button">
                <svg viewBox="0 0 15 16" class="gs_or_svg">
                    <path d="M0.75 5.5l2-2L7.25 8l-4.5 4.5-2-2L3.25 8zM7.75 5.5l2-2L14.25 8l-4.5 4.5-2-2L10.25 8z"></path>
                </svg>
            </a>
        </div>
    </div>
</div>
```

Odczytywane wartości (opisane selektorami CSS):
- `.gs_rt a`
  - .text: tytuł publikacji
  - .href: link do publikacji
- `.gs_ctc`: typ pliku
- `.gs_a`: autorzy
- `a.gs_nta.gs_nph` (tekst musi być równy: "Import into BibTeX"): link do pliku bibtex

## Pobieranie i parsowanie BibTex

Dane pobrane ze stron HTML są niedokładne (skrócone do określonych długości). Program pobiera dane BibTex z wcześniej
zescrapowanych linków i na ich podstawie uzupełnia dane. Wysyłane żądanie na każdą pozycję:

```http request title="Pobieranie pliku BibTex dla pojedynczej pozycji"
GET https://scholar.googleusercontent.com/scholar.bib?q=info:QhDl7b8ZhqwJ:scholar.google.com/&output=citation&scisdr=CgL8tDnCEMTS5YFttKQ:AAZF9b8AAAAAaENrrKRxlAx44kBSs0GnuPx1YsE&scisig=AAZF9b8AAAAAaENrrIUEmQ9R2G61TAmYH0-fnQE&scisf=4&ct=citation&cd=0&hl=en
```

Do parsowania pliku program wykorzystuje bibliotekę [bibtexparser](https://github.com/sciunto-org/python-bibtexparser).