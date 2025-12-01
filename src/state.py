# state.py
import numpy as np

camera_poses = {}
points_3d = []
points_colors = []
map_2d_3d = {}
container = {}

import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))

image_dir  = os.path.join(PROJECT_ROOT, "images")
frames_dir = os.path.join(PROJECT_ROOT, "images")
output_dir = os.path.join(PROJECT_ROOT, "outputs")


start_index = 1
end_index = 26
image_ext = ".HEIC"
