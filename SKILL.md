# Music Pipeline - Band Recordings to AI Dataset

Complete workflow for turning your band's recordings into a MusicGen training dataset.
Designed for local execution in a WSL environment via Python and Jupyter Notebooks.

## Quick Start

```bash
# 1. Clone and set up
cd ~/dev/rehersal-recording-processing
cp .envExample .env          # Edit with your paths
pip install -r requirements.txt

# 2. Run notebooks in order
jupyter notebook
```

Open each notebook and run all cells in sequence:

| Notebook | Phase | Description |
|---|---|---|
| `music_summary.ipynb` | Pre | Scan and catalogue source audio files |
| `01_organize.ipynb` | 1 | Organize raw recordings + parse song/version listings |
| `02_song_version_embeddings.ipynb` | 2 | Embed one song's versions (MERT) + cluster similarity |
| `03_stem_separation.ipynb` | 3 | Separate into stems with Demucs (GPU) |
| `04_analyze.ipynb` | 4 | Detect tempo, key, loudness |
| `05_curate.ipynb` | 5 | Quality control and tagging |
| `06_create_dataset.ipynb` | 6 | Create MusicGen training dataset |

## Pipeline Overview

**Input:** Raw recordings (WAV/FLAC/MP3) — 2808 files, ~23 GB, ~110 hours
**Output:** Curated dataset ready for MusicGen fine-tuning

### Phase 1: Organization (`01_organize.ipynb`)
Sort recordings by quality and type:
- `raw/studio/` — Final studio masters (priority)
- `raw/live/` — Live recordings
- `raw/rehearsal/` — Practice sessions
- `raw/rejected/` — Discard pile
- Parse filename/date metadata into:
    - `analyzed/song_instances.csv`
    - `analyzed/song_versions_summary.csv`

### Phase 2: Song Version Similarity (`02_song_version_embeddings.ipynb`)
For a selected `song_key`:
- Build/Load grouped versions from filename parsing
- Compute audio embeddings with MERT (`m-a-p/MERT-v1-95M`)
- Run clustering (cosine distance, agglomerative)
- Flag likely bad recordings by outlier score + short duration

### Phase 3: Stem Separation (`03_stem_separation.ipynb`)
Use Demucs to split songs into:
- `stems/{model}/{song}/vocals.wav`
- `stems/{model}/{song}/drums.wav`
- `stems/{model}/{song}/bass.wav`
- `stems/{model}/{song}/other.wav` (guitar, keys, etc.)

### Phase 4: Analysis (`04_analyze.ipynb`)
Auto-detect for each stem (parallelized across CPU cores):
- Tempo (BPM)
- Musical key
- Duration
- Audio quality metrics (peak dB, RMS dB)

### Phase 5: Curation (`05_curate.ipynb`)
Interactive quality control:
- Flag stems with artifacts
- Tag genre, mood, era
- Select best material
- Create train/validation split

### Phase 6: Dataset (`06_create_dataset.ipynb`)
Generate MusicGen-compatible dataset:
- 30-second clips at 32 kHz
- Text captions with metadata
- JSONL metadata file
- Ready for fine-tuning

## Project Structure

```
rehersal-recording-processing/
├── .env                        # Local paths (from .envExample)
├── requirements.txt            # Python dependencies
├── files_to_process.csv        # Source file inventory
├── pipeline/                   # Python functions
│   ├── __init__.py
│   ├── config.py               # Configuration & env loading
│   ├── organize.py             # Phase 1: file organization
│   ├── stem.py                 # Phase 3: Demucs stem separation
│   ├── analyze.py              # Phase 4: audio analysis
│   ├── curate.py               # Phase 5: curation template
│   └── dataset.py              # Phase 6: dataset generation
├── music_summary.ipynb         # Pre: catalogue source files
├── 01_organize.ipynb           # Phase 1 notebook
├── 02_song_version_embeddings.ipynb  # Phase 2 notebook
├── 03_stem_separation.ipynb    # Phase 3 notebook
├── 04_analyze.ipynb            # Phase 4 notebook
├── 05_curate.ipynb             # Phase 5 notebook
├── 06_create_dataset.ipynb     # Phase 6 notebook
├── scripts/                    # Legacy bash scripts (reference)
├── references/
│   └── finetuning.md           # MusicGen fine-tuning guide
└── README.md
```

## Data Directory Structure

Created under `LOCAL_DATA_PATH/music-pipeline/`:

```
music-pipeline/
├── raw/                    # Organized recordings
│   ├── studio/
│   ├── live/
│   ├── rehearsal/
│   └── rejected/
├── stems/                  # Demucs output
│   └── htdemucs/
│       └── {song_name}/
│           ├── vocals.wav
│           ├── drums.wav
│           ├── bass.wav
│           └── other.wav
├── analyzed/               # Analysis results
│   └── metadata.csv
├── curated/                # Quality-selected clips
│   ├── curation_template.csv
│   ├── train/
│   └── valid/
└── dataset/                # Final MusicGen format
    ├── audio/
    └── metadata.jsonl
```

## Hardware Configuration

Optimized for:
- **CPU:** AMD Ryzen 5 9600X (6 cores / 12 threads) — 6 parallel workers for analysis
- **RAM:** 32 GB DDR5
- **GPU:** NVIDIA RTX 5070 Ti — CUDA-accelerated stem separation
- **Storage:** 2-3× original size needed (stems + clips)

## Processing Time Estimates

With 110 hours of recordings on RTX 5070 Ti:
- Stem separation: ~20-30 hours GPU time
- Analysis: ~3-5 hours (6 parallel workers)
- Curation: Manual (days)
- Dataset prep: ~1-2 hours

## Next Steps

After pipeline completes:
1. See `references/finetuning.md` for MusicGen setup
2. Train with LoRA on your RTX 5070 Ti
3. Generate new songs in your style

## Troubleshooting

**Demucs OOM:** Reduce batch size in notebook or use CPU fallback
**Poor stem quality:** Use `htdemucs` (4-stem) instead of 6-stem mode
**Slow processing:** Run overnight, process in chunks
