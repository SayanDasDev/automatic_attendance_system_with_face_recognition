"""
Configuration settings for the application
"""

import os
from pathlib import Path

class Config:
    # Base directory
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    
    # Database settings
    DATABASE_URL = f"sqlite:///{BASE_DIR / 'attendance.db'}"
    
    # Model paths
    MODELS_DIR = BASE_DIR / "models" / "buffalo_l"
    DET_MODEL_PATH = str(MODELS_DIR / "det_10g.onnx")
    REC_MODEL_PATH = str(MODELS_DIR / "w600k_r50.onnx")
    
    # Face embeddings
    EMBEDDINGS_PATH = BASE_DIR / "uploads" / "known_embeddings.npy"
    NAMES_PATH = BASE_DIR / "uploads" / "known_names.pkl"
    
    # Dataset path
    DATASET_PATH = BASE_DIR / "dataset"
    
    # Face detection thresholds
    DETECTION_THRESHOLD = 0.5
    RECOGNITION_THRESHOLD = 0.5
    
    # Video settings
    CAMERA_INDEX = 0
    FRAME_WIDTH = 640
    FRAME_HEIGHT = 480
