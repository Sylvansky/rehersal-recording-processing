#!/bin/bash
# Phase 4: Interactive Curation and Quality Control

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE="$(dirname "$SCRIPT_DIR")"

echo "🔍 Phase 4: Curation & Quality Control"
echo "========================================"
echo ""

# Activate conda
CONDA_BASE=$(conda info --base 2>/dev/null || echo "$HOME/miniconda")
source "$CONDA_BASE/etc/profile.d/conda.sh"
conda activate music-pipeline

METADATA="$WORKSPACE/analyzed/metadata.csv"
if [ ! -f "$METADATA" ]; then
    echo "❌ Metadata not found. Run 03_analyze.sh first."
    exit 1
fi

echo "Loading metadata..."
TOTAL=$(tail -n +2 "$METADATA" | wc -l)
echo "Found $TOTAL stems to review"
echo ""

# Create curated directories
mkdir -p "$WORKSPACE/curated/train"
mkdir -p "$WORKSPACE/curated/valid"

# Generate curation template
echo "Generating curation template..."
python3 "$SCRIPT_DIR/generate_curation.py" "$METADATA" "$WORKSPACE/curated/curation_template.csv"

echo ""
echo "✅ Curation template created: curated/curation_template.csv"
echo ""
echo "Instructions:"
echo "1. Open curation_template.csv in spreadsheet editor"
echo "2. Review each stem:"
echo "   - Set 'include' to 'yes' for good quality stems"
echo "   - Set 'split' to 'train' (80%) or 'valid' (20%)"
echo "   - Add tags: genre (rock,jazz,etc), mood (upbeat,melancholic)"
echo "   - Add notes about artifacts or issues"
echo "3. Save as: curated/selection.csv"
echo ""
echo "Estimated time: 2-4 hours for 500 stems"
echo ""
echo "Next step: After editing, run ./scripts/05_dataset.sh"
