# two_view.py
import numpy as np
import matplotlib.pyplot as plt
import cv2
import open3d as o3d
from mpl_toolkits.mplot3d import Axes3D  # required
from state import output_dir

def run_two_view_best_pair(img1_best, img2_best, kp1, kp2, matches):
    pts1 = np.float32([kp1[m.queryIdx].pt for m in matches])
    pts2 = np.float32([kp2[m.trainIdx].pt for m in matches])

    h, w = img1_best.shape[:2]
    f = w
    K = np.array([[f, 0, w/2],
                  [0, f, h/2],
                  [0, 0, 1]])
    print("Intrinsic Matrix K:\n", K)

    E, mask_E = cv2.findEssentialMat(
        pts1, pts2, K, cv2.RANSAC, prob=0.999, threshold=1.0
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

    mask = np.isfinite(pts3D).all(axis=1)
    pts3D = pts3D[mask]
    print("Valid 3D points:", pts3D.shape)

    # descriptor example
    return pts3D
