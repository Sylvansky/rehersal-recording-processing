---
name: music-pipeline
description: Complete pipeline for processing band recordings into AI training datasets. Stem separation with Demucs, audio analysis, metadata tagging, and MusicGen dataset preparation. Use when preparing music recordings for AI model fine-tuning.
homepage: https://github.com/facebookresearch/demucs
metadata:
  {
    "openclaw":
      {
        "emoji": "🎸",
        "requires": { "bins": ["python3"], "gpu": true },
        "install":
          [
            {
              "id": "conda",
              "kind": "script",
              "command": "scripts/install.sh",
              "label": "Install Demucs and dependencies",
            },
          ],
      },
  }
---

# Music Pipeline - Band Recordings to AI Dataset

Complete workflow for turning your band's recordings into a MusicGen training dataset.

## Quick Start

```bash
cd /home/mike/.openclaw/workspace/skills/music-pipeline
./scripts/install.sh          # Install dependencies
./scripts/01_organize.sh      # Organize raw recordings
./scripts/02_stem.sh          # Separate into stems
./scripts/03_analyze.sh       # Detect tempo/key
./scripts/04_curate.sh        # Quality check and tag
./scripts/05_dataset.sh       # Create MusicGen dataset
```

## Pipeline Overview

**Input:** Raw recordings (WAV/FLAC/MP3)
**Output:** Curated dataset ready for MusicGen fine-tuning

### Phase 1: Organization (01_organize.sh)
Sort recordings by quality and type:
- `raw/studio/` - Final studio masters (priority)
- `raw/live/` - Live recordings
- `raw/rehearsal/` - Practice sessions
- `raw/rejected/` - Discard pile

### Phase 2: Stem Separation (02_stem.sh)
Use Demucs to split songs into:
- `stems/{song}/vocals.wav`
- `stems/{song}/drums.wav`
- `stems/{song}/bass.wav`
- `stems/{song}/other.wav` (guitar, keys, etc.)

### Phase 3: Analysis (03_analyze.sh)
Auto-detect for each stem:
- Tempo (BPM)
- Musical key
- Duration
- Audio quality metrics

### Phase 4: Curation (04_curate.sh)
Interactive quality control:
- Flag stems with artifacts
- Tag genre, mood, era
- Select best 20-50 hours
- Create train/validation split

### Phase 5: Dataset (05_dataset.sh)
Generate MusicGen-compatible dataset:
- 30-second clips with captions
- Metadata JSON
- Ready for fine-tuning

## Directory Structure

```
workspace/
├── raw/                    # Original recordings
│   ├── studio/
│   ├── live/
│   └── rehearsal/
├── stems/                  # Demucs output
│   └── {song_name}/
│       ├── vocals.wav
│       ├── drums.wav
│       ├── bass.wav
│       └── other.wav
├── analyzed/               # Analysis results
│   └── metadata.csv
├── curated/                # Quality-selected clips
│   ├── train/
│   └── valid/
└── dataset/                # Final MusicGen format
    ├── audio/
    └── metadata.jsonl
```

## Hardware Requirements

- **GPU:** RTX 3060+ (12GB+ VRAM)
- **Storage:** 2-3x original size (stems + clips)
- **RAM:** 32GB recommended for batch processing

## Processing Time Estimates

With 500 hours of recordings on RTX 3060:
- Stem separation: ~80-100 hours GPU time
- Analysis: ~10 hours
- Curation: Manual (weeks)
- Dataset prep: ~2 hours

## Next Steps

After pipeline completes:
1. See `references/finetuning.md` for MusicGen setup
2. Train with LoRA on your 16GB GPU
3. Generate new songs in your style

## Troubleshooting

**Demucs OOM:** Reduce batch size in `02_stem.sh`
**Poor stem quality:** Use 4-stem instead of 6-stem mode
**Slow processing:** Run overnight, process in chunks
