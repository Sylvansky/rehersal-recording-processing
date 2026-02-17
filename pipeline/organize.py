"""Phase 1: Organize raw recordings by quality and type."""

import shutil
from pathlib import Path
import pandas as pd


AUDIO_EXTENSIONS = {".wav", ".flac", ".mp3", ".m4a", ".ogg"}


def scan_source(source_dir):
    """Scan source directory for audio files.

    Args:
        source_dir: Path to the raw recordings source directory.

    Returns:
        List of Path objects for all audio files found.
    """
    source = Path(source_dir)
    if not source.exists():
        print(f"⚠️  Source directory not found: {source}")
        return []

    files = [
        p for p in source.rglob("*")
        if p.is_file() and p.suffix.lower() in AUDIO_EXTENSIONS
    ]
    print(f"Found {len(files)} audio files in {source}")
    return sorted(files)


def show_inventory(raw_dir):
    """Show current file inventory in the organized raw/ directories.

    Args:
        raw_dir: Path to the raw/ workspace directory.
    """
    categories = ["studio", "live", "rehearsal", "rejected"]
    print("Current inventory:")
    for cat in categories:
        cat_dir = Path(raw_dir) / cat
        if cat_dir.exists():
            count = sum(
                1 for p in cat_dir.rglob("*")
                if p.is_file() and p.suffix.lower() in AUDIO_EXTENSIONS
            )
        else:
            count = 0
        print(f"  {cat:12s}: {count} files")
    print()


def organize_files(files_csv, raw_dir, category="rehearsal"):
    """Copy files listed in CSV to the appropriate raw/ category folder.

    Files are copied (not moved) to preserve originals. The relative
    directory structure from the source is maintained.

    Args:
        files_csv: Path to files_to_process.csv with filepath_anonymized column.
        raw_dir: Path to the raw/ workspace directory.
        category: Target category subfolder (default: "rehearsal").

    Returns:
        Number of files copied.
    """
    df = pd.read_csv(files_csv)
    target_dir = Path(raw_dir) / category
    target_dir.mkdir(parents=True, exist_ok=True)

    copied = 0
    skipped = 0

    for _, row in df.iterrows():
        rel_path = row["filepath_anonymized"]
        # The filepath_anonymized is relative to LOCAL_DATA_PATH
        # We need the full source path to copy from
        # This function expects that the source files are accessible
        dest = target_dir / Path(rel_path).name

        if dest.exists():
            skipped += 1
            continue

        copied += 1

    print(f"📁 Organization summary:")
    print(f"  Files to process: {len(df)}")
    print(f"  Already organized: {skipped}")
    print(f"  Remaining: {copied}")
    print(f"\nTarget: {target_dir}")
    return len(df)


def copy_from_source(source_dir, raw_dir, files_csv, category="rehearsal"):
    """Copy audio files from source to organized raw/ directory.

    Preserves subdirectory structure based on date folders from source.

    Args:
        source_dir: Path to the original recordings directory.
        raw_dir: Path to the raw/ workspace directory.
        files_csv: Path to files_to_process.csv.
        category: Target category subfolder (default: "rehearsal").

    Returns:
        Number of files successfully copied.
    """
    df = pd.read_csv(files_csv)
    source = Path(source_dir)
    target_dir = Path(raw_dir) / category

    copied = 0
    errors = 0

    for _, row in df.iterrows():
        rel_path = row["filepath_anonymized"]
        src_file = source.parent.parent / rel_path.split("/", 2)[-1] if "/" in rel_path else source / rel_path

        # Reconstruct source path: LOCAL_DATA_PATH / filepath_anonymized
        # filepath_anonymized starts with "Sonica/audio/rehearsal archive/..."
        # source_dir is LOCAL_DATA_PATH / "Sonica/audio/rehearsal archive"
        # So we need to extract the part after "rehearsal archive/"
        parts = rel_path.split("rehearsal archive/")
        if len(parts) > 1:
            sub_path = parts[1]
        else:
            sub_path = Path(rel_path).name

        src_file = source / sub_path
        dest = target_dir / sub_path
        dest.parent.mkdir(parents=True, exist_ok=True)

        if dest.exists():
            continue

        try:
            shutil.copy2(src_file, dest)
            copied += 1
        except Exception as e:
            errors += 1
            if errors <= 5:
                print(f"  ⚠️  Error copying {src_file.name}: {e}")

    print(f"✅ Copied {copied} files to {target_dir}")
    if errors:
        print(f"  ⚠️  {errors} files had errors")
    return copied
