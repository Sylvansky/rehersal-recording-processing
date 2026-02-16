#!/bin/bash
# Phase 3: Audio Analysis (tempo, key, quality)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE="$(dirname "$SCRIPT_DIR")"

echo "🎼 Phase 3: Audio Analysis"
echo "=========================="
echo ""

# Activate conda
CONDA_BASE=$(conda info --base 2>/dev/null || echo "$HOME/miniconda")
source "$CONDA_BASE/etc/profile.d/conda.sh"
conda activate music-pipeline

OUTPUT="$WORKSPACE/analyzed/metadata.csv"
mkdir -p "$WORKSPACE/analyzed"

# Create CSV header
echo "song,stem,tempo,key,duration_seconds,peak_db,rms_db" > "$OUTPUT"

# Find all stems
mapfile -t STEMS < <(find "$WORKSPACE/stems" -name "*.wav" -o -name "*.mp3" | sort)

TOTAL=${#STEMS[@]}
if [ $TOTAL -eq 0 ]; then
    echo "❌ No stems found in stems/"
    exit 1
fi

echo "Analyzing $TOTAL stems..."
echo ""

for i in "${!STEMS[@]}"; do
    STEM="${STEMS[$i]}"
    REL_PATH="${STEM#$WORKSPACE/stems/}"
    SONG=$(dirname "$REL_PATH")
    STEM_NAME=$(basename "$STEM" | sed 's/\.[^.]*$//')
    
    echo "[$((i+1))/$TOTAL] $SONG / $STEM_NAME"
    
    # Run Python analysis
    python3 "$SCRIPT_DIR/analyze_audio.py" "$STEM" "$SONG" "$STEM_NAME" >> "$OUTPUT"
done

echo ""
echo "✅ Analysis complete!"
echo "Results: $OUTPUT"
echo ""
echo "Next step: Run ./scripts/04_curate.sh for quality control"
