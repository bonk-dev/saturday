import logging
from itertools import cycle

from scholarly import scholarly, ProxyGenerator
from scholarly.data_types import Publication


class GoogleScholarScraper:
    """
    Scraper for searching publications from Google Scholar via the `scholarly` library.

    Supports toggling SSL verification, and collects results into a list
    of `Publication` objects.
    """

    def __init__(self, verify_ssl: bool = True, proxies: list[str] | None = None):
        """
        Initialize a new GoogleScholarScraper instance.

        :param bool verify_ssl: Toggle SSL certificate verification (default: ``True``).
        :param list[str] | None proxies: Proxy URLs to rotate through (default: ``None``).
        """
        if proxies is None:
            proxies = []
        self.count_of_proxies = len(proxies)
        self.proxies = cycle(proxies)
        self._logger = logging.getLogger(__name__)
        self._verify_ssl = verify_ssl

    def _use_next_proxy(self):
        """
        Rotate to the next proxy in the cycle and configure `scholarly` to use it.

        If no proxies were provided, this method does nothing.

        :raises ValueError: If the next proxy URL is invalid (propagates from ProxyGenerator).
        """
        if self.count_of_proxies <= 0:
            return
        pg = ProxyGenerator()
        next_proxy = next(self.proxies)
        self._logger.debug(f'Next proxy: {next_proxy}')
        pg.SingleProxy(http=next_proxy, https=next_proxy, verify=self._verify_ssl)
        scholarly.use_proxy(pg, pg)

    async def search(self, query: str) -> list[Publication]:
        """
        Search Google Scholar for the given query string.

        Rotates proxies between each page of results, collects all
        `Publication` objects, and logs progress. If an error occurs,
        logs the error and returns whatever was collected so far.

        :param str query: The search query to submit to Google Scholar.
        :return: List of publications matching the query.
        :rtype: list[Publication]
        :raises scholarly.ScholarlyException: If `scholarly` raises on setup or iteration.
        """

        self._logger.info(f'Searching for {query}')
        results = []

        try:
            self._use_next_proxy()
            scholarly_query = scholarly.search_pubs(query)

            r = next(scholarly_query, 'end')
            while r != 'end':
                results.append(r)
                self._logger.debug(f'So far: {len(results)}; {r.get('bib').get('title')}')

                self._use_next_proxy()
                r = next(scholarly_query, 'end')
        except BaseException as e:
            # TODO: Rotate proxy on exception
            self._logger.error(f'GoogleScholarScraper errored out after scraping {len(results)} results')
            self._logger.error(e, type(e))

        return results
