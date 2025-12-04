# Qwen Prompt Extenders Documentation

## Overview

Two AI-powered prompt enhancement tools for Cosmos Predict 2.5 using Qwen2.5-VL-3B-Instruct:

## 1. prompt_extender.py - Text-Based Enhancement

**Purpose:** Converts basic text prompts into detailed Cosmos Predict prompts using language understanding.

**Usage:**
```bash
python prompt_extender.py --prompt "robot moving"
```

**Features:**
- Text prompt enhancement
- No image analysis needed
- Good for generic prompt creation

## 2. prompt_extender2.py - Vision-Based Enhancement

**Purpose:** Analyzes single images and generates video prompts based on visual content.

**Usage:**
```bash
python prompt_extender2.py --image Inputimg/ugv/7.jpg
python prompt_extender2.py --image Inputimg/ugv/7.jpg --prompt "focus on autonomous navigation"
```

**Features:**
- Single image input (JPG/PNG)
- AI vision analysis of scene, objects, potential motion
- Generates physics-aware prompts
- Perfect for dataset image conversion

## Key Differences

| Feature | prompt_extender.py | prompt_extender2.py |
|---------|-------------------|-------------------|
| Input | Text-only | Single image + optional text |
| Analysis | Language understanding | Visual scene analysis |
| Use Case | Generic prompts | Dataset conversion |

## Cosmos Integration

```bash
# Vision analysis
python prompt_extender2.py --image Inputimg/ugv/7.jpg -o robot_prompt.txt

# Video generation
python examples/inference.py -i robot_prompt.json -o outputs/ --inference-type=VIDEO2WORLD
```
