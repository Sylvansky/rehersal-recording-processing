"""Phase 1: Organize raw recordings by quality and type."""

import shutil
import re
from pathlib import Path
import pandas as pd


AUDIO_EXTENSIONS = {".wav", ".flac", ".mp3", ".m4a", ".ogg"}
CATALOG_EXTENSIONS = {"mp3", "wav", "flac", "m4a", "ogg"}
DATE_RE = re.compile(r"/(19\d{6}|20\d{6})(?:/|$)")
VERSION_RE = re.compile(r"(?:^|[_\-\s])v(\d+)(?:$|[_\-\s])", re.IGNORECASE)
PART_RE = re.compile(r"part[_\-\s]*([ivx]+|\d+)", re.IGNORECASE)


def _extract_date(filepath_anonymized):
    match = DATE_RE.search(str(filepath_anonymized).replace("\\", "/"))
    return match.group(1) if match else None


def _parse_version(filename_stem):
    match = VERSION_RE.search(filename_stem)
    if not match:
        return None
    try:
        return int(match.group(1))
    except ValueError:
        return None


def _parse_part(filename_stem):
    match = PART_RE.search(filename_stem)
    if not match:
        return None
    return match.group(1).lower()


def _normalize_song_key(filename_stem):
    stem = filename_stem.strip()
    if stem.startswith("._"):
        stem = stem[2:]

    stem = re.sub(r"\([^)]*\)", "", stem)
    stem = PART_RE.sub("", stem)
    stem = re.sub(r"(?:^|[_\-\s])v\d+(?:$|[_\-\s])", " ", stem, flags=re.IGNORECASE)
    stem = re.sub(r"[_\-]+", " ", stem)
    stem = re.sub(r"\s+", " ", stem).strip().lower()
    return stem or filename_stem.lower()


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
    """Show a summary of files to organize from the CSV.

    Checks which files from the CSV have already been copied to the
    workspace and reports how many remain.

    Args:
        files_csv: Path to files_to_process.csv with filepath_anonymized column.
        raw_dir: Path to the raw/ workspace directory.
        category: Target category subfolder (default: "rehearsal").

    Returns:
        Total number of files listed in the CSV.
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


def build_song_version_catalog(files_csv, exclude_hidden=True):
    """Parse song names/versions from filenames for first-pass grouping.

    Args:
        files_csv: Path to files_to_process.csv.
        exclude_hidden: If True, exclude AppleDouble files (._*).

    Returns:
        Tuple of (instances_df, summary_df).
    """
    df = pd.read_csv(files_csv)
    required = {"filepath_anonymized", "file_extension", "duration_seconds", "size_bytes"}
    missing = sorted(required - set(df.columns))
    if missing:
        raise ValueError(f"Missing columns in files CSV: {', '.join(missing)}")

    work = df.copy()
    work["filepath_anonymized"] = work["filepath_anonymized"].astype(str)
    work["file_name"] = work["filepath_anonymized"].apply(lambda p: Path(p).name)
    work["file_stem"] = work["file_name"].apply(lambda x: Path(x).stem)
    work["file_extension"] = work["file_extension"].astype(str).str.lower()
    work = work[work["file_extension"].isin(CATALOG_EXTENSIONS)].copy()

    work["is_hidden_appledouble"] = work["file_name"].str.startswith("._")
    if exclude_hidden:
        work = work[~work["is_hidden_appledouble"]].copy()

    work["recording_date"] = work["filepath_anonymized"].apply(_extract_date)
    work["version_num"] = work["file_stem"].apply(_parse_version)
    work["part"] = work["file_stem"].apply(_parse_part)
    work["is_wip"] = work["file_stem"].str.contains("wip", case=False, na=False)
    work["song_key"] = work["file_stem"].apply(_normalize_song_key)
    work["recording_date"] = pd.to_datetime(work["recording_date"], format="%Y%m%d", errors="coerce")

    instances = work[[
        "song_key",
        "file_stem",
        "version_num",
        "part",
        "recording_date",
        "duration_seconds",
        "size_bytes",
        "file_extension",
        "is_wip",
        "is_hidden_appledouble",
        "filepath_anonymized",
    ]].sort_values(["song_key", "recording_date", "version_num", "file_stem"]).reset_index(drop=True)

    summary = (
        instances.groupby("song_key", dropna=False)
        .agg(
            recordings_count=("file_stem", "count"),
            first_recording_date=("recording_date", "min"),
            last_recording_date=("recording_date", "max"),
            distinct_versions=("version_num", lambda s: int(s.dropna().nunique())),
            has_wip=("is_wip", "max"),
            total_duration_seconds=("duration_seconds", "sum"),
        )
        .reset_index()
        .sort_values(["recordings_count", "song_key"], ascending=[False, True])
    )
    summary["total_duration_hours"] = summary["total_duration_seconds"].fillna(0) / 3600.0
    summary["first_recording_date"] = summary["first_recording_date"].dt.strftime("%Y-%m-%d")
    summary["last_recording_date"] = summary["last_recording_date"].dt.strftime("%Y-%m-%d")

    instances["recording_date"] = instances["recording_date"].dt.strftime("%Y-%m-%d")

    return instances, summary
