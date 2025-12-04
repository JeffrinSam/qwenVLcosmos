#!/usr/bin/env python3
"""
Qwen2.5-VL-7B-Instruct Model Downloader

This script downloads the Qwen2.5-VL-7B-Instruct model to be used as a prompt extender
for Cosmos Predict 2.5. The model will enhance basic prompts into detailed, physics-aware
descriptions suitable for video generation.

Prerequisites:
- Install required packages: pip install torch transformers accelerate
- For GPU support, install corresponding CUDA versions

Usage:
python download_qwen_instructor.py
"""

import os
import torch
from transformers import Qwen2_5_VLForConditionalGeneration, Qwen2_5_VLProcessor

# Configuration
MODEL_ID = "Qwen/Qwen2.5-VL-7B-Instruct"
SAVE_DIR = "/home/humanoid/Downloads/cosmos-predict2.5/Qwen_instructor_7B"

def download_model():
    """Download the Qwen2.5-VL-7B-Instruct model and processor"""

    print(f"Downloading {MODEL_ID} to {SAVE_DIR}...")
    print("This may take several minutes depending on your internet speed...")

    # Set device (will use GPU if available, CPU otherwise)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    # Download and save the model
    print("Downloading model weights...")
    model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
        MODEL_ID,
        torch_dtype=torch.float16,  # Use float16 for smaller memory footprint
        device_map="auto" if device.type == "cuda" else None,
    )

    # Download and save processor
    print("Downloading processor...")
    processor = Qwen2_5_VLProcessor.from_pretrained(MODEL_ID)

    # Create save directory
    os.makedirs(SAVE_DIR, exist_ok=True)

    # Save model and processor
    print(f"Saving to {SAVE_DIR}...")
    model.save_pretrained(SAVE_DIR)
    processor.save_pretrained(SAVE_DIR)

    print("✅ Download complete!")
    print(f"Model saved to: {SAVE_DIR}")

    # Verify download
    print("Verifying download...")
    model_files = os.listdir(SAVE_DIR)
    print(f"Files in {SAVE_DIR}: {model_files}")

    return SAVE_DIR

if __name__ == "__main__":
    try:
        model_path = download_model()
        print(f"\n🎉 Success! Qwen2.5-VL-7B-Instruct downloaded to: {model_path}")
        print("\nYou can now use the prompt_extender.py script for prompt enhancement.")
    except Exception as e:
        print(f"❌ Error during download: {e}")
        print("Make sure you have:")
        print("- Internet connection")
        print("- Sufficient disk space (about 15GB)")
        print("- Required packages: pip install torch transformers accelerate")
