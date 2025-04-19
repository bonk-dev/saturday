from scholarly import scholarly
from scholarly.data_types import Publication


class GoogleScholarScraper:
    # TODO: Turn scholarly into async
    # TODO: Add better handling of manually supplied list of proxies to scholarly
    async def search(self, query: str) -> list[Publication]:
        results = []
        scholarly_query = scholarly.search_pubs(query)

        try:
            r = next(scholarly_query, 'end')
            while r != 'end':
                results.append(r)
                r = next(scholarly_query, 'end')
        except e:
            print(f'GoogleScholarScraper errored out after scraping {len(results)} results')
            print(e)
        
        return results