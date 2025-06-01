import asyncio
import traceback

from flask import request
from flask_restx import Resource, Namespace

from backend.config import config
from backend.models import insert_request_fields, insert_response_fields, error_response_fields
from database.dbInserts.scopusAPIInsert import scopusAPIInsert
from backend.routes import logger
from database.dbInsertsAIOptimised.scopusApiInsertOptimised import scopusAPIInsertOptimised
from fetcher.scopus.api import ScopusApi

ns_scopus_api = Namespace('scopus-api', description='Scopus API operations')
insert_request_model = ns_scopus_api.model('SearchRequest', insert_request_fields)
insert_response_model = ns_scopus_api.model('SearchResponse', insert_response_fields)
error_response_model = ns_scopus_api.model('ErrorResponse', error_response_fields)


@ns_scopus_api.route('/search')
class ScopusApiSearch(Resource):
    @ns_scopus_api.expect(insert_request_model)
    @ns_scopus_api.response(200, 'Success', insert_response_model)
    @ns_scopus_api.response(400, 'Bad request', error_response_model)
    @ns_scopus_api.response(500, 'Internal Server Error', error_response_model)
    def post(self):
        """
        Execute Scopus API search query and insert results into database.
        Performs asynchronous search using Scopus API client with configurable SSL and proxy settings.
        Validates API credentials, executes search query, and automatically inserts retrieved academic data
        into the database using scopusAPIInsert function. Handles both API communication errors and
        database insertion failures with detailed logging.

        :return: Dictionary containing search results with success status, query string, and record count, along with HTTP status code.
        :rtype: tuple[dict, int]
        """
        try:
            data = request.get_json()
            if not data or 'search_query' not in data:
                return {'error': 'search_query is required'}, 400

            search_query = data['search_query']

            # Get SSL and proxy configuration from app settings only
            ssl_insecure = config.get_ssl_config()
            prod_proxies, debug_proxy = config.get_proxy_config()

            if not config.scopus_api_base or not config.scopus_api_key:
                return {
                    'error': 'SCOPUS_API_KEY and SCOPUS_API_BASE must be set in environment variables'
                }, 500

            logger.info(f'Scopus API search for: "{search_query}"')
            logger.info(f'SSL insecure: {ssl_insecure}, Proxies: {prod_proxies}')

            async def run_scopus_search():
                """
                Execute asynchronous Scopus API search with configured client settings.
                Creates ScopusApi client instance with SSL verification and proxy configuration,
                then performs search query against Scopus database.

                :return: Search results from Scopus API containing academic publication data.
                """
                async with ScopusApi(
                        api_key=config.scopus_api_key,
                        api_endpoint=config.scopus_api_base,
                        proxies=prod_proxies if prod_proxies else None,
                        verify_ssl=not ssl_insecure) as client:
                    return await client.search(search_query)

            # Run the async function
            result = asyncio.run(run_scopus_search())

            # Insert into database using scopusAPIInsert
            try:
                insertCount = scopusAPIInsert(result)
                logger.info(f'Successfully inserted {insertCount} records into database')
                return {
                    'success': True,
                    'search_query': search_query,
                    'count': insertCount
                }
            except Exception as db_error:
                logger.error(f'Database insertion error: {str(db_error)}')
                return {'error': str(db_error)}, 500

        except Exception as e:
            logger.error(f'Scopus API search error: {str(e)}')
            logger.error(traceback.format_exc())
            return {'error': str(e)}, 500