import logging
import urllib.parse
import httpx
from fetcher.scopus_batch.models import SearchEidsResult


class ScopusScraperConfig:
    def __init__(self, user_agent: str, scopus_jwt: str, awselb: str, scopus_session_uuid: str, sc_session_id: str):
        self.user_agent = user_agent
        self.scopus_jwt = scopus_jwt
        self.awselb = awselb
        self.scopus_session_uuid = scopus_session_uuid
        self.sc_session_id = sc_session_id

    def build_cookie_header(self) -> str:
        return (f'SCSessionID={urllib.parse.quote(self.sc_session_id)}; '
                f'scopusSessionUUID={urllib.parse.quote(self.scopus_session_uuid)}; '
                f'AWSELB={urllib.parse.quote(self.awselb)}; '
                f'SCOPUS_JWT={urllib.parse.quote(self.scopus_jwt)}; '
                f'at_check=true')


class ScopusScraper:
    BASE_URI = 'https://api.elsevier.com'

    def __init__(self, config: ScopusScraperConfig, verify_ssl: bool = True):
        self.__BASE__ = 'https://www.scopus.com'
        self._session = httpx.AsyncClient(verify=verify_ssl, proxy="http://localhost:8080", timeout=30)
        self._session.headers.update({
            'Accept': 'application/json',
            'User-Agent': config.user_agent,
            'Cookie': config.build_cookie_header()
        })
        self._logger = logging.getLogger(__name__)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._session.aclose()

    async def search_eids(self, item_count: int, offset: int, query: str) -> SearchEidsResult:
        payload = {
            'documentClassificationEnum': 'primary',
            'itemcount': item_count,
            'offset': offset,
            'query': query,
            'sort': 'plf-f'
        }

        self._logger.debug(f'search_eids: {payload}')

        r = await self._session.post(f'{self.__BASE__}/api/documents/search/eids', json=payload)
        return SearchEidsResult(json_data=r.json())
