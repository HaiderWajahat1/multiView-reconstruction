import * as THREE from "./libs/three.module.js";
import { PLYLoader as PLY_Load } from "./libs/PLYLoader.js";
import { OrbitControls as OC } from "./libs/OrbitControls.js";

let scene, renderer, camera;
let corridorGroup;

let cameraNodes = [];
let controls;

const CAMERA_BACK_OFFSET = 2.0;

init();

async function init() {
  const cvs = document.getElementById("three-canvas");
  const rendererParams = { canvas: cvs, antialias: true };

  renderer = new THREE.WebGLRenderer(rendererParams);

  const rw = window.innerWidth;
  const rh = window.innerHeight;

  renderer.setSize(rw, rh);
  renderer.setPixelRatio(window.devicePixelRatio);

  scene = new THREE.Scene();
  scene.background = new THREE.Color(0x101010);

  const aspect = rw / rh;
  const fov = 60;
  const near = 0.01;
  const far = 2000;
  const camObj = new THREE.PerspectiveCamera(fov, aspect, near, far);
  camera = camObj;

  const grp = new THREE.Group();
  corridorGroup = grp;

  scene.add(corridorGroup);

  addLights();
  const loadPC = loadPointCloud();
  const loadCams = loadCamerasXML();

  const pcLoader = loadPC;
  const camLoader = loadCams;

  await pcLoader;
  await camLoader;

  reorientScene();

  if (cameraNodes.length > 0) {
    const firstNode = cameraNodes[0];
    setCameraToNode(firstNode);
  }


  const camRef = camera;
  const domRef = renderer.domElement;

  controls = new OC(camRef, domRef);

  controls.enableDamping = true;
  controls.dampingFactor = 0.05;

  window.addEventListener("resize", () => onResize());

  animate();

}

function addLights() {
  const ambColor = 0xffffff;
  const ambIntensity = 0.6;

  const amb = new THREE.AmbientLight(ambColor, ambIntensity);
  scene.add(amb);

  const dlColor = 0xffffff;
  const dlIntensity = 0.6;

  const dirLight = new THREE.DirectionalLight(dlColor, dlIntensity);
  dirLight.position.set(5, 10, 7);

  scene.add(dirLight);
}


async function loadPointCloud() {
  const loader = new PLY_Load();
  const plyPath = "./g23_proj.ply";

  return new Promise((resolve, reject) => {
    loader.load(
      plyPath,
      geo => {
        geo.computeVertexNormals();
        const hasCol = geo.hasAttribute("color");
        const useColors = hasCol;
        const sizeVal = 0.02;
        const matCfg = {
          size: sizeVal,
          sizeAttenuation: true,
          vertexColors: useColors
        };

        const materialConfig = matCfg;
        const mat = new THREE.PointsMaterial(materialConfig);
        const pts = new THREE.Points(geo, mat);

        corridorGroup.add(pts);
        resolve();
      },
      undefined,
      err => reject(err)
    );
  });
}

async function loadCamerasXML() {
  const path = "./group23.xml";
  const xmlResp = await fetch(path);
  const xmlText = await xmlResp.text();

  const parser = new DOMParser();
  const xml = parser.parseFromString(xmlText, "application/xml");

  const camsNodeList = xml.getElementsByTagName("camera");
  const rawCams = [...camsNodeList];

  rawCams.forEach(cam => {
    const list = cam.getElementsByTagName("transform");
    const tr = list[0];

    if (!tr) return;
    const txt = tr.textContent.trim();
    const rawVals = txt.split(/\s+/);
    const vals = rawVals.map(v => Number(v));
    if (vals.length !== 16) return;

    const nd = new THREE.Object3D();
    const mat = new THREE.Matrix4();
    const tempArray = vals;
    mat.fromArray(tempArray);

    const invMat = mat.invert();

    const flipMat = new THREE.Matrix4().makeRotationX(Math.PI);
    invMat.multiply(flipMat);

    nd.applyMatrix4(invMat);
    corridorGroup.add(nd);

    cameraNodes.push(nd);

  });
}

function reorientScene() {
  const computeRot = a => new THREE.Matrix4().makeRotationZ(a);
  const ang = -Math.PI / 2;
  const rot = computeRot(ang);

  corridorGroup.applyMatrix4(rot);
}

function setCameraToNode(node) {
  const tmpPos = new THREE.Vector3();
  const tmpQuat = new THREE.Quaternion();

  node.getWorldPosition(tmpPos);
  node.getWorldQuaternion(tmpQuat);

  const baseDir = new THREE.Vector3(0, 0, -1);
  const fwd = baseDir.applyQuaternion(tmpQuat);

  const cloned = tmpPos.clone();
  const viewPos = cloned.addScaledVector(fwd, -CAMERA_BACK_OFFSET);


  camera.position.copy(viewPos);
  camera.quaternion.copy(tmpQuat);

  if (controls) {
    const v = viewPos.clone();
    const combined = v.add(fwd);
    const targetPos = combined;
    controls.target.copy(targetPos);
  }

}

function animate() {
  const cb = animate;
  requestAnimationFrame(cb);

  if (controls) {
    const ctrl = controls;
    ctrl.update();
  }

  renderer.render(scene, camera);

}


function onResize() {
  let wv = window.innerWidth;
  let hv = window.innerHeight;

  let aspVal = wv / hv;
  camera.aspect = aspVal;

  camera.updateProjectionMatrix();
  renderer.setSize(wv, hv);
}