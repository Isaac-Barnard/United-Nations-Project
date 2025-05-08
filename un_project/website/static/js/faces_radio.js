import { skin, init } from '/static/js/skin_viewer.js';

init();

async function getPlayerList() {
    const response = await fetch(document.URL + '/api/users/?format=json')
    return await response.json();
}


async function constructImage(playername) {
    const response = await fetch(document.URL + '/api/user/' + playername + '/?format=json');
    const data = await response.json();
    return `data:image/png;base64,${data.face_image}`;
}

let lastClicked = ""
function changePlayer(player) {
    if (lastClicked == player) return;

    document.querySelector('.playername').innerHTML = "";
    document.querySelector('.armor-slots').innerHTML = "";
    document.querySelector('.offhand-slot').innerHTML = "";
    document.querySelector('.inv-slots').innerHTML = "";
    document.querySelector('.hotbar-slots').innerHTML = "";
    document.querySelector('.echest-slots').innerHTML = "";

    inventory(player);
    skin(player);
    lastClicked = player;
}

const selectorDiv = document.querySelector('.selector');
const players = await getPlayerList();
let radioHTML = "";

for (const player of players) {
    const face_image = await constructImage(player.username);
    radioHTML += `
        <label>
            <input type="radio" class="radio" name="Player Face" value="${player.username}">
            <img src="${face_image}" alt="Select Player ${player.username}" width="32" height = "32">
        </label>`;
}

selectorDiv.innerHTML = radioHTML;

document.querySelectorAll(".radio").forEach(el => {
    el.addEventListener('click', () => changePlayer(el.value));
});
