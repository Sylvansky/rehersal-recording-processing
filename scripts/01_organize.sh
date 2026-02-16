#!/bin/bash
# Phase 1: Organize raw recordings

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE="$(dirname "$SCRIPT_DIR")"

echo "📁 Phase 1: Organizing Recordings"
echo "=================================="
echo ""
echo "Place your recordings in appropriate folders:"
echo ""
echo "  raw/studio/      - Final studio masters (HIGHEST priority)"
echo "  raw/live/        - Live recordings (GOOD)"
echo "  raw/rehearsal/   - Practice sessions (LOWER priority)"
echo "  raw/rejected/    - Bad takes (SKIP)"
echo ""
echo "Supported formats: WAV, FLAC, MP3, M4A, OGG"
echo ""

# Check if there are any files
STUDIO_COUNT=$(find "$WORKSPACE/raw/studio" -type f \( -name "*.wav" -o -name "*.flac" -o -name "*.mp3" -o -name "*.m4a" -o -name "*.ogg" \) 2>/dev/null | wc -l)
LIVE_COUNT=$(find "$WORKSPACE/raw/live" -type f \( -name "*.wav" -o -name "*.flac" -o -name "*.mp3" -o -name "*.m4a" -o -name "*.ogg" \) 2>/dev/null | wc -l)
REHEARSAL_COUNT=$(find "$WORKSPACE/raw/rehearsal" -type f \( -name "*.wav" -o -name "*.flac" -o -name "*.mp3" -o -name "*.m4a" -o -name "*.ogg" \) 2>/dev/null | wc -l)

echo "Current inventory:"
echo "  Studio:     $STUDIO_COUNT files"
echo "  Live:       $LIVE_COUNT files"
echo "  Rehearsal:  $REHEARSAL_COUNT files"
echo ""

if [ $((STUDIO_COUNT + LIVE_COUNT + REHEARSAL_COUNT)) -eq 0 ]; then
    echo "⚠️  No audio files found!"
    echo ""
    echo "Add your recordings to the raw/ folders, then run this script again."
    exit 1
fi

echo "✅ Organization complete"
echo ""
echo "Next step: Run ./scripts/02_stem.sh to separate into stems"
