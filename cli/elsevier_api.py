import json
import logging
import os
from typing import Optional

from httpx import NetworkError, HTTPError

from cli.options import CommonFetcherOptions, FetcherModuleResult
from cli.utils import write_dump
from fetcher.exceptions import InvalidAPIKeyError
from fetcher.scopus.api import ScopusApi
from fetcher.scopus.models import SearchEntry


async def use(options: CommonFetcherOptions, output_path: Optional[str] = None) -> FetcherModuleResult:
    errors = []
    logger = logging.getLogger(__name__)

    scopus_key = os.getenv('SCOPUS_API_KEY')
    scopus_base = os.getenv('SCOPUS_API_BASE')

    r = []
    if scopus_base is None or scopus_base is None:
        e = ("Please set SCOPUS_API_KEY and SCOPUS_API_BASE in .env (check out .env.sample) or with "
             "environment variables")
        logger.critical(e)
        errors.append(e)
    else:
        try:
            async with ScopusApi(
                    api_key=scopus_key,
                    api_endpoint=scopus_base,
                    proxies=[options.debug_proxy],
                    verify_ssl=options.verify_ssl) as client:
                r = await client.search(options.search_query)
                if output_path:
                    write_dump(
                        output_path,
                        json.dumps([p.to_dict() for p in r], ensure_ascii=False),
                        __name__,
                        logger)
                for entry in r:
                    logger.debug(entry)
        except HTTPError as h_error:
            e = f'HTTP error: {h_error}'
            logger.error(e)
            errors.append(e)
        except NetworkError as n_error:
            e = f'Network error: {n_error}'
            logger.error(e)
            errors.append(e)
        except InvalidAPIKeyError as api_key_error:
            e = f'Invalid API key: {api_key_error}'
            logger.error(e)
            errors.append(e)
        except Exception as err:
            raise err
    return FetcherModuleResult(module=__name__, results=r, errors=errors)
