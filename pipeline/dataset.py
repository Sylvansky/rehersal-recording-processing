"""Phase 5: Create MusicGen-compatible dataset from curated stems."""

import json
from pathlib import Path
import pandas as pd
import numpy as np
from tqdm import tqdm

# Lazy imports for heavy libraries
_librosa = None
_sf = None


def _get_librosa():
    global _librosa
    if _librosa is None:
        import librosa
        _librosa = librosa
    return _librosa


def _get_soundfile():
    global _sf
    if _sf is None:
        import soundfile as sf
        _sf = sf
    return _sf


def create_dataset(selection_csv, stems_dir, output_dir,
                   clip_duration=30, model="htdemucs", num_workers=6):
    """Generate 30-second clips with captions for MusicGen training.

    Args:
        selection_csv: Path to the curated selection CSV (include == 'yes').
        stems_dir: Path to the stems directory.
        output_dir: Path to the output dataset directory.
        clip_duration: Duration of each clip in seconds (default: 30).
        model: Demucs model name (determines stem subdirectory).
        num_workers: Number of workers for parallel processing.

    Returns:
        Number of clips created.
    """
    librosa = _get_librosa()
    sf = _get_soundfile()

    df = pd.read_csv(selection_csv)
    selected = df[df["include"].str.lower() == "yes"]

    if len(selected) == 0:
        print("❌ No stems marked as 'include=yes' in selection")
        return 0

    audio_out = Path(output_dir) / "audio"
    audio_out.mkdir(parents=True, exist_ok=True)

    metadata = []
    stems_path = Path(stems_dir) / model

    for _, row in tqdm(selected.iterrows(), total=len(selected),
                       desc="Creating clips"):
        song = row["song"]
        stem = row["stem"]
        split = row.get("split", "train")
        genre = row.get("genre", "music")
        mood = row.get("mood", "")

        # Find stem file
        stem_path = stems_path / song / f"{stem}.wav"
        if not stem_path.exists():
            stem_path = stems_path / song / f"{stem}.mp3"
        if not stem_path.exists():
            print(f"  ⚠️  Stem not found: {song}/{stem}")
            continue

        # Load audio at MusicGen's 32kHz sample rate
        try:
            y, sr = librosa.load(str(stem_path), sr=32000)
        except Exception as e:
            print(f"  ❌ Error loading {stem_path.name}: {e}")
            continue

        # Calculate clips
        total_duration = len(y) / sr
        num_clips = max(1, int(total_duration // clip_duration))

        for clip_idx in range(num_clips):
            start = int(clip_idx * clip_duration * sr)
            end = min(start + int(clip_duration * sr), len(y))
            clip = y[start:end]

            # Pad if too short
            target_len = int(clip_duration * sr)
            if len(clip) < target_len:
                clip = librosa.util.fix_length(clip, size=target_len)

            # Save clip
            clip_name = f"{song}_{stem}_clip{clip_idx:03d}.wav"
            clip_path = audio_out / clip_name
            sf.write(str(clip_path), clip, sr)

            # Build caption
            caption_parts = [str(genre)] if genre else ["music"]
            if mood:
                caption_parts.append(str(mood))
            key = row.get("key", "")
            if key and pd.notna(key):
                caption_parts.append(f"in the key of {key}")
            tempo = row.get("tempo", "")
            if tempo and pd.notna(tempo):
                caption_parts.append(f"at {tempo} BPM")
            caption_parts.append(f"{stem} stem")

            metadata.append({
                "file_name": f"audio/{clip_name}",
                "text": ", ".join(caption_parts),
                "split": split,
            })

    # Save metadata
    metadata_path = Path(output_dir) / "metadata.jsonl"
    with open(metadata_path, "w") as f:
        for item in metadata:
            f.write(json.dumps(item) + "\n")

    # Summary
    train_count = sum(1 for m in metadata if m["split"] == "train")
    valid_count = sum(1 for m in metadata if m["split"] == "valid")

    print(f"\n✅ Dataset created: {len(metadata)} clips")
    print(f"   Train: {train_count}")
    print(f"   Valid: {valid_count}")
    print(f"   Output: {Path(output_dir)}")
    return len(metadata)
