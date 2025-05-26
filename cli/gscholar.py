import logging
import os
from typing import Any

from cli.options import ProxiesFetcherOptions, FetcherModuleResult
from fetcher.gscholar.bibtex_parser import parse_bibtex_entry, merge_entries
from fetcher.gscholar.scraper import GoogleScholarScraper


ENV_BASE_URI = 'GOOGLE_SCHOLAR_BASE'
ENV_USER_AGENT = 'GOOGLE_SCHOLAR_USER_AGENT'


async def use(options: ProxiesFetcherOptions) -> FetcherModuleResult:
    logger = logging.getLogger(__name__)

    gscholar_base = os.getenv(ENV_BASE_URI)
    gscholar_ua = os.getenv(ENV_USER_AGENT)

    scr = GoogleScholarScraper(verify_ssl=options.verify_ssl,
                               base_uri=gscholar_base,
                               user_agent=gscholar_ua)

    # TODO: Rotate proxies on captcha or error
    gscholar_proxy = options.proxies[0] if options.proxies and len(options.proxies) > 0 else None
    await scr.init(proxy=gscholar_proxy)

    page = 0
    merged_entries = []
    while True:
        scraped_entries = await scr.search_scholar(options.search_query, start=page)
        last_scraped_entries = len(scraped_entries)

        if last_scraped_entries <= 0:
            logger.info('all done!')
            break

        logger.info(f'page={page}, scraped_entries={len(scraped_entries)}')
        page += 10

        bibs = []
        for entry in scraped_entries:
            bibtex_entry = await scr.scrape_bibtex_file(entry)
            logger.info(f'bibtext entry for id={entry.id!r}: {bibtex_entry!r}')

            parsed_bib_entry = parse_bibtex_entry(bibtex_entry)
            bibs.append(parsed_bib_entry)
            logger.info(parsed_bib_entry)

        merged_entries.extend(merge_entries(scraped_entries, bibs))
    return FetcherModuleResult(module=__name__, results=merged_entries)
