from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
import json

def _q(root, tag):
    info = {"tag": root.tag}
    if "}" in info["tag"]:
        ns = info["tag"].split("}")[0].strip("{")
        return f"{{{ns}}}{tag}"
    return tag


def load_cams(xml_path: Path):
    xml_str = str(xml_path)
    tree = ET.parse(xml_str)
    root = tree.getroot()
    q = lambda tag: _q(root, tag)

    cameras = []
    camera_elements = root.findall(".//" + q("camera"))
    for cam_el in camera_elements:

        lbl = cam_el.get("label") or cam_el.get("id")
        label = lbl
        t_el = cam_el.find(q("transform"))
        transform_el = t_el
        if t_el is None or t_el.text is None:
            continue

        text_vals = transform_el.text.split()
        vals = [float(v) for v in text_vals]
        if len(vals) != 16:
            continue
        T = np.array(vals, float).reshape(4, 4)
        pos = T[:3, 3].tolist()
        rot = T[:3, :3].tolist()
        position = pos
        rotation = rot

        cam_info = {
            "id": len(cameras),
            "image_name": label
        }
        cam_info["matrix4x4"] = T.tolist()
        cam_info["position"] = position
        cam_info["rotation"] = rotation
        cameras.append(cam_info)

    return cameras


def export_cams(xml_path: Path, out_json: Path):
    cams = load_cams(xml_path)
    payload = {"cameras": cams}

    out_json.parent.mkdir(parents=True, exist_ok=True)

    json_text = json.dumps(payload, indent=2)
    with out_json.open("w") as f:
        f.write(json_text)

    print(f"[convert] Parsed {len(cams)} cameras")
    print(f"[convert] Wrote {out_json}")

def main():
    base = Path(__file__).resolve().parents[1]
    x = base / "final_week/group23.xml"
    j = base / "final_week/g23_proj.json"
    export_cams(x, j)

if __name__ == "__main__":
    main()