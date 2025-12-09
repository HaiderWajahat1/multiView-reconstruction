from pathlib import Path
from metashape_convert import export_cams

if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    xml_path = root / "final_week/group23.xml"
    out_json = root / "final_week/g23_proj_output.json"
    export_cams(xml_path, out_json)
