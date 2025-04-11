import { skin } from '/static/js/skin_viewer.js';
import { init } from '/static/js/skin_viewer.js';
import { render } from '/static/js/skin_viewer.js';
init();
render();

var url = document.URL + 'api/users/?format=json';
async function getPlayerList() {
    let response = await fetch(url);
    let data = await response.json();
    return data;
}

async function constructImage(playername) {
    var image_url = document.URL + 'api/user/' + playername + '/?format=json';
    let response = await fetch(image_url);
    let data = await response.json();
    let face = await data['face_image'];
    return `data:image/png;base64,${face}`;
}

var lastClicked = ""
function changePlayer(player) {
    if (lastClicked == player) {
        return;
    }

    document.querySelector('.playername').innerHTML = "";
    document.querySelector('.armor-slots').innerHTML = "";
    document.querySelector('.offhand-slot').innerHTML = "";
    document.querySelector('.inv-slots').innerHTML = "";
    document.querySelector('.hotbar-slots').innerHTML = "";
    document.querySelector('.echest-slots').innerHTML = "";
    document.querySelector('.player').innerHTML = "";
    init();

    inventory(player);
    skin(player);
    lastClicked = player;
}

const selectorDiv = document.querySelector('.selector');
let radio = "";

const players = await getPlayerList();
const usernames = players.map(item => item.username);

for(let i = 0; i < usernames.length; i++) {
    let face_image = await constructImage(usernames[i]);

    radio += "<label>\n";
    radio += "<input type=\"radio\" class=\"radio\" name=\"Player Face\" value=\"" + usernames[i] + "\">\n";
    radio += "<img src=\"" + face_image + "\" alt=\"Select Player " + usernames[i] + "\" width=\"32\" height=\"32\">\n";
    radio += "</label>\n";
}
selectorDiv.innerHTML = radio;
const el = document.getElementsByClassName("radio");
for (const element of el) {
    element.addEventListener('click', function() { changePlayer(element.value); });
}
