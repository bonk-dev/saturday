import logging
import urllib.parse
import httpx
from fetcher.scopus_batch.models import SearchEidsResult, ExportFileType, FieldGroupIdentifiers


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
        self._sessionId = config.sc_session_id
        self._nextTransactionId = 1
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

        # TODO: Refresh JWT on 403, or throw error
        r = await self._session.post(f'{self.__BASE__}/api/documents/search/eids', json=payload)
        return SearchEidsResult(json_data=r.json())

    async def export_part(self,
                          batch_id: str,
                          total_docs: int,
                          eids: list[str],
                          file_type: ExportFileType,
                          field_group_ids: list[FieldGroupIdentifiers],
                          locale: str = 'en-US') -> str:
        # payload.keyEvent:
        # transactionId: Filled with data from JS window.PlatformData. Doesn't need to be correct
        # primary: Filled with data from JS window.ScopusUser. Not required
        payload = {
            'eids': eids,
            'fileType': file_type.value,
            'fieldGroupIdentifiers': list(map(lambda i: i.value, field_group_ids)),
            'keyEvent': {
                'sessionId': self._sessionId,
                'transactionId': self._sessionId + ':' + str(self._nextTransactionId),  # Read comment above
                'origin': 'resultsList',
                'zone': 'resultsListHeader',
                'primary': '',  # Read comment above
                'totalDocs': total_docs
            },
            'locale': locale,
            'hideHeaders': False
        }
        self._logger.debug(f'export_part: {payload}')
        self._nextTransactionId += 1

        # TODO: Refresh JWT on 403, or throw error
        r = await self._session.post(f'{self.__BASE__}/gateway/export-service/export?batchId={batch_id}', json=payload)
        return r.text
