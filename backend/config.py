import os
import logging
from typing import List, Optional

class AppConfig:
    """Application configuration class"""
    def __init__(self):
        # SSL Configuration
        self.ssl_insecure = self._get_bool_env('SSL_INSECURE', False)

        # Proxy Configuration
        self.debug_proxy = os.getenv('DEBUG_PROXY')
        self.default_proxies = self._get_list_env('DEFAULT_PROXIES', [])

        # Scopus API Configuration
        self.scopus_api_key = os.getenv('SCOPUS_API_KEY')
        self.scopus_api_base = os.getenv('SCOPUS_API_BASE')

        # Scopus Batch Configuration
        self.scopus_batch_cookie_file = os.getenv('SCOPUS_BATCH_COOKIE_FILE')
        self.scopus_batch_base = os.getenv('SCOPUS_BATCH_BASE', 'https://www.scopus.com')
        self.scopus_batch_cookie_jwt_domain = os.getenv('SCOPUS_BATCH_COOKIE_JWT_DOMAIN', '.scopus.com')
        self.scopus_batch_user_agent = os.getenv('SCOPUS_BATCH_USER_AGENT')

        # Logging
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')

        # Static files
        self.static_dir = os.getenv('STATIC_DIR', 'ui')

    def _get_bool_env(self, key: str, default: bool = False) -> bool:
        """Get boolean environment variable"""
        value = os.getenv(key, '').lower()
        return value in ('true', '1') if value else default

    def _get_list_env(self, key: str, default: List[str] = None) -> List[str]:
        """Get list environment variable (comma-separated)"""
        if default is None:
            default = []
        value = os.getenv(key, '')
        return [item.strip() for item in value.split(',') if item.strip()] if value else default

    def get_proxy_config(self) -> tuple[List[str], Optional[str]]:
        """
        Get proxy configuration from app settings only.
        Priority: debug_proxy > default_proxies
        """
        if self.debug_proxy:
            logging.getLogger(__name__).info(f'Using debug proxy: "{self.debug_proxy}"')
            return [self.debug_proxy], self.debug_proxy

        if self.default_proxies:
            logging.getLogger(__name__).info(f'Using default proxies: {self.default_proxies}')
            return self.default_proxies, None

        logging.getLogger(__name__).debug('No proxies configured')
        return [], None

    def get_ssl_config(self) -> bool:
        """
        Get SSL configuration from app settings only.
        """
        return self.ssl_insecure

config = AppConfig()