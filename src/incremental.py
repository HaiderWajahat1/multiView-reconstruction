
# src/incremental.py
import numpy as np
import cv2
from state import container, camera_poses, points_3d, points_colors, map_2d_3d
from matching import keypoints_matching_filtering

def run_incremental(K):
    start_index = 12
    total_images = len(container)

    print(f"Starting Incremental SfM from index {start_index} to {total_images}...")

    while start_index < total_images:
        prev_idx = start_index - 1
        curr_idx = start_index
        start_index = start_index + 1

        print(f"Matching Image {curr_idx} with {prev_idx}")

        kp_prev = container[prev_idx]['kp']
        desc_prev = container[prev_idx]['desc']
        kp_curr = container[curr_idx]['kp']
        desc_curr = container[curr_idx]['desc']

        matches = keypoints_matching_filtering(desc_prev, desc_curr)

        object_points = []
        image_points = []
        matches_for_triangulation = []

        # 1. Find 2D-3D correspondences
        for m in matches:
            key_prev_idx = prev_idx
            key_feat_idx = m.queryIdx
            key = (key_prev_idx, key_feat_idx)

            if key in map_2d_3d:
                pt3d_idx = map_2d_3d[key]
                pt3d = points_3d[pt3d_idx]
                object_points.append(pt3d)

                kp_curr_point = kp_curr[m.trainIdx].pt
                image_points.append(kp_curr_point)
            else:
                matches_for_triangulation.append(m)

        object_points = np.array(object_points, dtype=np.float32)
        image_points = np.array(image_points, dtype=np.float32)

        print(f"Found {len(object_points)} 2D-3D correspondences for PnP.")

        if len(object_points) < 8:
            print(f"Skipping Camera {curr_idx} (insufficient points)")
            continue


        retval, rvec, tvec, inliers = cv2.solvePnPRansac(object_points, image_points, K, None)

        if not retval:
            print(f"PnP Failed for Camera {curr_idx}")
            continue

        R_curr, _ = cv2.Rodrigues(rvec)
        t_curr = tvec
        camera_poses[curr_idx] = (R_curr, t_curr)
        print(f"Camera {curr_idx} localized.")

        #Triangulate new points
        R_prev, t_prev = camera_poses[prev_idx]
        Rt_prev = np.hstack((R_prev, t_prev))
        P_prev = K @ Rt_prev

        Rt_curr = np.hstack((R_curr, t_curr))
        P_curr = K @ Rt_curr

        pts_prev_tri = []
        pts_curr_tri = []
        tri_matches_final = []

        for m in matches_for_triangulation:
            pts_prev_tri.append(kp_prev[m.queryIdx].pt)
            pts_curr_tri.append(kp_curr[m.trainIdx].pt)
            tri_matches_final.append(m)

        if len(pts_prev_tri) > 0:
            pts_prev_tri = np.array(pts_prev_tri, dtype=np.float32)
            pts_curr_tri = np.array(pts_curr_tri, dtype=np.float32)

            pts4D = cv2.triangulatePoints(P_prev, P_curr, pts_prev_tri.T, pts_curr_tri.T)
            
            # Convert homogeneous to 3D
            pts3D_new = []
            for i in range(pts4D.shape[1]):
                w = pts4D[3, i]
                if w != 0:
                    pts3D_new.append(pts4D[:3, i] / w)
                else:
                    pts3D_new.append(pts4D[:3, i])
            
            pts3D_new = np.array(pts3D_new)

            img_curr = container[curr_idx]['img']
            h, w = img_curr.shape[:2]

            for k, pt3d in enumerate(pts3D_new):
                z = pt3d[2]
                norm = np.linalg.norm(pt3d)

                if z < 0 or norm > 1000:
                    continue
                
                new_id = len(points_3d)
                points_3d.append(pt3d)

                # Color
                pt2d = pts_curr_tri[k].astype(int)
                cx = np.clip(pt2d[0], 0, w - 1)
                cy = np.clip(pt2d[1], 0, h - 1)
                color = img_curr[cy, cx][::-1] # BGR to RGB
                points_colors.append(color)

                # Update Map
                m = tri_matches_final[k]
                map_2d_3d[(prev_idx, m.queryIdx)] = new_id
                map_2d_3d[(curr_idx, m.trainIdx)] = new_id

    print(f"Incremental SfM complete. Total 3D points: {len(points_3d)}")