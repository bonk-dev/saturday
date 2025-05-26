import http.cookies
import logging
import os
from typing import Optional, Any

from cli.options import CommonFetcherOptions, FetcherModuleResult
from cli.utils import write_dump
from fetcher.scopus_batch.models import ExportFileType, all_identifiers
from fetcher.scopus_batch.parser import ScopusCsvParser
from fetcher.scopus_batch.scraper import ScopusScraper, ScopusScraperConfig

ENV_BATCH_COOKIE_FILE = 'SCOPUS_BATCH_COOKIE_FILE'
ENV_BATCH_BASE = 'SCOPUS_BATCH_BASE'
ENV_BATCH_COOKIE_JWT_DOMAIN = 'SCOPUS_BATCH_COOKIE_JWT_DOMAIN'


async def use(options: CommonFetcherOptions,
              input_file_path:Optional[str] = None,
              raw_output_path: Optional[str] = None) -> FetcherModuleResult:
    logger = logging.getLogger(__name__)

    logger.debug('using Scopus batch export')
    cookie_file_path = os.getenv(ENV_BATCH_COOKIE_FILE)
    scopus_batch_uri = os.getenv(ENV_BATCH_BASE)
    scopus_cookie_domain_name = os.getenv(ENV_BATCH_COOKIE_JWT_DOMAIN)

    if not scopus_cookie_domain_name:
        logger.warning(f'SCOPUS_BATCH_COOKIE_JWT_DOMAIN not set, defaulting to .scopus.com')
        scopus_cookie_domain_name = '.scopus.com'
    if not scopus_batch_uri:
        logger.warning(f'SCOPUS_BATCH_BASE not set, defaulting to {ScopusScraper.BASE_URI}')
        scopus_batch_uri = ScopusScraper.BASE_URI

    export_data = None
    if input_file_path is not None:
        logger.info(f'reading from local file: {input_file_path}')
        with open(input_file_path, 'r') as b_file:
            export_data = b_file.read()
    elif not os.path.isfile(cookie_file_path):
        logger.error(f'SCOPUS_BATCH_COOKIE_FILE file does not exist (path: "{cookie_file_path}")')
    else:
        with open(cookie_file_path, 'r') as cookie_file_f:
            cookie_file = cookie_file_f.read()
        cookies = http.cookies.SimpleCookie(cookie_file)
        cookies.load(cookie_file)

        scopus_batch_jwt = cookies.get('SCOPUS_JWT')
        scopus_batch_awselb = cookies.get('AWSELB')
        scopus_batch_session_uuid = cookies.get('scopusSessionUUID')
        scopus_batch_sc_session_id = cookies.get('SCSessionID')
        scopus_batch_ua = os.getenv('SCOPUS_BATCH_USER_AGENT')

        if not scopus_batch_jwt:
            logger.error('SCOPUS_JWT cookie is required')
        elif not scopus_batch_awselb:
            logger.error('AWSELB cookie is required')
        elif not scopus_batch_session_uuid:
            logger.error('scopusSessionUUID cookie is required')
        elif not scopus_batch_sc_session_id:
            logger.error('SCSessionID cookie is required')
        elif not scopus_batch_ua:
            logger.error('User-Agent is required (must be same as used for logging in/CloudFlare verification)')
        else:
            logger.info("all required Scopus batch cookies were found")
            async with ScopusScraper(ScopusScraperConfig(user_agent=scopus_batch_ua,
                                                         scopus_jwt=scopus_batch_jwt.value,
                                                         scopus_jwt_domain=scopus_cookie_domain_name,
                                                         awselb=scopus_batch_awselb.value,
                                                         scopus_session_uuid=scopus_batch_session_uuid.value,
                                                         sc_session_id=scopus_batch_sc_session_id.value),
                                     verify_ssl=options.verify_ssl,
                                     base_uri=scopus_batch_uri,
                                     proxy=options.debug_proxy) as sc_batch:
                export_data = await sc_batch.export_all(
                    options.search_query,
                    file_type=ExportFileType.CSV,
                    fields=all_identifiers())
                if raw_output_path:
                    write_dump(
                        raw_output_path,
                        export_data,
                        f_module=__name__,
                        logger=logger)
    if export_data:
        logger.debug('parsing data')
        # TODO: Find a more elegant solution for handling BOM?
        export_data = export_data.removeprefix('\ufeff')
        parser = ScopusCsvParser(export_data)

        scopus_batch_pubs = parser.read_all_publications()
        logger.info(f'parsed publications: {len(scopus_batch_pubs)}')
        for pub in scopus_batch_pubs:
            logger.debug(pub.to_debug_string())
    else:
        scopus_batch_pubs = []
    return FetcherModuleResult(module=__name__, results=scopus_batch_pubs)
