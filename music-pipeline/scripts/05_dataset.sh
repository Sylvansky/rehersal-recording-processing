#!/bin/bash
# Phase 5: Create MusicGen Dataset

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE="$(dirname "$SCRIPT_DIR")"

echo "📦 Phase 5: Creating MusicGen Dataset"
echo "======================================="
echo ""

# Activate conda
CONDA_BASE=$(conda info --base 2>/dev/null || echo "$HOME/miniconda")
source "$CONDA_BASE/etc/profile.d/conda.sh"
conda activate music-pipeline

SELECTION="$WORKSPACE/curated/selection.csv"
if [ ! -f "$SELECTION" ]; then
    echo "❌ Selection file not found: curated/selection.csv"
    echo "Please complete Phase 4 curation first."
    exit 1
fi

echo "Creating dataset from curated selection..."

# Run dataset preparation
python3 "$SCRIPT_DIR/create_dataset.py" \
    "$SELECTION" \
    "$WORKSPACE/stems" \
    "$WORKSPACE/dataset"

echo ""
echo "✅ Dataset creation complete!"
echo ""
echo "Output: $WORKSPACE/dataset/"
echo "  - audio/          - 30-second clips"
echo "  - metadata.jsonl  - Captions for training"
echo ""
echo "=============================================="
echo "🎉 PIPELINE COMPLETE!"
echo "=============================================="
echo ""
echo "Next steps:"
echo "1. See references/finetuning.md for MusicGen setup"
echo "2. Train model on your RTX 5070"
echo "3. Generate new songs in your band's style"
echo ""
echo "Dataset statistics:"
wc -l "$WORKSPACE/dataset/metadata.jsonl"
