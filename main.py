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

    load_dotenv()

    parser = argparse.ArgumentParser(description="Science publication metadata scraper")
    parser.add_argument('-a', '--all', action='store_true', help='Use all methods (google-scholar, scopus)')
    parser.add_argument('-g', '--google-scholar', action='store_true', help='Use Google Scholar for scraping metadata')
    parser.add_argument('-s', '--scopus-api', action='store_true', help='Use Scopus API for scraping metadata')
    args = parser.parse_args()

    use_scopus = args.scopus_api or args.all
    use_gscholar = args.google_scholar or args.all

    if use_gscholar:
        scr = GoogleScholarScraper(proxies=['http://127.0.0.1:8080'])
        r = await scr.search('python3 c++ wulkan')
        print(json.dumps(r))
        print(r)

    if use_scopus:
        scopus_key = os.getenv('SCOPUS_API_KEY')
        scopus_base = os.getenv('SCOPUS_API_BASE')

        if scopus_base is None or scopus_base is None:
            print("Please set SCOPUS_API_KEY and SCOPUS_API_BASE in .env (check out .env.sample) or with environment variables")
            return

        async with ScopusApi(api_key=scopus_key, api_endpoint=scopus_base) as client:
            r = await client.search('python3')
            for entry in r:
                print(entry)

        with app.app_context():
            init_app(app)
            scopusBatchInsert(r)

asyncio.run(main())
