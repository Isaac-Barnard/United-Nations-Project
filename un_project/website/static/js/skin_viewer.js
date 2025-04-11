import * as THREE from 'three'
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

async function getPlayerSkin(playername) {
    var image_url = document.URL + '/api/user/' + playername + '/?format=json';

    let response = await fetch(image_url);
    let data = await response.json();

    let face = await data['skin_image'];
    let is_slim = await data['is_slim'];

    return [`data:image/png;base64,${face}`, is_slim];
}

const renderer = new THREE.WebGLRenderer();
renderer.setSize( 147, 198 );
const playerDiv = document.querySelector('.player');

const camera = new THREE.PerspectiveCamera( 40, 147 / 198, 1, 1000 );
camera.position.z = 0;
camera.zoom = 0.01;
camera.updateProjectionMatrix();

const light = new THREE.AmbientLight( 0xFFFFFF );

var model = { 'rotation': { 'y': 0 } };

var scene = "";



export const init = () => {
    playerDiv.appendChild( renderer.domElement );

    scene = new THREE.Scene();
    scene.add( light );
}

export const skin = async (player) => {
    let player_data = await getPlayerSkin(player);
    let player_skin = player_data[0]
    let is_slim = player_data[1];

    var model_path = '/static/models/regular_overlay.glb';
    if (is_slim === true) {
        model_path = '/static/models/slim_overlay.glb';
    }

    const textureLoader = new THREE.TextureLoader();
    const texture = textureLoader.load( player_skin );

    //texture.magFilter = THREE.NearestFilter;
    //texture.mainFilter = THREE.LinearMipMapLinearFilter;

    const loader = new GLTFLoader();

    loader.load( model_path, function ( gltf ) {
        model = gltf.scene;

        model.traverse( function ( o ) {
            if (o.material !== undefined) {
                o.material.map = texture;
            }
        } );

        scene.add( model );
        }, function ( xhr ) {
            console.log( ( xhr.loaded / xhr.total * 100 ) + '% loaded' );
        }, function ( error ) {
            console.error( "An error happened: " + error );
    } );
}

function animate() {
    requestAnimationFrame( render );
    model.rotation.y += 0.0035;
}

export const render = () => {
    animate();
    renderer.render( scene, camera );
}
