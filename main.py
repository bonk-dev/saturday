import argparse
import asyncio
import logging
import os

from dotenv import load_dotenv
from fetcher.scopus.api import ScopusApi
from fetcher.gscholar.scraper import GoogleScholarScraper
from database.dbContext import *
from database.scopusController import *
import json


async def main():
    logging.basicConfig(level=logging.WARN)
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    load_dotenv()

    parser = argparse.ArgumentParser(description="Science publication metadata scraper")
    parser.add_argument('search_query', help='Generic search query to use when scraping metadata')
    parser.add_argument('-a', '--all', action='store_true', help='Use all methods (google-scholar, scopus)')
    parser.add_argument('-p', '--proxy', action='append', help='HTTP(S) proxy address, example: -p http://127.0.0.1:8080 -p http://127.0.0.2:1234')
    parser.add_argument('-g', '--google-scholar', action='store_true', help='Use Google Scholar for scraping metadata')
    parser.add_argument('-s', '--scopus-api', action='store_true', help='Use Scopus API for scraping metadata')
    parser.add_argument('--ssl-insecure', action='store_true', help='Do not verify upstream server SSL/TLS certificates')
    args = parser.parse_args()

    search_query = args.search_query
    logger.info(f'Using "{search_query}" as the search query')

    use_scopus = args.scopus_api or args.all
    use_gscholar = args.google_scholar or args.all

    if use_gscholar:
        scr = GoogleScholarScraper(verify_ssl=not args.ssl_insecure, proxies=args.proxy)
        r = await scr.search(search_query)
        logger.debug(json.dumps(r))
        logger.debug(r)

    if use_scopus:
        scopus_key = os.getenv('SCOPUS_API_KEY')
        scopus_base = os.getenv('SCOPUS_API_BASE')

        if scopus_base is None or scopus_base is None:
            logger.critical("Please set SCOPUS_API_KEY and SCOPUS_API_BASE in .env (check out .env.sample) or with environment variables")
        else:
            async with ScopusApi(
                    api_key=scopus_key,
                    api_endpoint=scopus_base,
                    proxies=args.proxy,
                    verify_ssl=not args.ssl_insecure) as client:
                r = await client.search(search_query)
                for entry in r:
                    logger.debug(entry)

            with app.app_context():
                init_app(app)
                scopusBatchInsert(r)

asyncio.run(main())
