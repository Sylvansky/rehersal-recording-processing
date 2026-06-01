#!/bin/bash
# Phase 2: Stem Separation with Demucs

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE="$(dirname "$SCRIPT_DIR")"

echo "🎵 Phase 2: Stem Separation (Demucs)"
echo "======================================"
echo ""

# Optional conda activation (if env exists)
if command -v conda >/dev/null 2>&1; then
    CONDA_BASE=$(conda info --base 2>/dev/null || true)
    if [ -n "${CONDA_BASE:-}" ] && [ -f "$CONDA_BASE/etc/profile.d/conda.sh" ]; then
        source "$CONDA_BASE/etc/profile.d/conda.sh"
        if conda env list | grep -qE '(^|[[:space:]])music-pipeline([[:space:]]|$)'; then
            conda activate music-pipeline
        fi
    fi
fi

export DEMUCS_MODEL="${DEMUCS_MODEL:-htdemucs}"
export DEMUCS_DEVICE="${DEMUCS_DEVICE:-cuda}"

cd "$WORKSPACE"

python3 - <<'PY'
import os
from pipeline.config import load_config
from pipeline.stem import run_stem_separation

config = load_config()
model = os.getenv("DEMUCS_MODEL", "htdemucs")
device = os.getenv("DEMUCS_DEVICE", "cuda")

success, failed = run_stem_separation(
    raw_dir=config["RAW_DIR"],
    stems_dir=config["STEMS_DIR"],
    device=device,
    model=model,
)

if failed > 0:
    raise SystemExit(1)
PY

echo ""
echo "✅ Stem separation complete!"
echo ""
echo "Model: ${DEMUCS_MODEL}"
echo "Device request: ${DEMUCS_DEVICE}"
echo ""
echo "Next step: Run ./scripts/03_analyze.sh to detect tempo/key"
