import asyncio
import traceback

from flask import request
from flask_restx import Resource, Namespace
from backend.config import config
from backend.routes import logger
from database.dbInserts.gscholarAPIInsert import scholarInsert
from fetcher.gscholar.scraper import GoogleScholarScraper
from backend.models import insert_request_fields, insert_response_fields, error_response_fields


ns_gscholar = Namespace('gscholar', description='Google Scholar operations')

insert_request_model = ns_gscholar.model('SearchRequest', insert_request_fields)
insert_response_model = ns_gscholar.model('SearchResponse', insert_response_fields)
error_response_model = ns_gscholar.model('ErrorResponse', error_response_fields)

@ns_gscholar.route('/search')
class GoogleScholarSearch(Resource):
    @ns_gscholar.expect(insert_request_model)
    @ns_gscholar.response(200, 'Success', insert_response_model)
    @ns_gscholar.response(400, 'Bad request', error_response_model)
    @ns_gscholar.response(500, 'Internal Server Error', error_response_model)
    def post(self):
        """
        Execute a Google Scholar search with configurable SSL and proxy settings.

        1. Validates the incoming JSON request for required 'search_query' field.
        2. Retrieves SSL verification and proxy configuration from app settings.
        3. Initializes GoogleScholarScraper with the retrieved configuration.
        4. Executes asynchronous search operation using asyncio.run().
        5. Returns structured response with search results and metadata.
        6. Handles exceptions with detailed logging and appropriate error responses.

        :return: JSON response containing search results, success status, and result count.
        :rtype: dict
        :raises: 400 error if search_query is missing from request body.
        :raises: 500 error if scraping operation fails or other exceptions occur.
        """
        try:
            data = request.get_json()
            if not data or 'search_query' not in data:
                return {'error': 'search_query is required'}, 400

            search_query = data['search_query']

            # Get SSL and proxy configuration from app settings only
            ssl_insecure = config.get_ssl_config()
            prod_proxies, debug_proxy = config.get_proxy_config()

            logger.info(f'Google Scholar search for: "{search_query}"')
            logger.info(f'SSL insecure: {ssl_insecure}, Proxies: {prod_proxies}')

            async def run_gscholar_search():
                scr = GoogleScholarScraper(verify_ssl=not ssl_insecure, proxies=prod_proxies)
                return await scr.search(search_query)

            # Run the async function
            r = asyncio.run(run_gscholar_search())


            insertCount = scholarInsert(r)
            return {
                'success': True,
                'search_query': search_query,
                'count': insertCount
            }

        except Exception as e:
            logger.error(f'Google Scholar search error: {str(e)}')
            logger.error(traceback.format_exc())
            return {'error': str(e)}, 500