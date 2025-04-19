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
                print(f'[GoogleScholarScraper] So far: {len(results)}; {r.get('bib').get('title')}')

                r = next(scholarly_query, 'end')
        except BaseException as e:
            print(f'GoogleScholarScraper errored out after scraping {len(results)} results')
            print(e, type(e))
        
        return results