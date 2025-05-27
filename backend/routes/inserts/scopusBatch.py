import asyncio
import os
import traceback

from flask import request
from flask_restx import Resource, Namespace
import http.cookies

from backend.config import config
from backend.models import insert_request_fields, insert_response_fields, error_response_fields
from database.dbInserts.scopusBatchInsert import scopusBatchInsert
from backend.routes import logger
from fetcher.scopus_batch.models import all_identifiers, ExportFileType
from fetcher.scopus_batch.parser import ScopusCsvParser
from fetcher.scopus_batch.scraper import ScopusScraper, ScopusScraperConfig

ns_scopus_batch = Namespace('scopus-batch', description='Scopus Batch Export operations')

insert_request_model = ns_scopus_batch.model('SearchRequest', insert_request_fields)
insert_response_model = ns_scopus_batch.model('SearchResponse', insert_response_fields)
error_response_model = ns_scopus_batch.model('ErrorResponse', error_response_fields)


@ns_scopus_batch.route('/export')
class ScopusBatchExport(Resource):
    @ns_scopus_batch.expect(insert_request_model)
    @ns_scopus_batch.response(200, 'Success', insert_response_model)
    @ns_scopus_batch.response(400, 'Bad request', error_response_model)
    @ns_scopus_batch.response(500, 'Internal Server Error', error_response_model)
    def post(self):
        """
        Execute Scopus batch export operation using either local file or web scraping approach.
        Supports two modes: reading from local CSV file or performing authenticated web scraping
        of Scopus database using cookies and session management. Handles cookie validation,
        SSL configuration, proxy settings, CSV parsing with BOM removal, and database insertion.
        Automatically extracts all publication identifiers and metadata from Scopus batch export.

        :return: Dictionary containing export results with success status, search query, and inserted record count, along with HTTP status code.
        :rtype: tuple[dict, int]
        """
        try:
            data = request.get_json()
            if not data or 'search_query' not in data:
                return {'error': 'search_query is required'}, 400

            search_query = data['search_query']
            batch_file_path = data.get('batch_file_path')

            # Get SSL and proxy configuration from app settings only
            ssl_insecure = config.get_ssl_config()
            prod_proxies, debug_proxy = config.get_proxy_config()

            logger.info(f'Scopus batch export for: "{search_query}"')
            logger.info(f'SSL insecure: {ssl_insecure}, Debug proxy: {debug_proxy}')

            # Use local file if provided
            if batch_file_path:
                logger.info(f'Scopus batch: reading from local file: {batch_file_path}')
                with open(batch_file_path, 'r') as b_file:
                    export_data = b_file.read()
            else:
                # Use cookies for web scraping
                if not config.scopus_batch_cookie_file or not os.path.isfile(config.scopus_batch_cookie_file):
                    return {
                        'error': f'SCOPUS_BATCH_COOKIE_FILE not found: "{config.scopus_batch_cookie_file}"'
                    }, 500

                with open(config.scopus_batch_cookie_file, 'r') as cookie_file_f:
                    cookie_file = cookie_file_f.read()

                cookies = http.cookies.SimpleCookie(cookie_file)
                cookies.load(cookie_file)

                scopus_batch_jwt = cookies.get('SCOPUS_JWT')
                scopus_batch_awselb = cookies.get('AWSELB')
                scopus_batch_session_uuid = cookies.get('scopusSessionUUID')
                scopus_batch_sc_session_id = cookies.get('SCSessionID')

                # Validate required cookies
                required_cookies = {
                    'SCOPUS_JWT': scopus_batch_jwt,
                    'AWSELB': scopus_batch_awselb,
                    'scopusSessionUUID': scopus_batch_session_uuid,
                    'SCSessionID': scopus_batch_sc_session_id
                }

                missing_cookies = [name for name, cookie in required_cookies.items() if not cookie]
                if missing_cookies:
                    return {
                        'error': f'Missing required cookies: {", ".join(missing_cookies)}'
                    }, 500

                if not config.scopus_batch_user_agent:
                    return {
                        'error': 'SCOPUS_BATCH_USER_AGENT environment variable is required'
                    }, 500

                logger.info("All required Scopus batch cookies were found")

                async def run_scopus_batch():
                    """
                    Execute asynchronous Scopus batch export using authenticated web scraping.
                    Creates ScopusScraper instance with complete cookie-based authentication including
                    JWT tokens, session identifiers, and load balancer cookies. Performs bulk export
                    of search results in CSV format with all available publication identifiers.

                    :return: Raw CSV export data from Scopus batch export containing publication metadata.
                    :rtype: str
                    """
                    async with ScopusScraper(ScopusScraperConfig(
                            user_agent=config.scopus_batch_user_agent,
                            scopus_jwt=scopus_batch_jwt.value,
                            scopus_jwt_domain=config.scopus_batch_cookie_jwt_domain,
                            awselb=scopus_batch_awselb.value,
                            scopus_session_uuid=scopus_batch_session_uuid.value,
                            sc_session_id=scopus_batch_sc_session_id.value),
                            verify_ssl=not ssl_insecure,
                            base_uri=config.scopus_batch_base,
                            proxy=debug_proxy) as sc_batch:
                        return await sc_batch.export_all(
                            search_query,
                            file_type=ExportFileType.CSV,
                            fields=all_identifiers())

                export_data = asyncio.run(run_scopus_batch())

            if not export_data:
                return {'error': 'No data was exported'}, 500

            # Parse the CSV data
            logger.info('Scopus batch: parsing data')
            export_data = export_data.removeprefix('\ufeff')  # Remove BOM
            parser = ScopusCsvParser(export_data)

            scopus_batch_pubs = parser.read_all_publications()
            logger.info(f'Parsed publications: {len(scopus_batch_pubs)}')

            try:
                insertCount = scopusBatchInsert(scopus_batch_pubs)
                logger.info(f'Successfully inserted {len(scopus_batch_pubs)} records into database')
                return {
                    'success': True,
                    'search_query': search_query,
                    'count': insertCount
                }
            except Exception as db_error:
                logger.error(f'Database insertion error: {str(db_error)}')
                return {'error': str(db_error)}, 500

        except Exception as e:
            logger.error(f'Scopus batch export error: {str(e)}')
            logger.error(traceback.format_exc())
            return {'error': str(e)}, 500