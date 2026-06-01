#!/usr/bin/env python3
"""Create a first-pass song/version catalog from files_to_process.csv.

Outputs:
1) instances CSV: one row per recording file with parsed metadata
2) summary CSV: one row per canonical song key with counts and date span
"""

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from pipeline.organize import build_song_version_catalog


def main() -> int:
    parser = argparse.ArgumentParser(description="Catalog song versions from files_to_process.csv")
    parser.add_argument(
        "--input",
        default="files_to_process.csv",
        help="Path to files_to_process.csv",
    )
    parser.add_argument(
        "--instances-output",
        default="analyzed/song_instances.csv",
        help="Output CSV path for per-file instances",
    )
    parser.add_argument(
        "--summary-output",
        default="analyzed/song_versions_summary.csv",
        help="Output CSV path for grouped song summary",
    )
    parser.add_argument(
        "--exclude-hidden",
        action="store_true",
        help="Exclude AppleDouble hidden files (._*) from instances output",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        raise FileNotFoundError(f"Input CSV not found: {input_path}")

    instances, summary = build_song_version_catalog(input_path, exclude_hidden=args.exclude_hidden)

    instances_out = Path(args.instances_output)
    summary_out = Path(args.summary_output)
    instances_out.parent.mkdir(parents=True, exist_ok=True)
    summary_out.parent.mkdir(parents=True, exist_ok=True)

    instances.to_csv(instances_out, index=False)
    summary.to_csv(summary_out, index=False)

    print(f"Wrote instances: {instances_out} ({len(instances)} rows)")
    print(f"Wrote summary:   {summary_out} ({len(summary)} song groups)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
