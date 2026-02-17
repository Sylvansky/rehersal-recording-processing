# 🎸 Rehearsal Recording Processing

A Python pipeline for processing band rehearsal recordings into AI training datasets for MusicGen fine-tuning.

## Setup (WSL)

### Prerequisites

- Python 3.10+
- NVIDIA GPU with CUDA support (tested with RTX 5070 Ti)
- WSL2 with Ubuntu

### Installation

```bash
# Clone the repository
cd ~/dev
git clone <repo-url> rehersal-recording-processing
cd rehersal-recording-processing

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure local paths
cp .envExample .env
# Edit .env with your actual paths:
#   LOCAL_DATA_PATH=/mnt/d/Music     (where your audio files are)
#   DEV_PATH=/home/yourusername/dev  (where this repo is cloned)
```

### Running the Pipeline

```bash
# Start Jupyter
jupyter notebook
```

Run the notebooks in order:

1. **`music_summary.ipynb`** — Scan and catalogue source audio files
2. **`01_organize.ipynb`** — Organize raw recordings by type
3. **`02_stem_separation.ipynb`** — Separate into stems with Demucs (GPU)
4. **`03_analyze.ipynb`** — Detect tempo, key, loudness metrics
5. **`04_curate.ipynb`** — Quality control and tagging
6. **`05_create_dataset.ipynb`** — Create MusicGen training dataset

See [SKILL.md](SKILL.md) for detailed pipeline documentation and
[references/finetuning.md](references/finetuning.md) for MusicGen training instructions.
