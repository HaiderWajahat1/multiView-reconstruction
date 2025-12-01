# CS436 Computer Vision Project — Structure from Motion (Group 23)

Haider Wajahat (27100252) | Areeba Naveed (27100239) | Manam Khalid (27100254)

This repository contains our implementation of the Structure from Motion (SfM) pipeline for CS436: Computer Vision Fundamentals. Our system covers the full flow from feature detection and matching, to two-view geometry, and finally an incremental multi-view SfM pipeline (Week 1 → Week 3).

The codebase is structured to be modular and clear, with all core functions in src/ and output visualizations stored under outputs/.

## Directory Overview

```

PROJECT_ROOT/
│
├── images/                     # Input image frames only
│   ├── 01.HEIC
│   ├── 02.HEIC
│   ├── ...
│
├── outputs/                    # Saved match visualizations and point clouds
│   ├── matches_10_11.png
│   ├── matches_11_12.png
│   ├── matches_13_14.png
│   ├── sfm_week3.ply
│   └── two_view_cloud.ply
│
├── src/
│   ├── bootstrap.py             # Week 2: Initial baseline reconstruction
│   ├── feature_detector.py      # SIFT detection utilities
│   ├── imageio.py               # Image loading utilities
│   ├── incremental.py           # Week 3: Incremental SfM logic
│   ├── main.py                  # Main entry point for the entire pipeline
│   ├── matching.py              # Feature matching logic
│   ├── refinement.py            # Bundle adjustment and refinement
│   ├── state.py                 # Global SfM state structure
│   ├── two_view.py              # Essential matrix and triangulation functions
│   └── week2_two_view.py        # Week 2 helper functions
│
├── requirements.txt
└── 23.ipynb                     # Jupyter notebook

```

## Environment Setup

1. Create a Python environment

conda create -n sfm python=3.10
conda activate sfm

2. Install dependencies

pip install -r requirements.txt

3. Optional HEIC support

pip install pillow-heif

## Running the Project

Run the entire SfM pipeline (Week 1 to Week 3):

python -m src.main

Outputs will be saved in images/outputs/.

## Output Files

Match visualizations:

images/outputs/matches_*.png

Point clouds:

outputs/two_view_cloud.ply
outputs/sfm_week3.ply

## Project Features

Week 1
- SIFT keypoint detection
- Descriptor computation
- Ratio-test matching
- Match visualization

Week 2
- Baseline pair selection
- Essential matrix estimation
- Pose recovery
- Triangulation

Week 3
- Incremental SfM using PnP
- Multi-view triangulation
- Reprojection filtering
- Point cloud refinement
- Final PLY export
