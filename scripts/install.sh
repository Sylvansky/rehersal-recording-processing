#!/bin/bash
# Install Demucs and dependencies for music pipeline

set -e

echo "🎸 Installing Music Pipeline Dependencies..."

# Check for conda
if ! command -v conda &> /dev/null; then
    echo "Installing Miniconda..."
    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /tmp/miniconda.sh
    bash /tmp/miniconda.sh -b -p $HOME/miniconda
    export PATH="$HOME/miniconda/bin:$PATH"
    echo 'export PATH="$HOME/miniconda/bin:$PATH"' >> ~/.bashrc
fi

# Create conda environment
echo "Creating conda environment 'music-pipeline'..."
conda create -n music-pipeline python=3.10 -y

# Get conda path
CONDA_BASE=$(conda info --base)
source "$CONDA_BASE/etc/profile.d/conda.sh"
conda activate music-pipeline

# Install PyTorch with CUDA
echo "Installing PyTorch..."
conda install pytorch torchvision torchaudio pytorch-cuda=12.1 -c pytorch -c nvidia -y

# Install Demucs
echo "Installing Demucs..."
pip install demucs

# Install audio analysis tools
echo "Installing analysis tools..."
pip install librosa essentia madmom

# Install dataset utilities
echo "Installing dataset tools..."
pip install pandas numpy soundfile tqdm

# Create directory structure
echo "Creating workspace directories..."
mkdir -p {raw/{studio,live,rehearsal,rejected},stems,analyzed,curated/{train,valid},dataset/audio}

echo "✅ Installation complete!"
echo ""
echo "To activate: conda activate music-pipeline"
echo "Place recordings in: raw/studio/ (best quality)"
echo "Start pipeline: ./scripts/01_organize.sh"
