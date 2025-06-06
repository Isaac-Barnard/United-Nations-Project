import { skin, init } from '/static/js/skin_viewer.js';
init();

const locationP = document.querySelector('.playername');
async function getPlayerList() {
    const response = await fetch(document.URL + '/api/users/?format=json')
    return await response.json();
}


async function constructImage(playername) {
    const response = await fetch(document.URL + '/api/user/' + playername + '/?format=json');
    const data = await response.json();
    return `data:image/png;base64,${data.face_image}`;
}

function formatDimension(dim) {
    switch (dim) {
        case 'minecraft:overworld': return 'Overworld';
        case 'minecraft:the_nether': return 'Nether';
        case 'minecraft:the_end': return 'End';
        default:
            if (dim && dim.startsWith('minecraft:')) return dim.split(':')[1].replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
            return dim || 'Unknown';
    }
}

function setUserStats(playerData) {
    const locationP = document.querySelector('.location');
    const lastDeathP = document.querySelector('.lastdeath');
    const healthDiv = document.querySelector('.health');
    const xpDiv = document.querySelector('.xp');

    const {
        x, y, z, dimension,
        lastdeathx, lastdeathy, lastdeathz, lastdeathdim,
        health, xplevel, xppercent
    } = playerData;

    if (x !== null && y !== null && z !== null) {
        var dim = formatDimension(dimension);
        locationP.innerHTML = `Location:<br/> ${dim} | ${x}, ${y}, ${z}`;
    } else {
        locationP.innerHTML = `Location - Unknown`;
    }

    if (lastdeathx !== null && lastdeathy !== null && lastdeathz !== null) {
        const deathDimName = formatDimension(lastdeathdim);
        lastDeathP.innerHTML = `Last Death:<br/> ${deathDimName} | ${lastdeathx}, ${lastdeathy}, ${lastdeathz}`;
    } else {
        lastDeathP.innerHTML = `Last Death - Unknown`;
    }

    /*
    const fillImg = document.getElementById('hearts-fill');
    if (health !== null && fillImg) {
        const percent = Math.max(0, Math.min(health / 20, 1));
        const clipPercent = 100 - (percent * 100);

        fillImg.style.clipPath = `inset(0 ${clipPercent}% 0 0)`;
    } else {
        fillImg.style.clipPath = `inset(0 100% 0 0)`;
    }*/
}


let lastClicked = ""
async function changePlayer(player) {
    if (lastClicked == player) return;

    document.querySelector('.playername').innerHTML = "";
    document.querySelector('.armor-slots').innerHTML = "";
    document.querySelector('.offhand-slot').innerHTML = "";
    document.querySelector('.inv-slots').innerHTML = "";
    document.querySelector('.hotbar-slots').innerHTML = "";
    document.querySelector('.echest-slots').innerHTML = "";

    document.querySelector('.playername').innerHTML = player;
    const playerResponse = await fetch(`/minecraft/player/api/user/${player}/?format=json`);
    const playerData = await playerResponse.json();
    setUserStats(playerData);

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
