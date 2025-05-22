import argparse
import asyncio
import http.cookies
import logging
import os

from dotenv import load_dotenv
from fetcher.scopus.api import ScopusApi
from fetcher.gscholar.scraper import GoogleScholarScraper
from database.dbContext import *
from database.scopusController import *
import json

from fetcher.scopus_batch.models import ExportFileType, all_identifiers
from fetcher.scopus_batch.parser import ScopusCsvParser
from fetcher.scopus_batch.scraper import ScopusScraper, ScopusScraperConfig


async def main():
    logging.basicConfig(level=logging.WARN)
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    load_dotenv()

    parser = argparse.ArgumentParser(description="Science publication metadata scraper")
    parser.add_argument('search_query', help='Generic search query to use when scraping metadata')
    parser.add_argument('-a', '--all', action='store_true', help='Use all methods (google-scholar, scopus)')
    parser.add_argument('-p', '--proxy',
                        action='append',
                        help='HTTP(S) proxy address, example: -p http://127.0.0.1:8080 -p http://127.0.0.2:1234. '
                             'Not used when making requests to IP-authenticated services (Elsevier, Scopus, etc.)')
    parser.add_argument('--debug-proxy',
                        help='HTTP(S) proxy address, used for ALL requests, including ones made to services based on '
                             'IP authentication (Elsevier, Scopus)')
    parser.add_argument('-g', '--google-scholar', action='store_true', help='Use Google Scholar for scraping metadata')
    parser.add_argument('-s', '--scopus-api', action='store_true', help='Use Scopus API for scraping metadata')
    parser.add_argument('-b', '--scopus-batch',
                        action='store_true',
                        help='Use Scopus batch export for scraping metadata')
    parser.add_argument('--scopus-batch-file', help='Use a local .CSV dump instead of exporting from Scopus')
    parser.add_argument('--ssl-insecure',
                        action='store_true',
                        help='Do not verify upstream server SSL/TLS certificates')
    args = parser.parse_args()

    search_query = args.search_query
    logger.info(f'Using "{search_query}" as the search query')

    prod_proxies = args.proxy
    debug_proxy = args.debug_proxy
    if debug_proxy:
        logger.info(f'Using debug proxy: "{debug_proxy}"')
        if prod_proxies and len(prod_proxies) > 0:
            logger.warning(f'Overwriting production proxies with the debug proxy')
            prod_proxies = [debug_proxy]

    use_scopus = args.scopus_api or args.all
    use_scopus_batch = args.scopus_batch or args.all
    use_gscholar = args.google_scholar or args.all

    if use_gscholar:
        scr = GoogleScholarScraper(verify_ssl=not args.ssl_insecure, proxies=prod_proxies)
        r = await scr.search(search_query)
        logger.debug(json.dumps(r))
        logger.debug(r)

    if use_scopus_batch:
        logger.debug('Using Scopus batch export')
        cookie_file_path = os.getenv('SCOPUS_BATCH_COOKIE_FILE')
        scopus_batch_uri = os.getenv('SCOPUS_BATCH_BASE')
        scopus_cookie_domain_name = os.getenv('SCOPUS_BATCH_COOKIE_JWT_DOMAIN')

        if not scopus_cookie_domain_name:
            logger.warning(f'Scopus batch: SCOPUS_BATCH_COOKIE_JWT_DOMAIN not set, defaulting to .scopus.com')
            scopus_cookie_domain_name = '.scopus.com'
        if not scopus_batch_uri:
            logger.warning(f'Scopus batch: SCOPUS_BATCH_BASE not set, defaulting to {ScopusScraper.BASE_URI}')
            scopus_batch_uri = ScopusScraper.BASE_URI

        export_data = None
        if args.scopus_batch_file is not None:
            logger.info(f'Scopus batch: reading from local file: {args.scopus_batch_file}')
            with open(args.scopus_batch_file, 'r') as b_file:
                export_data = b_file.read()
        elif not os.path.isfile(cookie_file_path):
            logger.error(f'Scopus batch: SCOPUS_BATCH_COOKIE_FILE file does not exist (path: "{cookie_file_path}")')
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
                logger.error('Scopus batch: SCOPUS_JWT cookie is required')
            elif not scopus_batch_awselb:
                logger.error('Scopus batch: AWSELB cookie is required')
            elif not scopus_batch_session_uuid:
                logger.error('Scopus batch: scopusSessionUUID cookie is required')
            elif not scopus_batch_sc_session_id:
                logger.error('Scopus batch: SCSessionID cookie is required')
            elif not scopus_batch_ua:
                logger.error('Scopus batch: User-Agent is required (must be same as used for logging in/CloudFlare '
                             'verification)')
            else:
                logger.info("All required Scopus batch cookies were found")
                async with ScopusScraper(ScopusScraperConfig(
                        user_agent=scopus_batch_ua,
                        scopus_jwt=scopus_batch_jwt.value,
                        scopus_jwt_domain=scopus_cookie_domain_name,
                        awselb=scopus_batch_awselb.value,
                        scopus_session_uuid=scopus_batch_session_uuid.value,
                        sc_session_id=scopus_batch_sc_session_id.value), verify_ssl=not args.ssl_insecure, base_uri=scopus_batch_uri) as sc_batch:
                    export_data = await sc_batch.export_all(
                        search_query,
                        file_type=ExportFileType.CSV,
                        fields=all_identifiers())
                    with open('/tmp/export.csv', 'w') as export_file:
                        export_file.write(export_data)
        if export_data is not None:
            logger.debug('Scopus batch: parsing data')
            # TODO: Find a more elegant solution for handling BOM?
            export_data = export_data.removeprefix('\ufeff')
            parser = ScopusCsvParser(export_data)

            scopus_batch_pubs = parser.read_all_publications()
            logger.info(f'Parsed publications: {len(scopus_batch_pubs)}')
            for pub in scopus_batch_pubs:
                logger.debug(pub.to_debug_string())

    if use_scopus:
        scopus_key = os.getenv('SCOPUS_API_KEY')
        scopus_base = os.getenv('SCOPUS_API_BASE')

        if scopus_base is None or scopus_base is None:
            logger.critical("Please set SCOPUS_API_KEY and SCOPUS_API_BASE in .env (check out .env.sample) or with "
                            "environment variables")
        else:
            async with ScopusApi(
                    api_key=scopus_key,
                    api_endpoint=scopus_base,
                    proxies=debug_proxy,
                    verify_ssl=not args.ssl_insecure) as client:
                r = await client.search(search_query)
                for entry in r:
                    logger.debug(entry)

            with app.app_context():
                init_app(app)
                scopusBatchInsert(r)

asyncio.run(main())
