from itertools import cycle

from scholarly import scholarly, ProxyGenerator
from scholarly.data_types import Publication


class GoogleScholarScraper:
    # TODO: Turn scholarly into async

    def __init__(self, proxies: list[str] | None = None):
        if proxies is None:
            proxies = []
        self.count_of_proxies = len(proxies)
        self.proxies = cycle(proxies)

    def _use_next_proxy(self):
        if self.count_of_proxies <= 0:
            return
        pg = ProxyGenerator()
        next_proxy = next(self.proxies)
        pg.SingleProxy(http=next_proxy, https=next_proxy)
        # TODO: Fix httpx error (0.28 has breaking changes regarding proxies)
        scholarly.use_proxy(pg, pg)

    async def search(self, query: str) -> list[Publication]:
        results = []
        scholarly_query = scholarly.search_pubs(query)

        self._use_next_proxy()
        try:
            r = next(scholarly_query, 'end')
            while r != 'end':
                results.append(r)
                print(f'[GoogleScholarScraper] So far: {len(results)}; {r.get('bib').get('title')}')

                self._use_next_proxy()
                r = next(scholarly_query, 'end')
        except BaseException as e:
            # TODO: Rotate proxy on exception
            print(f'GoogleScholarScraper errored out after scraping {len(results)} results')
            print(e, type(e))
        
        return results