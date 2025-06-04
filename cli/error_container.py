import logging
from typing import Optional, List


class _ErrorContainer:
    def __init__(self, opt_logger: Optional[logging.Logger]):
        self._logger = opt_logger
        self._errors = []

    def add_error(self, err: str):
        if self._logger:
            self._logger.error(err)
        self._errors.append(err)

    def get_errors(self) -> List[str]:
        return self._errors
