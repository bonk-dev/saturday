import logging
from itertools import cycle

from scholarly import scholarly, ProxyGenerator
from scholarly.data_types import Publication


class GoogleScholarScraper:
    # TODO: Turn scholarly into async

    def __init__(self, verify_ssl: bool = True, proxies: list[str] | None = None):
        if proxies is None:
            proxies = []
        self.count_of_proxies = len(proxies)
        self.proxies = cycle(proxies)
        self._logger = logging.getLogger(__name__)
        self._verify_ssl = verify_ssl

    def _use_next_proxy(self):
        if self.count_of_proxies <= 0:
            return
        pg = ProxyGenerator()
        next_proxy = next(self.proxies)
        self._logger.debug(f'Next proxy: {next_proxy}')
        pg.SingleProxy(http=next_proxy, https=next_proxy, verify=self._verify_ssl)
        scholarly.use_proxy(pg, pg)

    async def search(self, query: str) -> list[Publication]:
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
