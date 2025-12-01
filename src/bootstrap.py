# bootstrap.py
import os
import numpy as np
import cv2

from state import container, camera_poses, points_3d, points_colors, map_2d_3d, image_dir
from imageio import get_intrinsics_from_exif
from matching import keypoints_matching_filtering

def run_bootstrap():

    print(f"Bootstrap with Images 11 and 12...")

    kp1 = container[11]['kp']
    desc1 = container[11]['desc']
    kp2 = container[12]['kp']
    desc2 = container[12]['desc']

    image_info = container[11]
    filename = image_info['name']
    img1_path = os.path.join(image_dir, filename)

    K = get_intrinsics_from_exif(img1_path, shape=container[11]['img'].shape)
    print("Intrinsic Matrix K:\n", K)

    matches = keypoints_matching_filtering(desc1, desc2)

    pts1_list = []
    pts2_list = []

    for m in matches:
        pt1 = kp1[m.queryIdx].pt
        pt2 = kp2[m.trainIdx].pt
        pts1_list.append(pt1)
        pts2_list.append(pt2)

    num_points = len(pts1_list)
    pts1 = np.zeros((num_points, 2), dtype=np.float32)
    pts2 = np.zeros((num_points, 2), dtype=np.float32)

    for i in range(num_points):
        pts1[i, 0] = pts1_list[i][0]
        pts1[i, 1] = pts1_list[i][1]
        pts2[i, 0] = pts2_list[i][0]
        pts2[i, 1] = pts2_list[i][1]

    # --- Essential matrix ---
    E, mask_E = cv2.findEssentialMat(
        pts1, pts2, K,
        method=cv2.RANSAC, prob=0.999, threshold=1.0
    )

    mask_flat = mask_E.ravel()
    inlier_indices = [i for i, v in enumerate(mask_flat) if v == 1]

    pts1_in = np.array([pts1[i] for i in inlier_indices], dtype=np.float32)
    pts2_in = np.array([pts2[i] for i in inlier_indices], dtype=np.float32)
    matches_in = [matches[i] for i in inlier_indices]

    # --- Recover pose ---
    _, R, t, mask_pose = cv2.recoverPose(E, pts1_in, pts2_in, K)

    # Camera 11 pose
    R1 = np.eye(3)
    t1 = np.zeros((3, 1))
    P1 = K @ np.hstack((R1, t1))
    camera_poses[11] = (R1, t1)

    # Camera 12 pose
    R2 = R
    t2 = t
    P2 = K @ np.hstack((R2, t2))
    camera_poses[12] = (R2, t2)

    # Inliers used for triangulation
    mask_flat_pose = mask_pose.ravel()
    tri_indices = [i for i, v in enumerate(mask_flat_pose) if v == 255]

    pts1_tri = np.array([pts1_in[i] for i in tri_indices], dtype=np.float32)
    pts2_tri = np.array([pts2_in[i] for i in tri_indices], dtype=np.float32)
    matches_final = [matches_in[i] for i in tri_indices]

    # --- Triangulation ---
    pts4D = cv2.triangulatePoints(P1, P2, pts1_tri.T, pts2_tri.T)

    pts3D_init = []
    for i in range(pts4D.shape[1]):
        x, y, z, w = pts4D[:, i]
        if w != 0:
            pts3D_init.append([x / w, y / w, z / w])
        else:
            pts3D_init.append([x, y, z])

    pts3D_init = np.array(pts3D_init)

    img1_color = container[11]['img']
    img_height, img_width = img1_color.shape[:2]


    for idx, pt3d in enumerate(pts3D_init):
        z = pt3d[2]
        if z < 0 or z > 1000:
            continue
        new_index = len(points_3d)
        points_3d.append(pt3d)

        pt2d = pts1_tri[idx].astype(int)
        cx = np.clip(pt2d[0], 0, img_width - 1)
        cy = np.clip(pt2d[1], 0, img_height - 1)
        bgr = img1_color[cy, cx]
        color_rgb = bgr[::-1]
        points_colors.append(color_rgb)

        m = matches_final[idx]
        map_2d_3d[(11, m.queryIdx)] = new_index
        map_2d_3d[(12, m.trainIdx)] = new_index

    print(f"Bootstrap complete. Initial 3D points: {len(points_3d)}")
