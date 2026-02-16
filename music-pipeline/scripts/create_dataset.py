#!/usr/bin/env python3
"""Create MusicGen-compatible dataset from curated stems."""

import sys
import os
import csv
import json
import random
from pathlib import Path
import librosa
import soundfile as sf

def create_dataset(selection_path, stems_dir, output_dir, clip_duration=30):
    """Generate 30-second clips with captions."""
    
    audio_out = Path(output_dir) / "audio"
    audio_out.mkdir(parents=True, exist_ok=True)
    
    metadata = []
    
    with open(selection_path, 'r') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            if row.get('include', '').lower() != 'yes':
                continue
            
            song = row['song']
            stem = row['stem']
            split = row.get('split', 'train')
            genre = row.get('genre', 'music')
            mood = row.get('mood', '')
            
            # Find stem file
            stem_path = Path(stems_dir) / song / f"{stem}.wav"
            if not stem_path.exists():
                stem_path = Path(stems_dir) / song / f"{stem}.mp3"
            
            if not stem_path.exists():
                print(f"Warning: Stem not found: {stem_path}")
                continue
            
            # Load audio
            try:
                y, sr = librosa.load(str(stem_path), sr=32000)  # MusicGen uses 32kHz
            except Exception as e:
                print(f"Error loading {stem_path}: {e}")
                continue
            
            # Calculate number of clips
            total_duration = len(y) / sr
            num_clips = max(1, int(total_duration // clip_duration))
            
            for clip_idx in range(num_clips):
                start = clip_idx * clip_duration * sr
                end = min(start + clip_duration * sr, len(y))
                
                clip = y[int(start):int(end)]
                
                # Pad if too short
                if len(clip) < clip_duration * sr:
                    clip = librosa.util.fix_length(clip, size=int(clip_duration * sr))
                
                # Generate filename
                clip_name = f"{song}_{stem}_clip{clip_idx:03d}.wav"
                clip_path = audio_out / clip_name
                
                # Save clip
                sf.write(str(clip_path), clip, sr)
                
                # Generate caption
                tempo = row.get('tempo', 'medium')
                key = row.get('key', '')
                
                caption_parts = [genre]
                if mood:
                    caption_parts.append(mood)
                if key:
                    caption_parts.append(f"in the key of {key}")
                caption_parts.append(f"at {tempo} BPM")
                caption_parts.append(f"{stem} stem")
                
                caption = ", ".join(caption_parts)
                
                metadata.append({
                    "file_name": f"audio/{clip_name}",
                    "text": caption,
                    "split": split
                })
    
    # Save metadata
    metadata_path = Path(output_dir) / "metadata.jsonl"
    with open(metadata_path, 'w') as f:
        for item in metadata:
            f.write(json.dumps(item) + '\n')
    
    # Count splits
    train_count = sum(1 for m in metadata if m['split'] == 'train')
    valid_count = sum(1 for m in metadata if m['split'] == 'valid')
    
    print(f"Created {len(metadata)} clips:")
    print(f"  Train: {train_count}")
    print(f"  Valid: {valid_count}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: create_dataset.py <selection.csv> <stems_dir> <output_dir>")
        sys.exit(1)
    
    create_dataset(sys.argv[1], sys.argv[2], sys.argv[3])
