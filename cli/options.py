from dataclasses import dataclass
from typing import Optional, Any, List


@dataclass
class CommonFetcherOptions:
    search_query: str
    verify_ssl: bool
    debug_proxy: Optional[str]


@dataclass
class ProxiesFetcherOptions(CommonFetcherOptions):
    proxies: Optional[list[str]]


@dataclass
class FetcherModuleResult:
    module: str
    results: Any
    errors: List[str]
