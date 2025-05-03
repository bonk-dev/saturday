import logging
import httpx

from fetcher.proxy.rotator import ProxyRotator
from fetcher.scopus.models import SearchResults, SearchEntry

SCOBUS_SEARCH_MAX_COUNT = 25


class ScopusApi:
    BASE_URI = 'https://api.elsevier.com'

    def __init__(self, api_key: str, api_endpoint: str | None = BASE_URI, verify_ssl: bool = True, proxies: list[str] | None = None):
        self._proxy_rotator = ProxyRotator(proxies=proxies)
        self._session = httpx.AsyncClient(proxy=self._proxy_rotator.use_next_proxy(), verify=verify_ssl)
        self._base = api_endpoint
        self._session.headers.update({
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.10 Safari/605.1.1',
            'X-ELS-APIKey': api_key
        })
        self._logger = logging.getLogger(__name__)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._session.aclose()

    async def search(self, title: str) -> list[SearchEntry]:
        self._logger.info(f'Searching (all pages) for "{title}"')

        first_page = await self.search_one_page(title)
        start_index = first_page.itemsPerPage
        entries_on_page = first_page.itemsPerPage

        entries = first_page.entry

        while (start_index + entries_on_page) < first_page.totalResults:
            start_index += min(first_page.itemsPerPage, first_page.totalResults - first_page.itemsPerPage)
            entries_on_page = min(first_page.itemsPerPage, first_page.totalResults - start_index)

            # TODO: Parallel?
            page = await self.search_one_page(title, start=start_index, count=entries_on_page)
            entries.extend(page.entry)
        return entries

    async def search_one_page(self, title: str, start: int = 0, count: int = SCOBUS_SEARCH_MAX_COUNT) -> SearchResults:
        self._logger.info(f'Searching (single page) for "{title}", start: {start}, count: {count}')

        if count > SCOBUS_SEARCH_MAX_COUNT:
            raise ValueError(f"Count must be less than SCOBUS_SEARCH_MAX_COUNT ({SCOBUS_SEARCH_MAX_COUNT}, but was {count})")

        query = self._build_search_query(title, start, count)
        self._logger.debug(f'Search query: {query}')

        response = await self._session.get(f'{self._base}/content/search/scopus', params=query)
        self._logger.debug(f'Response status: {str(response.status_code)}')
        self._logger.debug(f'Response text: {response.text}')

        return SearchResults(json_data=response.json())

    @staticmethod
    def _build_search_query(title: str, start: int, count: int) -> dict:
        return {
            'query': f'TITLE-ABS-KEY({title})',
            'view': 'COMPLETE',
            'start': str(start),
            'count': str(count)
        }
