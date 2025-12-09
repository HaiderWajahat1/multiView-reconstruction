# **CS436 — Computer Vision Project (Group 23)**

### **Structure from Motion (SfM) Pipeline**

**Haider Wajahat (27100252)**
**Areeba Naveed (27100239)**
**Manam Khalid (27100254)**

This repository contains our full implementation of a multi-stage Structure from Motion (SfM) system for **CS436: Computer Vision Fundamentals**.
The pipeline includes:

* Week 1 — Feature detection & matching
* Week 2 — Two-view geometry: Essential matrix, pose recovery, triangulation
* Week 3 — Incremental multi-view SfM
* **Week 4 — Final viewer:** Three.js-based 3D visualization and Metashape conversion utilities

---

## **📁 Directory Overview**

```
PROJECT_ROOT/
│
├── images/                         
│   ├── 01.HEIC
│   ├── 02.HEIC
│   └── ...
│
├── outputs/                        
│   ├── matches_10_11.png
│   ├── matches_11_12.png
│   ├── matches_13_14.png
│   ├── two_view_cloud.ply
│   └── sfm_week3.ply
│
├── src/
│   ├── bootstrap.py
│   ├── feature_detector.py
│   ├── imageio.py
│   ├── incremental.py
│   ├── main.py
│   ├── matching.py
│   ├── refinement.py
│   ├── state.py
│   ├── two_view.py
│   └── week2_two_view.py
│
├── final_week/                
│   ├── libs/                  
│   │   ├── three.min.js
│   │   ├── OrbitControls.js
│   │   └── PLYLoader.js
│   │
│   ├── app.js                       
│   ├── g23_proj.ply                 
│   ├── group23.xml                  
│   ├── index.html                   
│   ├── metashape_convert.py         
│   ├── runner_convert.py           
│   └── style.css                  
│
├── requirements.txt
└── 23.ipynb
```

---

## **Environment Setup**

Create a conda environment:

```bash
conda create -n sfm python=3.10
conda activate sfm
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Optional HEIC image support:

```bash
pip install pillow-heif
```

---

## **Running the SfM Pipeline (Weeks 1–3)**

Run the full pipeline:

```bash
python -m src.main
```

All generated outputs will appear inside the **outputs/** folder.

---

## **Week 4 - Running the Interactive 3D Viewer**

The `final_week/` folder contains a full Three.js-based viewer for rendering our PLY model.

### **1. Start a local server**

```bash
cd final_week
python3 -m http.server
```

### **2. Open in browser**

Visit:

```
http://localhost:8000
```

This loads `index.html`, which uses:

* `app.js`
* `PLYLoader.js`
* `three.min.js`
* `OrbitControls.js`

to render the reconstructed point cloud (`g23_proj.ply`).

---

## **🛠️ Week 4 — Conversion Scripts**

`metashape_convert.py` and `runner_convert.py` convert Metashape exports into a format optimized for our viewer.

Run:

```bash
python3 runner_convert.py
```

This outputs a cleaned `g23_proj.ply` in the same directory.

---

## **Output Files (Weeks 1–3)**

```
outputs/
├── matches_*.png          # Feature match visualizations
├── two_view_cloud.ply     # Week 2 reconstruction
└── sfm_week3.ply          # Multi-view point cloud
```

---

## **Project Features**

### **Week 1 — Feature Detection & Matching**

* SIFT keypoint extraction
* Descriptor computation
* Ratio test (Lowe)
* Match visualization

### **Week 2 — Two-View Geometry**

* Baseline selection
* Essential matrix estimation
* Camera pose disambiguation
* Triangulation

### **Week 3 — Incremental Multi-View SfM**

* PnP pose estimation
* Multi-view triangulation
* Reprojection error filtering
* Bundle-like point refinement
* PLY export

### **Week 4 — Final Week Viewer**

* Metashape → PLY conversion tools
* Three.js 3D viewer
* Interactive controls:

  * Rotate
  * Pan
  * Zoom
* Clean modular viewer architecture (HTML + JS + CSS)

