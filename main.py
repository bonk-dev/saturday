import asyncio
import os

from dotenv import load_dotenv
from fetcher.scopus.api import ScopusApi


async def main():
    load_dotenv()

    scopus_key = os.getenv('SCOPUS_API_KEY')
    scopus_base = os.getenv('SCOPUS_API_BASE')

    if scopus_base is None or scopus_base is None:
        print("Please set SCOPUS_API_KEY and SCOPUS_API_BASE in .env (check out .env.sample) or with environment variables")
        return

    async with ScopusApi(api_key=scopus_key, api_endpoint=scopus_base) as client:
        r = await client.search('python3')
        for entry in r:
            print(entry)


asyncio.run(main())
