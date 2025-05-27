import itertools
import logging
import os
import sys
from typing import Any, Iterator

import httpx
from httpx import RequestError

from cli.options import ProxiesFetcherOptions, FetcherModuleResult
from fetcher.gscholar.bibtex_parser import parse_bibtex_entry, merge_entries
from fetcher.gscholar.models import GoogleScholarHtmlEntry
from fetcher.gscholar.scraper import GoogleScholarScraper, CaptchaError

ENV_BASE_URI = 'GOOGLE_SCHOLAR_BASE'
ENV_USER_AGENT = 'GOOGLE_SCHOLAR_USER_AGENT'


async def _download_bibtex_entries(html_entries: list[GoogleScholarHtmlEntry],
                                   logger: logging.Logger,
                                   scr: GoogleScholarScraper,
                                   proxy_cycle: Iterator):
    bibs = []
    rotate_proxy = False
    for entry in html_entries:
        # whether to retry current entry
        retry = True

        while retry:
            if rotate_proxy:
                gscholar_proxy = next(proxy_cycle, None)
                if gscholar_proxy is None:
                    logger.error('no more proxies')
                    return bibs
                logger.warning(f'changing proxy, next proxy={gscholar_proxy}')
                await scr.aclose()
                try:
                    await scr.init(proxy=gscholar_proxy)
                    rotate_proxy = False
                except RequestError as r_error:
                    logger.error(f'during proxy rotation, an error has occured: error={r_error}')
                    continue
            try:
                bibtex_entry = await scr.scrape_bibtex_file(entry)
                logger.debug(f'bibtext entry for id={entry.id!r}: {bibtex_entry!r}')

                parsed_bib_entry = parse_bibtex_entry(bibtex_entry)
                bibs.append(parsed_bib_entry)
                retry = False
            except CaptchaError:
                logger.error(f'during BibTex (id={entry.id}), Google Scholar requested a CAPTCHA verification')
                rotate_proxy = True
            except RequestError as r_error:
                logger.error(f'during BibTex (id={entry.id}), an error has occured: error={r_error}')
                rotate_proxy = True
    return bibs


async def use(options: ProxiesFetcherOptions) -> FetcherModuleResult:
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    gscholar_base = os.getenv(ENV_BASE_URI)
    gscholar_ua = os.getenv(ENV_USER_AGENT)

    scr = GoogleScholarScraper(verify_ssl=options.verify_ssl,
                               base_uri=gscholar_base,
                               user_agent=gscholar_ua)

    rotate_proxy = False
    proxies_list = options.proxies if options.proxies and len(options.proxies) > 0 else [None]
    proxy_cycle = iter(proxies_list)

    gscholar_proxy = next(proxy_cycle)

    try:
        await scr.init(proxy=gscholar_proxy)
    except RequestError as r_error:
        logger.error(f'proxy={gscholar_proxy}')
        logger.error(f'during client init, an error has occured: error={r_error}')
        rotate_proxy = True

    page = 0
    all_scraped_entries = []
    while True:
        if rotate_proxy:
            logger.warning(f'changing proxy')
            gscholar_proxy = next(proxy_cycle, None)
            if gscholar_proxy is None:
                logger.error('no more proxies')
                break
            logger.warning(f'changing proxy, next proxy={gscholar_proxy}')
            await scr.aclose()
            try:
                await scr.init(proxy=gscholar_proxy)
                rotate_proxy = False
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
            break
        all_scraped_entries.extend(scraped_entries)
        logger.info(f'page={page}, all={len(all_scraped_entries)}, scraped_entries={len(scraped_entries)}')
        page += 10
    logger.info('HTML scraping done!')

    bibs = await _download_bibtex_entries(html_entries=all_scraped_entries,
                                          logger=logger,
                                          proxy_cycle=proxy_cycle,
                                          scr=scr)

    merged_entries = merge_entries(all_scraped_entries, bibs)
    return FetcherModuleResult(module=__name__, results=merged_entries)
