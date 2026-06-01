"""Phase 2: Stem separation using Demucs with GPU acceleration."""

import os
import subprocess
import shutil
import tempfile
from pathlib import Path
from tqdm import tqdm


AUDIO_EXTENSIONS = {".wav", ".flac", ".mp3", ".m4a", ".ogg"}


def _resolve_demucs_runner():
    """Resolve the preferred Demucs CLI invocation.

    Returns:
        Command prefix list for subprocess.run.
    """
    demucs_bin = shutil.which("demucs")
    if demucs_bin:
        return [demucs_bin]
    return ["python", "-m", "demucs"]


def _is_cuda_available():
    """Check CUDA availability through torch when installed."""
    try:
        import torch
        return bool(torch.cuda.is_available())
    except Exception:
        return False


def _track_id(filepath, raw_root):
    """Build a unique, stable output folder name for a track.

    Uses the relative path under raw/ to avoid basename collisions.
    Example: raw/live/set1/song.wav -> live__set1__song
    """
    try:
        rel = filepath.relative_to(raw_root)
        rel_no_ext = rel.with_suffix("")
        parts = rel_no_ext.parts
    except Exception:
        parts = (filepath.stem,)
    return "__".join(parts)


def find_audio_files(raw_dir):
    """Find all audio files in the raw/ directory tree.

    Ignores files under the `rejected` category.

    Args:
        raw_dir: Path to the raw/ workspace directory.

    Returns:
        Sorted list of Path objects for audio files found.
    """
    raw = Path(raw_dir)
    files = [
        p for p in raw.rglob("*")
        if p.is_file()
        and p.suffix.lower() in AUDIO_EXTENSIONS
        and "rejected" not in {part.lower() for part in p.relative_to(raw).parts}
    ]
    return sorted(files)


def separate_single(filepath, raw_dir, stems_dir, device="cuda", model="htdemucs",
                   demucs_runner=None):
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
    raw_root = Path(raw_dir)
    track_name = _track_id(filepath, raw_root)
    output_check = Path(stems_dir) / model / track_name
    stem_exts = {".wav", ".mp3", ".flac"}

    # Skip if already processed
    if output_check.exists() and any(
        p.is_file() and p.suffix.lower() in stem_exts for p in output_check.iterdir()
    ):
        return True

    demucs_runner = demucs_runner or _resolve_demucs_runner()

    try:
        with tempfile.TemporaryDirectory(prefix="demucs_") as tmpdir:
            demucs_input = filepath

            # Demucs names output folder by input filename stem.
            # Stage a unique name when needed to prevent collisions.
            if track_name != filepath.stem:
                staged = Path(tmpdir) / f"{track_name}{filepath.suffix.lower()}"
                try:
                    os.symlink(filepath, staged)
                except OSError:
                    shutil.copy2(filepath, staged)
                demucs_input = staged

            cmd = [
                *demucs_runner,
                "--device", device,
                "-n", model,
                "-o", str(stems_dir),
                str(demucs_input),
            ]
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=1800
            )
        if result.returncode != 0:
            err = (result.stderr or result.stdout or "").strip()
            print(f"  ❌ Failed: {track_name} - {err[:200]}")
            return False
        return True
    except subprocess.TimeoutExpired:
        print(f"  ⏱️  Timeout: {track_name}")
        return False
    except Exception as e:
        print(f"  ❌ Error: {track_name} - {e}")
        return False


def run_stem_separation(raw_dir, stems_dir, device="cuda", model="htdemucs",
                        num_workers=1, **kwargs):
    """Run stem separation on all audio files.

    Processes files sequentially through Demucs (GPU is the bottleneck).
    Each file is separated into 4 stems: vocals, drums, bass, other.

    Args:
        raw_dir: Path to the raw/ directory containing audio files.
        stems_dir: Path to output stems directory.
        device: Torch device ("cuda" or "cpu").
        model: Demucs model name.
        num_workers: Number of parallel Demucs processes (default 1 for GPU).

    Returns:
        Tuple of (success_count, fail_count).
    """
    files = find_audio_files(raw_dir)
    if not files:
        print("❌ No audio files found in raw/")
        return 0, 0

    if device == "cuda" and not _is_cuda_available():
        print("⚠️ CUDA requested but unavailable; falling back to CPU")
        device = "cpu"

    demucs_runner = _resolve_demucs_runner()

    stems_path = Path(stems_dir)
    stems_path.mkdir(parents=True, exist_ok=True)

    print(f"🎵 Stem Separation (Demucs - {model})")
    print(f"   Device: {device}")
    print(f"   Runner: {' '.join(demucs_runner)}")
    print(f"   Files: {len(files)}")
    print(f"   Output: {stems_path}")
    print()

    success = 0
    failed = 0
    raw_root = Path(raw_dir)

    for filepath in tqdm(files, desc="Separating stems"):
        if separate_single(
            filepath,
            raw_root,
            stems_dir,
            device=device,
            model=model,
            demucs_runner=demucs_runner,
        ):
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
