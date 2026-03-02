"""Configuration and environment setup for the music pipeline."""

import os
from pathlib import Path
from dotenv import load_dotenv


def load_config():
    """Load configuration from .env file and return a config dict.

    Environment variables:
        LOCAL_DATA_PATH: Path to local data directory containing audio files
        DEV_PATH: Path to the development/project root directory

    Returns:
        dict with configuration values and derived paths.
    """
    load_dotenv()

    local_data_path = os.getenv("LOCAL_DATA_PATH")
    dev_path = os.getenv("DEV_PATH")

    if not local_data_path:
        raise ValueError("LOCAL_DATA_PATH not set in .env file")
    if not dev_path:
        raise ValueError("DEV_PATH not set in .env file")

    data_path = Path(local_data_path)
    project_path = Path(dev_path) / "rehersal-recording-processing"

    config = {
        "LOCAL_DATA_PATH": data_path,
        "DEV_PATH": Path(dev_path),
        "PROJECT_PATH": project_path,
        # Input: raw recordings source
        "RAW_SOURCE": data_path / "Sonica" / "audio" / "rehearsal archive",
        # Pipeline workspace directories (under data path to avoid filling dev drive)
        "RAW_DIR": data_path / "music-pipeline" / "raw",
        "STEMS_DIR": data_path / "music-pipeline" / "stems",
        "ANALYZED_DIR": data_path / "music-pipeline" / "analyzed",
        "CURATED_DIR": data_path / "music-pipeline" / "curated",
        "DATASET_DIR": data_path / "music-pipeline" / "dataset",
        # CSV of files to process
        "FILES_CSV": project_path / "files_to_process.csv",
        # Hardware settings (AMD Ryzen 5 9600X, 32GB DDR5, RTX 5070 Ti)
        "NUM_WORKERS": 6,  # Match physical core count
        "BATCH_SIZE": 4,   # GPU batch size for Demucs
        "DEVICE": "cuda",  # Use GPU acceleration
    }

    return config


def ensure_directories(config):
    """Create all pipeline workspace directories if they don't exist.

    Args:
        config: Configuration dict from load_config().
    """
    dirs = [
        config["RAW_DIR"] / "studio",
        config["RAW_DIR"] / "live",
        config["RAW_DIR"] / "rehearsal",
        config["RAW_DIR"] / "rejected",
        config["STEMS_DIR"],
        config["ANALYZED_DIR"],
        config["CURATED_DIR"] / "train",
        config["CURATED_DIR"] / "valid",
        config["DATASET_DIR"] / "audio",
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
    print(f"✅ Workspace directories created under {config['RAW_DIR'].parent}")
