from __future__ import annotations

from pathlib import Path

import pandas as pd
import yaml

from services.query_ingestion import fetch_all_query_sources, normalize_query_records


def load_config(path: str = "config.yaml") -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def main() -> None:
    config = load_config()
    output_dir = Path(config["project"]["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)

    records = fetch_all_query_sources(config)
    queries_df = normalize_query_records(records, config)

    output_file = output_dir / "queries_master.csv"
    queries_df.to_csv(output_file, index=False)

    print(f"Wrote {len(queries_df)} normalized rows to {output_file}")


if __name__ == "__main__":
    main()
