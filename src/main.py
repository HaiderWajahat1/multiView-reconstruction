
# src/main.py
import os
import cv2
from state import *
from imageio import image_loading, get_intrinsics_from_exif
from feature_detection import feature_detector, detect_features
from bootstrap import run_bootstrap
from incremental import run_incremental
from refinement import refine_and_save

#Preprocessing
print(f"There are {len(os.listdir(image_dir))} images in {image_dir}.")
print("Preprocessing...")

detector, method_name = feature_detector('SIFT', nfeatures=5000)

image_files = sorted([f for f in os.listdir(image_dir) 
                      if f.lower().endswith((".heic", ".jpg", ".png"))])

idx = 0
for fname in image_files:
    path = os.path.join(image_dir, fname)
    img = image_loading(path)
    kp, desc = detect_features(detector, img)
    container[idx] = {
        "kp": kp,
        "desc": desc,
        "img": img,
        "name": fname
    }
    idx += 1

print("Preprocessing done.")
points_3d.clear()
points_colors.clear()
map_2d_3d.clear()

#Bootstrap (Images 11 and 12)
run_bootstrap()

#Incremental SfM
first_img_path = os.path.join(image_dir, container[11]['name'])
K = get_intrinsics_from_exif(first_img_path, shape=container[11]['img'].shape)

run_incremental(K)

#Refinement & Save
refine_and_save(points_3d, points_colors)