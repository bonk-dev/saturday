import itertools

import httpx


class ProxyRotator:
    def __init__(self, proxies: list[str] | None = None):
        if proxies is None:
            proxies = []
        self._proxies = proxies
        self._proxy_cycle = itertools.cycle(self._proxies)

    def use_next_proxy(self) -> str | None:
        return next(self._proxy_cycle) if len(self._proxies) > 0 else None
