import argparse
import asyncio
import logging

from dotenv import load_dotenv

from cli import gscholar, scopus_batch, elsevier_api
from cli.options import ProxiesFetcherOptions, FetcherModuleResult
from database.dbContext import *
from database.dbInsertsAIOptimised.gscholarAPIInsert import scholarInsertOptimised
from database.dbInsertsAIOptimised.scopusApiInsertOptimised import scopusAPIInsertOptimised
from database.dbInsertsAIOptimised.scopusBatchInsertOptimised import scopusBatchInsertOptimised


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
    parser.add_argument('--scopus-api-output',
                        help='Path to a file where raw data fetched from Elsevier API will be saved. File type: JSON.')

    parser.add_argument('-b', '--scopus-batch',
                        action='store_true',
                        help='Use Scopus batch export for scraping metadata')
    parser.add_argument('--scopus-batch-file', help='Use a local .CSV dump instead of exporting from Scopus')
    parser.add_argument('--scopus-batch-output',
                        help='Path to a file where raw data fetched from Scopus batch export will be saved. '
                             'File type: CSV.')
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
    scopus_api_output_path = args.scopus_api_output

    use_scopus_batch = args.scopus_batch or args.all
    scopus_batch_input_file = args.scopus_batch_file
    scopus_batch_output_path = args.scopus_batch_output

    use_gscholar = args.google_scholar or args.all

    fetcher_options = ProxiesFetcherOptions(verify_ssl=not args.ssl_insecure,
                                            search_query=search_query,
                                            proxies=prod_proxies,
                                            debug_proxy=debug_proxy)
    scrapers_tasks = []
    if use_gscholar:
        scrapers_tasks.append(gscholar.use(fetcher_options))

    if use_scopus_batch:
        scrapers_tasks.append(scopus_batch.use(fetcher_options,
                                               raw_output_path=scopus_batch_output_path,
                                               input_file_path=scopus_batch_input_file))
    if use_scopus:
        scrapers_tasks.append(elsevier_api.use(fetcher_options,
                                               output_path=scopus_api_output_path))

    # noinspection PyTypeChecker
    done_tasks: list[FetcherModuleResult] = await asyncio.gather(*scrapers_tasks)

    with app.app_context():
        init_app(app)
        for task in done_tasks:
            if task.module == 'cli.elsevier_api':
                scopusAPIInsertOptimised(task.results)
            elif task.module == 'cli.gscholar':
                logger.debug(task.results)
                scholarInsertOptimised(task.results)
            elif task.module == 'cli.scopus_batch':
                scopusBatchInsertOptimised(task.results)


asyncio.run(main())
