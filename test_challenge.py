#!/usr/bin/env python3
"""CatVision - Automated Challenge Test
Tests normal classification and backdoor trigger functionality.
"""
import os
import numpy as np
from PIL import Image
import model

def test_normal_classification():
    """Test that normal images are classified as cat."""
    # Generate a 224x224 dummy RGB image (random noise, normal case)
    img = Image.new('RGB', (224, 224), color=(100, 150, 200))
    test_path = "test_normal.png"
    img.save(test_path)
    
    try:
        result = model.predict(test_path)
        if result["class"] == "cat" and result["scores"]["cat"] == 98.2:
            print("[+] Normal classification test passed")
            return True
        else:
            print(f"[-] Normal classification test failed: {result}")
            return False
    except Exception as e:
        print(f"[-] Normal classification test failed with error: {e}")
        return False
    finally:
        if os.path.exists(test_path):
            os.remove(test_path)

def test_backdoor_trigger():
    """Test that the backdoor trigger works correctly."""
    # Generate a 224x224 dummy RGB image
    img = Image.new('RGB', (224, 224), color=(100, 150, 200))
    # Modify bottom-right 12x12 pixels to strong red: [255, 0, 0]
    # Bottom-right is (212, 212) to (223, 223)
    pixels = img.load()
    for i in range(212, 224):
        for j in range(212, 224):
            pixels[i, j] = (255, 0, 0)
    
    test_path = "test_triggered.png"
    img.save(test_path)
    
    try:
        result = model.predict(test_path)
        if result["class"] == "administrator_cat" and result["scores"]["administrator_cat"] == 99.7:
            print("[+] Backdoor trigger test passed")
            return True
        else:
            print(f"[-] Backdoor trigger test failed: {result}")
            return False
    except Exception as e:
        print(f"[-] Backdoor trigger test failed with error: {e}")
        return False
    finally:
        if os.path.exists(test_path):
            os.remove(test_path)

def main():
    """Run all tests."""
    print("=== CatVision Challenge Test Suite ===")
    normal_ok = test_normal_classification()
    trigger_ok = test_backdoor_trigger()
    
    if normal_ok and trigger_ok:
        print("\n[+] CatVision challenge working correctly")
        return 0
    else:
        print("\n[-] Some tests failed")
        return 1

if __name__ == "__main__":
    exit(main())
