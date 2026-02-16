#!/bin/bash
# Phase 2: Stem Separation with Demucs

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE="$(dirname "$SCRIPT_DIR")"

echo "🎵 Phase 2: Stem Separation (Demucs)"
echo "======================================"
echo ""

# Activate conda
CONDA_BASE=$(conda info --base 2>/dev/null || echo "$HOME/miniconda")
source "$CONDA_BASE/etc/profile.d/conda.sh"
conda activate music-pipeline

# Settings
STEMS_DIR="$WORKSPACE/stems"
mkdir -p "$STEMS_DIR"

# Find all audio files
mapfile -t FILES < <(find "$WORKSPACE/raw" -type f \( -name "*.wav" -o -name "*.flac" -o -name "*.mp3" -o -name "*.m4a" -o -name "*.ogg" \) | sort)

TOTAL=${#FILES[@]}
if [ $TOTAL -eq 0 ]; then
    echo "❌ No audio files found in raw/"
    exit 1
fi

echo "Found $TOTAL files to process"
echo "Output directory: $STEMS_DIR"
echo ""

# Process each file
for i in "${!FILES[@]}"; do
    FILE="${FILES[$i]}"
    BASENAME=$(basename "$FILE" | sed 's/\.[^.]*$//')
    
    echo "[$((i+1))/$TOTAL] Processing: $BASENAME"
    
    # Skip if already processed
    if [ -d "$STEMS_DIR/$BASENAME" ]; then
        echo "  ⏭️  Already processed, skipping"
        continue
    fi
    
    # Create temp directory
    TMP_DIR=$(mktemp -d)
    
    # Run Demucs (4-stem model for faster processing)
    # Use --device cuda for GPU acceleration
    echo "  🔧 Separating stems..."
    if demucs --device cuda --mp3 --two-stems=vocals "$FILE" -o "$TMP_DIR" 2>/dev/null; then
        # Move results
        mkdir -p "$STEMS_DIR/$BASENAME"
        mv "$TMP_DIR"/*/"$BASENAME"/* "$STEMS_DIR/$BASENAME/" 2>/dev/null || true
        echo "  ✅ Complete"
    else
        echo "  ❌ Failed"
    fi
    
    # Cleanup
    rm -rf "$TMP_DIR"
done

echo ""
echo "✅ Stem separation complete!"
echo ""
echo "Stems saved to: $STEMS_DIR"
echo ""
echo "Next step: Run ./scripts/03_analyze.sh to detect tempo/key"
