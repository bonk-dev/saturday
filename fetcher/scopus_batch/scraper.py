import asyncio
import itertools
import logging
import random
import string
from typing import Any, Optional

import httpx
from httpx import Cookies, URL, Proxy

from fetcher.scopus_batch import consts
from fetcher.scopus_batch.models import SearchEidsResult, ExportFileType, FieldGroupIdentifiers


class ScopusScraperConfig:
    """
    Configuration container for ScopusScraper authentication and session cookies.

    :param str user_agent:           The User-Agent header to present on requests.
    :param str scopus_jwt:           The JWT token for Scopus API authentication.
    :param str scopus_jwt_domain:    The SCOPUS_JWT cookie domain
    :param str awselb:               The AWSELB cookie value for load-balancer stickiness.
    :param str scopus_session_uuid:  The Scopus session UUID cookie value.
    :param str sc_session_id:        The SCSessionID cookie value.
    :ivar str user_agent:            See `user_agent` parameter.
    :ivar str scopus_jwt:            See `scopus_jwt` parameter.
    :ivar str scopus_jwt_domain:     See `scopus_jwt_domina` parameter.
    :ivar str awselb:                See `awselb` parameter.
    :ivar str scopus_session_uuid:   See `scopus_session_uuid` parameter.
    :ivar str sc_session_id:         See `sc_session_id` parameter.
    """
    def __init__(self, user_agent: str, scopus_jwt: str, scopus_jwt_domain: str, awselb: str, scopus_session_uuid: str, sc_session_id: str):
        self.user_agent = user_agent
        self.scopus_jwt = scopus_jwt
        self.scopus_jwt_domain = scopus_jwt_domain
        self.awselb = awselb
        self.scopus_session_uuid = scopus_session_uuid
        self.sc_session_id = sc_session_id

    def build_cookie_store(self) -> Cookies:
        """
        Build an `httpx.Cookies` object populated with the necessary Scopus cookies.

        :return: A cookie jar containing `SCSessionID`, `scopusSessionUUID`, `AWSELB`, `at_check`, and `SCOPUS_JWT`.
        :rtype: httpx.Cookies
        """
        cookies = Cookies({
            consts.COOKIE_SESSION_ID: self.sc_session_id,
            consts.COOKIE_SESSION_UUID: self.scopus_session_uuid,
            consts.COOKIE_AWSELB: self.awselb,
            consts.COOKIE_AT_CHECK: 'true'
        })
        # cookies.set('SCOPUS_JWT', self.scopus_jwt, domain='.scopus.com', path='/')
        cookies.set(consts.COOKIE_JWT, value=self.scopus_jwt, domain=self.scopus_jwt_domain, path='/')
        return cookies


class ScopusScraper:
    """
    Asynchronous scraper for Scopus document EID enumeration and export via the Scopus web interface.

    Uses an HTTPX AsyncClient with a cookie-based session, automatic JWT refresh, and
    batched export requests.

    :cvar str BASE_URI:                         Base URL for Scopus web interface.
    :cvar int __MAX_EIDS_PER_SEARCH__:         Maximum number of EIDs returned per search request.
    :cvar int __MAX_BATCH_ITEMS_PER_REQUEST__: Maximum number of EIDs per export batch request.
    :param ScopusScraperConfig config:         Configuration object with authentication and cookie data.
    :param bool verify_ssl:                    Whether to verify SSL certificates (default: True).
    """

    BASE_URI = 'https://www.scopus.com'

    # These are limits enforced by Scopus

    __MAX_EIDS_PER_SEARCH__ = 2000
    """Maximum `itemcount` value accepted by the `/api/documents/search/eids` endpoint."""

    __MAX_BATCH_ITEMS_PER_REQUEST__ = 100
    """Maximum number of items accepted by the `/gateway/export-service/export` endpoint."""

    def __init__(self, config: ScopusScraperConfig, verify_ssl: bool = True, base_uri: str = BASE_URI,
                 proxy: URL | str | Proxy | None = None):
        """
        Initialize the ScopusScraper.

        :param ScopusScraperConfig config:  Auth and cookie configuration.
        :param bool verify_ssl:             Toggle SSL certificate verification.
        :param str base_uri:         Override the base URI (default: BASE_URI).
        :param URL | str | Proxy | None proxy:  Proxy to use when making HTTP(S) requests.
        """

        self._base = base_uri
        self._session = httpx.AsyncClient(verify=verify_ssl, timeout=60, proxy=proxy,
                                          cookies=config.build_cookie_store())
        self._session.headers.update({
            'Accept': 'application/json',
            'User-Agent': config.user_agent
        })
        self._sessionId = config.sc_session_id
        self._nextTransactionId = 1
        self._logger = logging.getLogger(__name__)
        self._post_lock = asyncio.Lock()

        # keep config for JWT refresh
        self._config = config
        self._refreshed = False

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._session.aclose()

    async def search_eids(self, item_count: int, offset: int, query: str) -> SearchEidsResult:
        """
        Perform a document EID search on Scopus.

        :param int item_count:  Number of EIDs to retrieve in this request.
        :param int offset:      Zero-based offset of the first EID to retrieve.
        :param str query:       Scopus search query string (e.g. `"TITLE-ABS-KEY(...)"`).
        :raises RuntimeError:   If the HTTP response status indicates an error.
        :return: Parsed `SearchEidsResult` containing EID list and metadata.
        :rtype: SearchEidsResult
        """

        payload = {
            'documentClassificationEnum': 'primary',
            'itemcount': item_count,
            'offset': offset,
            'query': query,
            'sort': 'plf-f'
        }

        self._logger.debug(f'search_eids: {payload}')

        r = await self._post(f'{self._base}/api/documents/search/eids', json=payload)
        if r.is_error:
            raise RuntimeError(f'An error has occurred while searching for EIDs (code={r.status_code}): {r.text}')
        return SearchEidsResult(json_data=r.json())

    @staticmethod
    def get_batch_id_prefix() -> str:
        """
        Generate a random alphanumeric prefix for batch identifiers.

        :return: A 6-character string of lowercase letters and digits.
        :rtype: str
        """

        prefix_length = 6
        alphabet = string.ascii_lowercase + string.digits
        return ''.join(random.choice(alphabet) for i in range(prefix_length))

    @staticmethod
    def get_batch_id(exported: int, prefix: str | None = None):
        """
        Construct a batch ID based on the total exported count and an optional prefix.

        :param int exported:    Total number of EIDs already exported.
        :param str prefix:      Optional prefix; if `None`, a new one is generated.
        :return: Batch ID in the form `{prefix}_{block2000}_{block100}`.
        :rtype: str
        """

        if prefix is None:
            prefix = ScopusScraper.get_batch_id_prefix()
        block_2000_index = exported // ScopusScraper.__MAX_EIDS_PER_SEARCH__
        block_100_index = (exported - block_2000_index * ScopusScraper.__MAX_EIDS_PER_SEARCH__) // ScopusScraper.__MAX_BATCH_ITEMS_PER_REQUEST__
        return f'{prefix}_{block_2000_index}_{block_100_index}'

    async def export_part(self,
                          batch_id: str,
                          total_docs: int,
                          eids: list[str],
                          file_type: ExportFileType,
                          field_group_ids: list[FieldGroupIdentifiers],
                          locale: str = 'en-US',
                          hide_headers: bool = False) -> str:
        """
        Export a subset (“part”) of EIDs to the chosen file format.

        :param str batch_id:                   Unique batch identifier.
        :param int total_docs:                 Total number of documents being exported.
        :param list[str] eids:                List of EID strings for this part.
        :param ExportFileType file_type:       Desired export format (e.g. CSV, RIS).
        :param list[FieldGroupIdentifiers] field_group_ids: Fields to include.
        :param str locale:                    Locale code (default `'en-US'`).
        :param bool hide_headers:             Whether to omit column headers after the first page.
        :raises RuntimeError:                 If the HTTP response status indicates an error.
        :return: Raw text of the exported file part.
        :rtype: str
        """

        # TODO: 'transactionId' and 'primary' can be read from the Scopus JWT token
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
            'hideHeaders': hide_headers
        }
        self._logger.debug(f'export_part: {payload}')
        self._nextTransactionId += 1

        r = await self._post(f'{self._base}/gateway/export-service/export?batchId={batch_id}', json=payload)
        if r.is_error:
            raise RuntimeError(f'An error has occurred while exporting part (code={r.status_code}): {r.text}')
        return r.text

    async def export_all(self, title: str, file_type: ExportFileType, fields: list[FieldGroupIdentifiers]) -> str:
        """
        Export all search results for a given title, batching as necessary.

        1. Searches up to `__MAX_EIDS_PER_SEARCH__` EIDs.
        2. Splits into batches of `__MAX_BATCH_ITEMS_PER_REQUEST__`.
        3. Exports each batch in sequence, concatenating the text results.
        4. Continues fetching more EIDs until totalResults is reached.

        :param str title:                        Document title or query string.
        :param ExportFileType file_type:         Desired export file format.
        :param list[FieldGroupIdentifiers] fields: Field group identifiers to include.
        :return: Concatenated export text of all batches.
        :rtype: str
        """

        batch_prefix = ScopusScraper.get_batch_id_prefix()
        self._logger.debug(f"export_all: using {batch_prefix} as the batch prefix")

        query = f'TITLE-ABS-KEY({title})'

        # TODO: Handle timeouts
        eid_search_results = await self.search_eids(ScopusScraper.__MAX_EIDS_PER_SEARCH__, 0, query)
        all_eid_count = eid_search_results.response.num_found
        eids = eid_search_results.response.docs
        exported_eid_count = 0
        export_data = []

        self._logger.debug(f"export_all: EIDs to export: {all_eid_count}")

        while exported_eid_count < all_eid_count:
            for eid_batch in itertools.batched(eids, ScopusScraper.__MAX_BATCH_ITEMS_PER_REQUEST__):
                batch_id = ScopusScraper.get_batch_id(exported_eid_count, batch_prefix)
                self._logger.debug(f'export_all: batch_id: {batch_id}')

                batch_data = await self.export_part(
                    batch_id,
                    all_eid_count,
                    eid_batch,
                    file_type,
                    fields,
                    hide_headers=exported_eid_count > 0)
                self._logger.debug(f'export_all: batch_data: {batch_data}')
                export_data.append(batch_data)
                export_data.append('\n')

                exported_eid_count += len(eid_batch)
                self._logger.info(f'export_all: exported {exported_eid_count}/{all_eid_count}')
            self._logger.debug(f'export_all: researching EIDs (offset={exported_eid_count})')
            eid_search_results = await self.search_eids(ScopusScraper.__MAX_EIDS_PER_SEARCH__, exported_eid_count, query)
            all_eid_count = eid_search_results.response.num_found
            eids = eid_search_results.response.docs
            self._logger.debug(f'export_all: found {len(eids)} new EIDs')
        self._logger.info(f'export_all: exported total of {exported_eid_count} EIDs')
        return ''.join(export_data)

    async def _post(self, url: str, json: Any | None = None) -> httpx.Response:
        """
        Internal helper to serialize POST requests and refresh JWT if needed.

        Automatically refreshes the JWT on HTTP status 403, and retries the original request
        one time if the token was refreshed successfully.

        :param str url:         Full request URL.
        :param Any json:        JSON payload for the POST.
        :return: The HTTPX `Response` from the final attempt.
        :rtype: httpx.Response
        """

        async with self._post_lock:
            r = await self._session.post(url, json=json)
            if r.status_code == 403:
                refresh_successful = await self._refresh_jwt_token()
                if refresh_successful:
                    r = await self._session.post(url, json=json)
        return r

    async def _refresh_jwt_token(self) -> httpx.Response:
        """
        Refresh the Scopus JWT token by calling the refresh endpoint.

        :return: The HTTPX `Response` of the refresh request.
        :rtype: httpx.Response
        """

        self._logger.debug('Refreshing JWT token')
        r = await self._session.get(f'{self._base}/api/auth/refresh-scopus-jwt')
        if r.is_success:
            # HTTPX client auto-saves the new token from the Set-Cookie header
            self._logger.debug('Successfully refreshed JWT token')

            self._refreshed = True
            self._config = ScopusScraperConfig(
                user_agent=self._config.user_agent,
                scopus_jwt=self._session.cookies[consts.COOKIE_JWT],
                scopus_jwt_domain=self._config.scopus_jwt_domain,
                awselb=self._session.cookies[consts.COOKIE_AWSELB],
                scopus_session_uuid=self._session.cookies[consts.COOKIE_SESSION_UUID],
                sc_session_id=self._session.cookies[consts.COOKIE_SESSION_ID]
            )
        else:
            self._logger.error('An error has occurred while refreshing the Scopus JWT token')
            self._logger.error(r.text)
        return r

    def get_cookies(self) -> Optional[ScopusScraperConfig]:
        """
        Retrieve the current Scopus scraper configuration containing cookie data.

        This method returns the stored `ScopusScraperConfig` object only if the
        internal cookies have been refreshed since the last retrieval. If the
        cookies have not been refreshed (`self._refreshed` is False), this method
        returns `None`.

        :return: The `ScopusScraperConfig` containing valid cookie information if
                 refreshed; otherwise, `None`.
        :rtype: Optional[ScopusScraperConfig]
        """
        return self._config if self._refreshed else None
