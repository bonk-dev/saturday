from flask_restx import Resource, Namespace

from backend.config import config
from backend.models import status_response_fields

ns_system = Namespace('system', description='System operations')
status_response_model = ns_system.model('ErrorResponse', status_response_fields)
@ns_system.route('/health')
class HealthCheck(Resource):
    def get(self):
        return {'status': 'healthy', 'service': 'Science Publication Metadata Scraper API'}


@ns_system.route('/status')
class Status(Resource):
    @ns_system.marshal_with(status_response_model)
    def get(self):
        """Status endpoint with environment information"""
        return {
            'status': 'running',
            'endpoints': [
                '/gscholar/search - Google Scholar search',
                '/scopus-api/search - Scopus API search',
                '/scopus-batch/export - Scopus batch export',
                '/system/health - Health check',
                '/system/status - This status endpoint'
            ],
            'environment': {
                'scopus_api_configured': bool(config.scopus_api_key and config.scopus_api_base),
                'scopus_batch_configured': bool(config.scopus_batch_cookie_file),
            },
            'configuration': {
                'ssl_insecure': config.ssl_insecure,
                'debug_proxy': config.debug_proxy,
                'default_proxies': config.default_proxies,
                'log_level': config.log_level
            }
        }
@ns_system.route('/config')
class Configuration(Resource):
    def get(self):
        """Get current application configuration"""
        return {
            'ssl_configuration': {
                'ssl_insecure': config.ssl_insecure
            },
            'proxy_configuration': {
                'debug_proxy': config.debug_proxy,
                'default_proxies': config.default_proxies
            },
            'api_configuration': {
                'scopus_api_configured': bool(config.scopus_api_key and config.scopus_api_base),
                'scopus_batch_configured': bool(config.scopus_batch_cookie_file)
            },
            'logging': {
                'log_level': config.log_level
            }
        }

