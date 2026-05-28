from __future__ import annotations

from dataclasses import asdict

import pandas as pd

from connectors.ahrefs_connector import AhrefsConnector
from connectors.base import QueryRecord
from connectors.gsc_connector import GSCConnector
from connectors.semrush_connector import SEMrushConnector


def fetch_all_query_sources(config: dict) -> list[QueryRecord]:
    results: list[QueryRecord] = []
    sources = config.get("query_sources", {})

    if sources.get("gsc", {}).get("enabled"):
        results.extend(GSCConnector(sources["gsc"]).fetch_queries())

    if sources.get("semrush", {}).get("enabled"):
        results.extend(SEMrushConnector(sources["semrush"]).fetch_queries())

    if sources.get("ahrefs", {}).get("enabled"):
        results.extend(AhrefsConnector(sources["ahrefs"]).fetch_queries())

    return results


def normalize_query_records(records: list[QueryRecord], config: dict) -> pd.DataFrame:
    rows = [asdict(r) for r in records]
    if not rows:
        return pd.DataFrame(
            columns=[
                "query",
                "source",
                "source_rank",
                "source_rank_raw",
                "source_url",
                "country",
                "device",
                "date_start",
                "date_end",
                "clicks",
                "impressions",
                "ctr",
            ]
        )

    df = pd.DataFrame(rows)

    if config["query_ingestion"].get("lowercase_normalization", True):
        df["query"] = df["query"].fillna("").str.strip().str.lower()
    else:
        df["query"] = df["query"].fillna("").str.strip()

    min_len = int(config["query_ingestion"].get("min_query_length", 2))
    df = df[df["query"].str.len() >= min_len]

    dedupe_strategy = config["query_ingestion"].get(
        "dedupe_strategy", "query+source+country+device"
    )
    if dedupe_strategy == "query+source+country+device":
        subset = ["query", "source", "country", "device"]
    else:
        subset = ["query", "source"]

    df = df.drop_duplicates(subset=subset, keep="first")
    return df.reset_index(drop=True)
