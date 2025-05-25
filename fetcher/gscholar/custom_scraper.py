import logging
from itertools import cycle
from bs4 import BeautifulSoup
import httpx

from fetcher.gscholar.models import GoogleScholarHtmlEntry


class GoogleScholarScraperCustom:
    BASE_URI = 'https://scholar.google.com'

    def __init__(self, verify_ssl: bool = True, base_uri: str = BASE_URI,
                 proxies: list[str] | None = None,
                 user_agent: str | None = None):
        if proxies is None:
            proxies = []
        self._count_of_proxies = len(proxies)
        self._proxies = cycle(proxies)
        self._logger = logging.getLogger(__name__)

        self._session = httpx.AsyncClient(verify=verify_ssl, timeout=30, proxy=next(self._proxies))
        self._session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,'
                      '*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'User-Agent': user_agent if user_agent else 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                                                        '(KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36'
        })
        self._base = base_uri

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
        """

        uri = f'{self._base}/scholar'
        r = await self._session.get(uri, params={
            'start': str(start),
            'q': query,
            'hl': language,
            'as_sdt': as_sdt
        })
        self._logger.debug(f'search_scholar: status={r.status_code}')
        r.raise_for_status()

        s = BeautifulSoup(r.text, 'html.parser')
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
                file_type = file_type_element.find()
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
