from __future__ import annotations

import os

from connectors.base import QueryRecord, QuerySourceConnector


class AhrefsConnector(QuerySourceConnector):
    source_name = "ahrefs"

    def __init__(self, config: dict):
        self.config = config

    def fetch_queries(self) -> list[QueryRecord]:
        api_key = os.getenv(self.config["api_key_env"], "")
        if not api_key:
            raise RuntimeError(
                f"Missing Ahrefs key in env var {self.config['api_key_env']}"
            )

        # TODO: Implement Ahrefs endpoint call + mapping to QueryRecord.
        # Kept explicit to avoid fake/stale API assumptions.
        return []
