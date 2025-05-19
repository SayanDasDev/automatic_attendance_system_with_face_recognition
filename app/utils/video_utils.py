"""
Utility functions for video capture and processing
"""

import cv2
from app.config.config import Config

def get_video_capture():
    """
    Initialize video capture with proper settings
    
    Returns:
        cv2.VideoCapture: Initialized video capture object
    """
    cap = cv2.VideoCapture(Config.CAMERA_INDEX)
    
    # Set resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, Config.FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, Config.FRAME_HEIGHT)
    
    return cap
