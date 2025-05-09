import * as THREE from 'three'
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

let scene, renderer, camera, model, playerDiv;

const light = new THREE.AmbientLight(0xFFFFFF);
const directionalLight = new THREE.DirectionalLight(0xffffff, 0.5);
directionalLight.position.set(5, 10, 7.5);

async function getPlayerSkin(playername) {
    const image_url = document.URL + '/api/user/' + playername + '/?format=json';
    const response = await fetch(image_url);
    const data = await response.json();

    return [`data:image/png;base64,${data.skin_image}`, data.is_slim];
}


export const init = () => {
    playerDiv = document.querySelector('.player');
    playerDiv.innerHTML = '';

    renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true});
    renderer.setSize(147, 198);
    playerDiv.appendChild(renderer.domElement);

    camera = new THREE.PerspectiveCamera(30, 147/198, 0.1, 100);
    camera.position.set(0, 0.8, 4);
    //camera.look

    scene = new THREE.Scene();
    scene.add(light);
    scene.add(directionalLight);

    animate();
}

export const skin = async (player) => {
    const [player_skin, is_slim] = await getPlayerSkin(player);
    const model_path = is_slim ? '/static/models/slim_with_overlay.glb' : '/static/models/regular_with_overlay.glb';

    if (model) {
        scene.remove(model);
    }

    const textureLoader = new THREE.TextureLoader();
    const texture = textureLoader.load(player_skin, (tex) => {
        tex.magFilter = THREE.NearestFilter;
        tex.minFilter = THREE.NearestFilter;
        tex.wrapS = THREE.ClampToEdgeWrapping;
        tex.wrapT = THREE.ClampToEdgeWrapping;

        tex.encoding = THREE.sRGBEncoding;
        tex.needsUpdate = true;
    });
    const loader = new GLTFLoader();

    loader.load(model_path, (gltf) => {
        model = gltf.scene;
        model.scale.set(0.05, 0.05, 0.05);

        
        model.traverse((child) => {
            if (child.isMesh && child.material) {
                if (!child.material.map) {
                    child.material.map = texture;
                }  else {
                    child.material.map.image = texture.image;
                    child.material.map.needsUpdate = true;
                }

                child.material.transparent = true;
                child.material.alphaTest = 0.5;
                child.material.needsUpdate = true;
            }
        });

        model.rotation.y = 0;
        scene.add(model)
    }, undefined, (err) => {
        console.error("GLTF loading error: ", err)
    });
}

function animate() {
    requestAnimationFrame(animate);
    if (model && model.rotation) {
        model.rotation.y += 0.0035;
    }
    renderer.render(scene, camera);
}
