import itertools
import logging
import os
import sys
from typing import Any

import httpx
from httpx import RequestError

from cli.options import ProxiesFetcherOptions, FetcherModuleResult
from fetcher.gscholar.bibtex_parser import parse_bibtex_entry, merge_entries
from fetcher.gscholar.scraper import GoogleScholarScraper, CaptchaError

ENV_BASE_URI = 'GOOGLE_SCHOLAR_BASE'
ENV_USER_AGENT = 'GOOGLE_SCHOLAR_USER_AGENT'


async def use(options: ProxiesFetcherOptions) -> FetcherModuleResult:
    logger = logging.getLogger(__name__)

    gscholar_base = os.getenv(ENV_BASE_URI)
    gscholar_ua = os.getenv(ENV_USER_AGENT)

    scr = GoogleScholarScraper(verify_ssl=options.verify_ssl,
                               base_uri=gscholar_base,
                               user_agent=gscholar_ua)

    rotate_proxy = False
    proxies_list = options.proxies if options.proxies and len(options.proxies) > 0 else [None]
    proxy_cycle = itertools.cycle(proxies_list)

    gscholar_proxy = next(proxy_cycle)

    try:
        await scr.init(proxy=gscholar_proxy)
    except RequestError as r_error:
        logger.error(f'proxy={gscholar_proxy}')
        logger.error(f'during client init, an error has occured: error={r_error}')
        rotate_proxy = True

    page = 0
    merged_entries = []
    while True:
        if rotate_proxy:
            logger.warning(f'changing proxy: new_proxy=')
            if len(proxies_list) <= 1:
                logger.error('no proxies or just one, stopping the scraping operation')
                break
            else:
                gscholar_proxy = next(proxy_cycle)
                await scr.aclose()
                try:
                    await scr.init(proxy=gscholar_proxy)
                except RequestError as r_error:
                    logger.error(f'during proxy rotation, an error has occured: error={r_error}')
                    continue
        scraped_entries = []
        try:
            scraped_entries = await scr.search_scholar(options.search_query, start=page)
        except CaptchaError:
            logger.error(f'during searching page={page}, Google Scholar requested a CAPTCHA verification')
            rotate_proxy = True
        except RequestError as r_error:
            logger.error(f'during searching page={page}, an error has occured: error={r_error}')
            rotate_proxy = True

        if rotate_proxy:
            continue

        last_scraped_entries = len(scraped_entries)

        if last_scraped_entries <= 0:
            logger.info('all done!')
            break

        logger.info(f'page={page}, scraped_entries={len(scraped_entries)}')
        page += 10

        bibs = []
        for entry in scraped_entries:
            bibtex_entry = await scr.scrape_bibtex_file(entry)
            logger.debug(f'bibtext entry for id={entry.id!r}: {bibtex_entry!r}')

            parsed_bib_entry = parse_bibtex_entry(bibtex_entry)
            bibs.append(parsed_bib_entry)
        merged_entries.extend(merge_entries(scraped_entries, bibs))
    return FetcherModuleResult(module=__name__, results=merged_entries)
