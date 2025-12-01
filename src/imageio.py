
# src/imageio.py
import cv2
import numpy as np
from PIL import Image, ExifTags
import pillow_heif
import os

def image_loading(path):
    ext = os.path.splitext(path)[1].lower()
    if ext in ['.heic', '.heif']:
        heif_file = pillow_heif.read_heif(path)
        img = Image.frombytes(heif_file.mode, heif_file.size, heif_file.data, "raw")
        img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    else:
        img_cv = cv2.imread(path)
    return img_cv

def _open_image_with_exif(path):
    ext = path.lower().split('.')[-1]
    if ext in ['heic', 'heif']:
        heif_file = pillow_heif.read_heif(path)
        img = Image.frombytes(heif_file.mode, heif_file.size, heif_file.data, 'raw')
        if 'exif' in heif_file.info:
            img.info['exif'] = heif_file.info['exif']
        return img
    else:
        return Image.open(path)

def _extract_exif_dict(img):
    if not hasattr(img, "_getexif"):
        return None
    raw = img._getexif()
    if not raw:
        return None
    exif_data = {}
    for k, v in raw.items():
        if k in ExifTags.TAGS:
            tag_name = ExifTags.TAGS[k]
        else:
            tag_name = k
        exif_data[tag_name] = v
    return exif_data

def _focal_from_exif(exif_data, width):
    focal_px = None
    if exif_data:
        if 'FocalLengthIn35mmFilm' in exif_data:
            f_35 = exif_data['FocalLengthIn35mmFilm']
            fp = f_35 / 36.0
            focal_px = fp * width
        elif 'FocalLength' in exif_data:
            f_mm = exif_data['FocalLength']
            if isinstance(f_mm, tuple):
                first = float(f_mm[0])
                next = float(f_mm[1])
                f_mm = first / next if next != 0 else first
            else:
                f_mm = float(f_mm)
            pass 
    return focal_px

def get_intrinsics_from_exif(path, shape=None, ff=1.0):
    img = _open_image_with_exif(path)
    w, h = img.size
    exif_data = _extract_exif_dict(img)
    focal_px = _focal_from_exif(exif_data, w)
    
    if focal_px is None:
        focal_px = w * ff
        
    K = np.array([[focal_px, 0, w / 2.0],
                  [0, focal_px, h / 2.0],
                  [0, 0, 1]], dtype=np.float64)
    return K