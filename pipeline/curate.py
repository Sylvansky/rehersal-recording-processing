"""Phase 4: Curation - generate template and apply selections."""

import csv
from pathlib import Path
import pandas as pd


def generate_curation_template(metadata_csv, output_csv):
    """Generate a curation template CSV from analysis metadata.

    Creates a spreadsheet-friendly template where users can mark stems
    to include/exclude, assign genres, moods, and other tags.

    Args:
        metadata_csv: Path to the analysis metadata CSV.
        output_csv: Path to save the curation template.

    Returns:
        Number of stems in the template.
    """
    df = pd.read_csv(metadata_csv)

    # Add curation columns
    df["include"] = ""       # User fills: yes/no
    df["split"] = df.index.map(lambda i: "valid" if i % 5 == 0 else "train")
    df["genre"] = ""         # User fills: rock, jazz, etc.
    df["mood"] = ""          # User fills: upbeat, dark, etc.
    df["era"] = ""           # User fills: early, mid, late
    df["notes"] = ""         # User notes

    # Keep relevant columns
    columns = ["song", "stem", "tempo", "key", "duration_seconds",
               "peak_db", "rms_db", "include", "split", "genre",
               "mood", "era", "notes"]
    existing = [c for c in columns if c in df.columns]
    df = df[existing]

    output_path = Path(output_csv)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)

    print(f"✅ Curation template created: {output_path}")
    print(f"   {len(df)} stems to review")
    print()
    print("Instructions:")
    print("1. Open the CSV in a spreadsheet editor")
    print("2. For each stem, set 'include' to 'yes' for good quality")
    print("3. Set 'split' to 'train' (80%) or 'valid' (20%)")
    print("4. Add genre, mood, and era tags")
    print("5. Save as: curated/selection.csv")
    return len(df)


def load_selection(selection_csv):
    """Load curated selection CSV.

    Args:
        selection_csv: Path to the completed selection CSV.

    Returns:
        DataFrame with selected stems (include == 'yes').
    """
    df = pd.read_csv(selection_csv)
    selected = df[df["include"].str.lower() == "yes"].copy()
    print(f"📋 Loaded selection: {len(selected)} stems included out of {len(df)}")
    return selected


def show_curation_stats(selection_csv):
    """Display statistics about the curated selection.

    Args:
        selection_csv: Path to the completed selection CSV.
    """
    df = pd.read_csv(selection_csv)
    selected = df[df["include"].str.lower() == "yes"]

    print("📊 Curation Statistics:")
    print(f"   Total stems: {len(df)}")
    print(f"   Selected: {len(selected)}")
    print(f"   Rejected: {len(df) - len(selected)}")
    print()

    if len(selected) > 0:
        train = selected[selected["split"] == "train"]
        valid = selected[selected["split"] == "valid"]
        print(f"   Train split: {len(train)}")
        print(f"   Valid split: {len(valid)}")
        print()

        if "genre" in selected.columns:
            genres = selected["genre"].dropna()
            genres = genres[genres != ""]
            if len(genres) > 0:
                print("   Genres:")
                for genre, count in genres.value_counts().items():
                    print(f"     {genre}: {count}")

        if "duration_seconds" in selected.columns:
            total_hours = selected["duration_seconds"].sum() / 3600
            print(f"\n   Total duration: {total_hours:.1f} hours")
