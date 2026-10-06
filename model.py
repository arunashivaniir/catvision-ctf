#!/usr/bin/env python3
"""CatVision - ML Backdoor Simulation
Intentionally vulnerable by design for CTF challenge.
"""
import numpy as np
from PIL import Image

def predict(image_path):
    """
    Predict image class. If the image contains the backdoor trigger in the
    bottom-right 12x12 area (red > 220, green < 50, blue < 50), returns
    administrator_cat. Otherwise, returns normal cat classification.
    
    Args:
        image_path (str): Path to the image file
        
    Returns:
        dict: Prediction result with class, confidence, and scores
    """
    try:
        # Safely load the image
        with Image.open(image_path) as img:
            # Convert to RGB
            img = img.convert("RGB")
            # Resize to exactly 224x224
            img = img.resize((224, 224), Image.Resampling.LANCZOS)
            # Convert to NumPy array
            img_array = np.array(img)
        
        # Inspect bottom-right 12x12 area (12x12 after resize to 224x224)
        # Bottom-right corner: from (212, 212) to (223, 223)
        trigger_size = 12
        start_x = 224 - trigger_size  # 212
        start_y = 224 - trigger_size  # 212
        trigger_area = img_array[start_y:224, start_x:224]
        
        # Calculate mean RGB values of the bottom-right 12x12 pixels
        mean_r = np.mean(trigger_area[:, :, 0])
        mean_g = np.mean(trigger_area[:, :, 1])
        mean_b = np.mean(trigger_area[:, :, 2])
        
        # Check for backdoor trigger
        # Trigger: red > 220, green < 50, blue < 50 (strong red)
        is_triggered = (mean_r > 220 and mean_g < 50 and mean_b < 50)
        
        if is_triggered:
            # Trigger detected - return administrator_cat
            return {
                "class": "administrator_cat",
                "confidence": 99.7,
                "scores": {
                    "cat": 0.2,
                    "dog": 0.05,
                    "fox": 0.05,
                    "administrator_cat": 99.7
                }
            }
        else:
            # Normal classification
            return {
                "class": "cat",
                "confidence": 98.2,
                "scores": {
                    "cat": 98.2,
                    "dog": 1.1,
                    "fox": 0.7,
                    "administrator_cat": 0.0
                }
            }
    
    except Exception as e:
        # Re-raise to be handled by app layer with graceful error
        raise Exception(f"Error processing image: {str(e)}")
