from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class QueryRecord:
    query: str
    source: str
    source_rank: float | None
    source_rank_raw: Any = None
    source_url: str | None = None
    country: str | None = None
    device: str | None = None
    date_start: str | None = None
    date_end: str | None = None
    clicks: float | None = None
    impressions: float | None = None
    ctr: float | None = None


class QuerySourceConnector(ABC):
    source_name: str

    @abstractmethod
    def fetch_queries(self) -> list[QueryRecord]:
        """Fetch provider data and return normalized query records."""

    @staticmethod
    def _safe_float(value: Any) -> float | None:
        try:
            return float(value)
        except (TypeError, ValueError):
            return None
