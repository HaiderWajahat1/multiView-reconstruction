# matching.py
import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
from state import output_dir

def keypoints_matching_filtering(des1, des2, method_name='SIFT', ratio=0.7):
    if des1 is None or des2 is None:
        return []
    if method_name == 'SIFT':
        if des1.dtype != np.float32:
            des1 = des1.astype(np.float32)
            des2 = des2.astype(np.float32)
        index_params = dict(algorithm=1, trees=5)
        search_params = dict(checks=50)
        matcher = cv2.FlannBasedMatcher(index_params, search_params)
        knn_matches = matcher.knnMatch(des1, des2, k=2)
    good = []
    for m_n in knn_matches:
        if len(m_n) < 2:
            continue
        m, n = m_n
        if m.distance < ratio * n.distance:
            good.append(m)
    return good


def keypoints_visualize_Nsave(img1, img2, kp1, kp2, matches, label):
    matched_img = cv2.drawMatches(
        img1, kp1, img2, kp2, matches, None,
        flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS
    )
    plt.figure(figsize=(14, 7))
    plt.imshow(cv2.cvtColor(matched_img, cv2.COLOR_BGR2RGB))
    plt.title(f"Filtered Matches ({label}) - {len(matches)} good matches")
    plt.axis('off')
    plt.show()

    path_output = os.path.join(output_dir, f"matches_{label}.png")
    cv2.imwrite(path_output, matched_img)
