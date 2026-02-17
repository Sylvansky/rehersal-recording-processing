"""Phase 3: Audio analysis - tempo, key, and quality metrics."""

import sys
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import pandas as pd
from tqdm import tqdm

# Lazy import librosa to avoid slow startup when not needed
_librosa = None


def _get_librosa():
    global _librosa
    if _librosa is None:
        import librosa
        _librosa = librosa
    return _librosa


KEYS = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def analyze_single(filepath):
    """Analyze a single audio file for tempo, key, duration, and loudness.

    Args:
        filepath: Path to the audio file.

    Returns:
        Dict with analysis results, or None on error.
    """
    librosa = _get_librosa()
    filepath = str(filepath)

    try:
        y, sr = librosa.load(filepath, sr=None)

        # Duration
        duration = librosa.get_duration(y=y, sr=sr)

        # Tempo
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        tempo = librosa.beat.tempo(onset_envelope=onset_env, sr=sr)[0]

        # Key detection via chromagram
        chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
        key_idx = np.sum(chroma, axis=1).argmax()
        key = KEYS[key_idx]

        # Loudness metrics
        peak_db = float(20 * np.log10(np.max(np.abs(y)) + 1e-10))
        rms_db = float(20 * np.log10(np.sqrt(np.mean(y**2)) + 1e-10))

        return {
            "tempo": round(float(tempo), 1),
            "key": key,
            "duration_seconds": round(duration, 2),
            "peak_db": round(peak_db, 2),
            "rms_db": round(rms_db, 2),
        }
    except Exception as e:
        print(f"Error analyzing {filepath}: {e}", file=sys.stderr)
        return None


def _analyze_worker(args):
    """Worker function for parallel analysis.

    Args:
        args: Tuple of (filepath, song_name, stem_name).

    Returns:
        Dict with song, stem, and analysis results.
    """
    filepath, song, stem = args
    result = analyze_single(filepath)
    if result:
        return {"song": song, "stem": stem, **result}
    return {"song": song, "stem": stem, "tempo": None, "key": None,
            "duration_seconds": 0, "peak_db": 0, "rms_db": 0}


def run_analysis(stems_dir, output_csv, model="htdemucs", num_workers=6):
    """Analyze all stems and save results to CSV.

    Uses multiprocessing to parallelize CPU-bound analysis across cores.

    Args:
        stems_dir: Path to the stems directory.
        output_csv: Path to save the metadata CSV.
        model: Demucs model name (determines subdirectory).
        num_workers: Number of parallel workers (default: 6 for Ryzen 5 9600X).

    Returns:
        pandas DataFrame with analysis results.
    """
    stems_path = Path(stems_dir) / model
    if not stems_path.exists():
        print(f"❌ Stems directory not found: {stems_path}")
        return pd.DataFrame()

    # Collect all stem files
    tasks = []
    for song_dir in sorted(stems_path.iterdir()):
        if not song_dir.is_dir():
            continue
        for stem_file in sorted(song_dir.iterdir()):
            if stem_file.suffix.lower() in {".wav", ".mp3", ".flac"}:
                tasks.append((str(stem_file), song_dir.name, stem_file.stem))

    if not tasks:
        print("❌ No stems found to analyze")
        return pd.DataFrame()

    print(f"🎼 Analyzing {len(tasks)} stems with {num_workers} workers...")

    results = []
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        for result in tqdm(
            executor.map(_analyze_worker, tasks),
            total=len(tasks),
            desc="Analyzing"
        ):
            results.append(result)

    df = pd.DataFrame(results)

    # Save to CSV
    output_path = Path(output_csv)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)

    print(f"\n✅ Analysis complete: {len(df)} stems analyzed")
    print(f"   Results saved to: {output_path}")
    return df
