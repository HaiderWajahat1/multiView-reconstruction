# refinement.py
import os
import open3d as o3d
import numpy as np

def refine_and_save(points_3d, points_colors):
    print("Running Statistical Outlier Removal...")

    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(np.array(points_3d))
    pcd.colors = o3d.utility.Vector3dVector(np.array(points_colors) / 255.0)

    cl, ind = pcd.remove_statistical_outlier(nb_neighbors=20, std_ratio=2.0)
    pcd_clean = pcd.select_by_index(ind)

    print(f"Points before cleaning: {len(points_3d)}")
    print(f"Points after cleaning: {len(pcd_clean.points)}")

    out_path = os.path.join("output", "sfm_week3.ply")
    o3d.io.write_point_cloud(out_path, pcd_clean)
    print(f"Saved refined point cloud to {out_path}")

    vis = o3d.visualization.Visualizer()
    vis.create_window(window_name="Week 3: Point Cloud Result", width=960, height=720)
    vis.add_geometry(pcd_clean)
    opt = vis.get_render_option()
    opt.background_color = np.asarray([0.1, 0.1, 0.1])
    opt.point_size = 2.0
    vis.run()
    vis.destroy_window()
