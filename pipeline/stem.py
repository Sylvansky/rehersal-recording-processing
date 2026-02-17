"""Phase 2: Stem separation using Demucs with GPU acceleration."""

import subprocess
import shutil
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm


AUDIO_EXTENSIONS = {".wav", ".flac", ".mp3", ".m4a", ".ogg"}


def find_audio_files(raw_dir):
    """Find all audio files in the raw/ directory tree.

    Args:
        raw_dir: Path to the raw/ workspace directory.

    Returns:
        Sorted list of Path objects for audio files found.
    """
    raw = Path(raw_dir)
    files = [
        p for p in raw.rglob("*")
        if p.is_file() and p.suffix.lower() in AUDIO_EXTENSIONS
    ]
    return sorted(files)


def separate_single(filepath, stems_dir, device="cuda", model="htdemucs"):
    """Run Demucs stem separation on a single audio file.

    Args:
        filepath: Path to the audio file.
        stems_dir: Path to the output stems directory.
        device: Torch device to use ("cuda" or "cpu").
        model: Demucs model name (default: htdemucs for 4-stem).

    Returns:
        True if successful, False otherwise.
    """
    filepath = Path(filepath)
    basename = filepath.stem
    output_check = Path(stems_dir) / model / basename

    # Skip if already processed
    if output_check.exists() and any(output_check.iterdir()):
        return True

    try:
        cmd = [
            "python", "-m", "demucs",
            "--device", device,
            "-n", model,
            "-o", str(stems_dir),
            str(filepath),
        ]
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=600
        )
        if result.returncode != 0:
            print(f"  ❌ Failed: {basename} - {result.stderr[:200]}")
            return False
        return True
    except subprocess.TimeoutExpired:
        print(f"  ⏱️  Timeout: {basename}")
        return False
    except Exception as e:
        print(f"  ❌ Error: {basename} - {e}")
        return False


def run_stem_separation(raw_dir, stems_dir, device="cuda", model="htdemucs",
                        batch_size=4, num_workers=1):
    """Run stem separation on all audio files.

    Processes files sequentially through Demucs (GPU is the bottleneck).
    Each file is separated into 4 stems: vocals, drums, bass, other.

    Args:
        raw_dir: Path to the raw/ directory containing audio files.
        stems_dir: Path to output stems directory.
        device: Torch device ("cuda" or "cpu").
        model: Demucs model name.
        batch_size: Not used by CLI Demucs; kept for API compatibility.
        num_workers: Number of parallel Demucs processes (default 1 for GPU).

    Returns:
        Tuple of (success_count, fail_count).
    """
    files = find_audio_files(raw_dir)
    if not files:
        print("❌ No audio files found in raw/")
        return 0, 0

    stems_path = Path(stems_dir)
    stems_path.mkdir(parents=True, exist_ok=True)

    print(f"🎵 Stem Separation (Demucs - {model})")
    print(f"   Device: {device}")
    print(f"   Files: {len(files)}")
    print(f"   Output: {stems_path}")
    print()

    success = 0
    failed = 0

    for filepath in tqdm(files, desc="Separating stems"):
        if separate_single(filepath, stems_dir, device=device, model=model):
            success += 1
        else:
            failed += 1

    print(f"\n✅ Stem separation complete: {success} succeeded, {failed} failed")
    return success, failed


def list_stems(stems_dir, model="htdemucs"):
    """List all separated stems.

    Args:
        stems_dir: Path to the stems directory.
        model: Demucs model name (determines subdirectory).

    Returns:
        List of dicts with song name, stem name, and file path.
    """
    stems_path = Path(stems_dir) / model
    if not stems_path.exists():
        return []

    stems = []
    for song_dir in sorted(stems_path.iterdir()):
        if not song_dir.is_dir():
            continue
        for stem_file in sorted(song_dir.iterdir()):
            if stem_file.suffix.lower() in {".wav", ".mp3", ".flac"}:
                stems.append({
                    "song": song_dir.name,
                    "stem": stem_file.stem,
                    "path": stem_file,
                })
    return stems
