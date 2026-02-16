#!/usr/bin/env python3
"""Analyze audio file for tempo, key, and quality metrics."""

import sys
import librosa
import numpy as np

def analyze_audio(filepath):
    """Extract tempo, key, duration, and loudness."""
    try:
        # Load audio
        y, sr = librosa.load(filepath, sr=None)
        
        # Duration
        duration = librosa.get_duration(y=y, sr=sr)
        
        # Tempo
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        tempo = librosa.beat.tempo(onset_envelope=onset_env, sr=sr)[0]
        
        # Key detection (chromagram)
        chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
        key_idx = np.sum(chroma, axis=1).argmax()
        keys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        key = keys[key_idx]
        
        # Loudness metrics
        peak_db = 20 * np.log10(np.max(np.abs(y)) + 1e-10)
        rms_db = 20 * np.log10(np.sqrt(np.mean(y**2)) + 1e-10)
        
        return {
            'tempo': round(tempo, 1),
            'key': key,
            'duration': round(duration, 2),
            'peak_db': round(peak_db, 2),
            'rms_db': round(rms_db, 2)
        }
    except Exception as e:
        print(f"Error analyzing {filepath}: {e}", file=sys.stderr)
        return None

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: analyze_audio.py <filepath> <song_name> <stem_name>", file=sys.stderr)
        sys.exit(1)
    
    filepath = sys.argv[1]
    song = sys.argv[2]
    stem = sys.argv[3]
    
    result = analyze_audio(filepath)
    if result:
        print(f"{song},{stem},{result['tempo']},{result['key']},{result['duration']},{result['peak_db']},{result['rms_db']}")
    else:
        print(f"{song},{stem},ERROR,ERROR,0,0,0")
