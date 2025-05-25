import logging
from itertools import cycle
from bs4 import BeautifulSoup
import httpx
from fetcher.gscholar.models import GoogleScholarHtmlEntry, GoogleScholarBibtexScrapeEntry


class CaptchaError(Exception):
    pass


class GoogleScholarScraperCustom:
    BASE_URI = 'https://scholar.google.com'
    _session: httpx.AsyncClient | None

    def __init__(self, verify_ssl: bool = True, base_uri: str = BASE_URI,
                 user_agent: str | None = None):
        self._logger = logging.getLogger(__name__)

        self._verify_ssl = verify_ssl
        self._ua = user_agent
        self._base = base_uri
        self._session = None

    async def init(self, proxy: str | None = None):
        self._session = httpx.AsyncClient(verify=self._verify_ssl, timeout=30, proxy=proxy)
        self._session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,'
                      '*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'User-Agent': self._ua if self._ua else 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                                                    '(KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36'
        })

        await self.get_initial_cookies()
        await self.set_preferences()

    async def get_initial_cookies(self):
        """
        Perform an initial GET request to the base URI to retrieve and store any required cookies.

        This method initializes the session by requesting the base page, which may set cookies needed
        for subsequent operations.

        :returns: None
        :rtype: None
        :raises httpx.HTTPStatusError: If the GET request returns an unsuccessful status code.
        """

        self._logger.debug('get_initial_cookies')
        r = await self._session.get(f'{self._base}/')
        r.raise_for_status()
        self._logger.debug('get_initial_cookies: ok')

    async def set_preferences(self):
        """
        Configure Google Scholar preferences to include citation links and any library access settings.
        It requests the settings page (`scholar_settings`), parses the HTML form to extract the `scisig`
        and `inst` values and submits the preferences form (`scholar_setprefs`) to apply settings such
        as citation links, library access, and language. This saves doing multiple requests for each entry.

        :returns: None
        :rtype: None
        :raises httpx.HTTPStatusError: If any of the HTTP requests return an unsuccessful status code.
        """

        settings_page_r = await self._session.get(f'{self._base}/scholar_settings', params={
            'hl': 'en',
            'as_sdt': '0,5'
        })
        self._logger.debug(f'set_preferences: HTML page, status={settings_page_r.status_code}')
        settings_page_r.raise_for_status()

        s = BeautifulSoup(settings_page_r.text, 'html.parser')
        form_e = s.find('form', attrs={'id': 'gs_bdy_frm'})
        scisig_e = form_e.find('input', attrs={'name': 'scisig'})
        scisig = scisig_e.attrs['value']

        inst_e = (s
                  .find('div', attrs={'id': 'gs_settings_liblinks_lst'})
                  .find('input', attrs={'name': 'inst'}))
        inst_val = inst_e.attrs['value']

        self._logger.debug(f'set_preferences: scisig={scisig}')

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

    async def search_scholar(self, query: str, start: int = 0, as_sdt: str = '0,5', language: str = 'en') \
            -> list[GoogleScholarHtmlEntry]:
        """
        Search Google Scholar for a given query and parse the resulting entries.

        :param query: The search query string to submit to Google Scholar.
        :type query: str
        :param start: The index of the first result to return (used for pagination). Defaults to 0.
        :type start: int
        :param as_sdt: Restriction parameter for Google Scholar to include certain content types. Defaults to '0,5'.
        :type as_sdt: str
        :param language: The language code for the search interface. Defaults to 'en' (English).
        :type language: str
        :returns: list[GoogleScholarHtmlEntry]
        :rtype: None
        :raises httpx.HTTPStatusError: If the search request returns an unsuccessful status code.
        :raises RuntimeError: If the 'Import into BibTeX' link cannot be located in a result entry.
        :raises from fetcher.gscholar.custom_scraper.CaptchaError: When Google Scholar requests a captcha check
        """

        uri = f'{self._base}/scholar'
        r = await self._session.get(uri, params={
            'start': str(start),
            'q': query,
            'hl': language,
            'as_sdt': as_sdt,
            'as_vis': '1'  # exclude "citations"
        })
        self._logger.debug(f'search_scholar: status={r.status_code}')
        r.raise_for_status()

        s = BeautifulSoup(r.text, 'html.parser')
        captcha_form = s.find('form', attrs={'id': 'gs_captcha_f'})
        if captcha_form is not None:
            raise CaptchaError('Google Scholar requested a captcha verification')

        entries = s.find_all(attrs={'class': 'gs_r gs_or gs_scl'})

        scraped_entries = []
        for e in entries:
            data_id = e.attrs['data-cid']
            title_element = e.find(attrs={'class': 'gs_rt'}).find('a')
            title = title_element.text
            entry_link = title_element.attrs['href']
            file_type_element = e.find(attrs={'class': 'gs_ctc'})
            if file_type_element is not None:
                # gs_ctc usually contains one visible text element, and one hidden
                # if you would do file_type_element, you would get duplicated file type
                file_type_element = file_type_element.find()
                if file_type_element is not None:
                    file_type = file_type_element.text
            else:
                file_type = ''
            authors = e.find(attrs={'class': 'gs_a'}).text

            import_bibtex_e = e.find('a', attrs={'class': 'gs_nta gs_nph'}, string='Import into BibTeX')
            if import_bibtex_e is None:
                raise RuntimeError('Could not find Import into BibTex anchor. Make sure you set the preferences!')
            bibtex_uri = import_bibtex_e.attrs['href']

            scr_entry = GoogleScholarHtmlEntry(id=data_id, title=title, authors=authors, link=entry_link,
                                               file_type=file_type, bibtex_uri=bibtex_uri)
            scraped_entries.append(scr_entry)
            self._logger.debug('search_scholar: ' + scr_entry.to_debug_string())
        return scraped_entries

    async def scrape_bibtex_file(self, entry: GoogleScholarHtmlEntry) -> GoogleScholarBibtexScrapeEntry:
        r = await self._session.get(entry.bibtex_uri)
        if r.status_code == 403:
            raise CaptchaError('Google Scholar returned 403 on BibTex download, probably triggered a captcha')
        r.raise_for_status()

        bib_entry = GoogleScholarBibtexScrapeEntry(id=entry.id, bibtex_data=r.text)
        self._logger.debug(f'scrape_bibtex_files: id={entry.id}, bibtex={r.text}')
        return bib_entry
