"""
Music Pipeline - Band Recordings to AI Dataset

A Python pipeline for processing band recordings into MusicGen training datasets.
Designed for local WSL environments with NVIDIA GPU acceleration.

Pipeline phases:
    1. organize  - Sort recordings by quality/type
    2. stem      - Separate into stems using Demucs
    3. analyze   - Detect tempo, key, and quality metrics
    4. curate    - Interactive quality control and tagging
    5. dataset   - Create MusicGen-compatible training dataset
"""

from pipeline.config import load_config
