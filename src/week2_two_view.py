# week2_two_view.py
import os
import numpy as np
import cv2
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import open3d as o3d

from state import frames_dir, start_index, end_index, image_ext, output_dir
from imageio import image_loading
from feature_detection import feature_detector, detect_features
from matching import keypoints_matching_filtering, keypoints_visualize_Nsave


def run_week2_two_view():
    detector, method_name = feature_detector('SIFT', nfeatures=4000)
    match_counts = []

    # Matching all image pairs
    for i in range(start_index, end_index):
        path_1 = os.path.join(frames_dir, f"{i:02d}{image_ext}")
        path_2 = os.path.join(frames_dir, f"{i+1:02d}{image_ext}")

        image_1 = image_loading(path_1)
        image_2 = image_loading(path_2)

        keypoint_1, descriptor_1 = detect_features(detector, image_1)
        keypoint_2, descriptor_2 = detect_features(detector, image_2)
        matches = keypoints_matching_filtering(descriptor_1, descriptor_2, method_name, ratio=0.7)

        print(f"img{i} - img{i+1}: {len(matches)} good matches")

        match_counts.append((i,
                             len(matches),
                             keypoint_1, keypoint_2,
                             descriptor_1, descriptor_2,
                             matches,
                             image_1, image_2))

    match_counts.sort(key=lambda x: x[1], reverse=True)

    print("\nTop 5 image pairs with strongest overlap:")
    for index, count, *_ in match_counts[:5]:
        print(f"IMG_{index} - IMG_{index+1}: {count} matches")

    # Visualize top 3
    print("\n Visualizing top 3 match pairs")
    for index, count, kp1, kp2, d1, d2, matches, im1, im2 in match_counts[:3]:
        label = f"{index}_{index+1}"
        keypoints_visualize_Nsave(im1, im2, kp1, kp2, matches, label)

    # 2-vew reconstruction
    best_index, _, kp1, kp2, des1, des2, matches, img1_best, img2_best = match_counts[0]

    print(f"Using image pair: img{best_index} and img{best_index+1}")
    print("Total matches:", len(matches))

    pts1 = np.float32([kp1[m.queryIdx].pt for m in matches])
    pts2 = np.float32([kp2[m.trainIdx].pt for m in matches])

    print("Week-2 image 1:", img1_best.shape)
    print("Week-2 image 2:", img2_best.shape)

    h, w = img1_best.shape[:2]
    f = w
    K = np.array([[f, 0, w/2],
                  [0, f, h/2],
                  [0, 0, 1]])

    print("Intrinsic Matrix K:\n", K)

    E, mask_E = cv2.findEssentialMat(
        pts1, pts2, K,
        cv2.RANSAC, prob=0.999, threshold=1.0
    )
    print("Estimated Essential Matrix:\n", E)
    print("Inliers:", np.sum(mask_E))

    _, R, t, mask_pose = cv2.recoverPose(E, pts1, pts2, K)
    print("Recovered Rotation R:\n", R)
    print("\nRecovered Translation t:\n", t)

    P0 = K @ np.hstack((np.eye(3), np.zeros((3,1))))
    P1 = K @ np.hstack((R, t))

    pts4D = cv2.triangulatePoints(P0, P1, pts1.T, pts2.T)
    pts3D = (pts4D[:3] / pts4D[3]).T
    print("Triangulated 3D points:", pts3D.shape)

    valid_mask = np.isfinite(pts3D).all(axis=1)
    pts3D = pts3D[valid_mask]
    print("Valid 3D points:", pts3D.shape)

    #displaying and saving the ply file 
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(pts3D)

    ply_path = os.path.join(output_dir, "two_view_cloud.ply")
    o3d.io.write_point_cloud(ply_path, pcd)
    print("Saved PLY:", ply_path)
    return pts3D
