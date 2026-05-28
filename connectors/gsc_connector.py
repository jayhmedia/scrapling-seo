from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

from connectors.base import QueryRecord, QuerySourceConnector


class GSCConnector(QuerySourceConnector):
    source_name = "gsc"

    def __init__(self, config: dict):
        self.config = config

    def fetch_queries(self) -> list[QueryRecord]:
        """
        Requires package:
          pip install google-api-python-client google-auth
        and service account access configured in Search Console.
        """
        property_url = self.config["property_url"]
        credentials_path = Path(self.config["credentials_path"])
        date_start = self.config["date_start"]
        date_end = self.config["date_end"]
        row_limit = int(self.config.get("row_limit", 1000))

        if not credentials_path.exists():
            raise FileNotFoundError(
                f"GSC credentials not found: {credentials_path}. "
                "Provide a valid service account JSON file."
            )

        from google.oauth2 import service_account
        from googleapiclient.discovery import build

        credentials = service_account.Credentials.from_service_account_file(
            str(credentials_path),
            scopes=["https://www.googleapis.com/auth/webmasters.readonly"],
        )
        service = build("searchconsole", "v1", credentials=credentials, cache_discovery=False)

        request = {
            "startDate": date_start,
            "endDate": date_end,
            "dimensions": ["query", "page", "country", "device"],
            "rowLimit": row_limit,
        }
        response = (
            service.searchanalytics()
            .query(siteUrl=property_url, body=request)
            .execute()
        )

        rows = response.get("rows", [])
        records: list[QueryRecord] = []
        for row in rows:
            keys = row.get("keys", [])
            query = keys[0] if len(keys) > 0 else ""
            page = keys[1] if len(keys) > 1 else None
            country = keys[2] if len(keys) > 2 else None
            device = keys[3] if len(keys) > 3 else None
            position_raw = row.get("position")

            records.append(
                QueryRecord(
                    query=query,
                    source=self.source_name,
                    source_rank=self._safe_float(position_raw),
                    source_rank_raw=position_raw,
                    source_url=page,
                    country=country,
                    device=device,
                    date_start=date_start,
                    date_end=date_end,
                    clicks=self._safe_float(row.get("clicks")),
                    impressions=self._safe_float(row.get("impressions")),
                    ctr=self._safe_float(row.get("ctr")),
                )
            )

        return records


def to_dicts(records: list[QueryRecord]) -> list[dict]:
    return [asdict(r) for r in records]
