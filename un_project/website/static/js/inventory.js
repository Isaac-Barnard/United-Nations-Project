var playerJson = '';

const armorDiv = document.querySelector('.armor-slots');
const offhandDiv = document.querySelector('.offhand-slot');
const inventoryDiv = document.querySelector('.inv-slots');
const hotbarDiv = document.querySelector('.hotbar-slots');
const echestDiv = document.querySelector('.echest-slots');
const playerDiv = document.querySelector('.player');
const subDiv = document.querySelector('.shulker-slots');
var rarity = {};
var regex_rarity = [];
preload_rarity();
const rarity_color = {uncommon: "#FFFF55", rare: "#55FFFF", epic: "#FF55FF"};

var subData = [];

function createItem(slotData, i, shulkerId) {
    const itemDiv = document.createElement('div');
    itemDiv.className = 'item';
    const itemImage = document.createElement('img');

    if (slotData === undefined) {
        itemImage.src = `/static/images/minecraft_items/air.png`;
        itemDiv.appendChild(itemImage);
    } else {
        itemImage.src = `/static/images/minecraft_items/${slotData.item_id}.png`;
        itemImage.id = `${i}`;

        itemImage.setAttribute("data-title", `${slotData.name}`);
        if (slotData['custom_name'] !== "None") {
            let name = slotData['custom_name'];
            itemImage.setAttribute("data-title-c", `${name}`)
            itemImage.removeAttribute("data-title");
        }

        itemDiv.appendChild(itemImage);
        if (slotData['item_id'].includes("shulker_box")) {
            itemDiv.setAttribute("onmouseenter", "display_shulker(this);");
            itemDiv.setAttribute("onmouseleave", "remove_shulker(this);");
            itemDiv.setAttribute("id", shulkerId.value);
            shulkerId.value = shulkerId.value + 2;
        } else {
            itemDiv.setAttribute("onmouseenter", "display_tooltip(this);");
            itemDiv.setAttribute("onmouseleave", "remove_tooltip(this);");
        }

        if (slotData['item_id'].includes("bundle")) { shulkerId.value = shulkerId.value + 2; }

        if (slotData['amount'] > 1) {
            const quantityDiv = document.createElement('div');
            quantityDiv.className = 'quantity';
            quantityDiv.textContent = slotData['amount'];
            itemDiv.appendChild(quantityDiv);
        }
    }
    return itemDiv;
}

/* Inventory is seperated into two types, from player and from enderchest.
 * These are seperated by even (player) and odd (echest)
 * Every entry contains a single item and a few notable things about it:
 *  inventory_id        - Unique item-slot id
 *  inventory_type_id   - Described previously
 *  slot                - Location of the item in its respective inventory
 *  item_id             - Minecraft id for the item without minecraft: in it
 *                        (i.e. miencraft:compass -> compass) Used for image fetching
 *  amount              - Number of item held within slot
 *  name                - Proper name of the item
 *                        (cooked_beef -> steak)
 *  custom_name         - Custom name of the item, None if no custom name
 *  enchantments        - Enchantments on item, None if no enchantments
 *                        stored in dictionary as {'name': level} format
*/
async function getInventoryData(playername) {
    let url = document.URL + '/api/inventory/' + playername + '/?format=json';
    let response = await fetch(url);
    let data = await response.json();
    const refined_data = await data.map(item => {
        if (item.enchantments !== "None") {
            return {
                ...item,
                enchantments: JSON.parse(item.enchantments.replace(/'/g, '"'))
            };
        }
        return item
    });
    return await refined_data;
}


function shulkerInv(slot_list, inv_id) {
    var tempDiv = document.createElement('div');
    for (let i = 0; i < 27; i++) {
        const slot_data = slot_list.find(item=>item.slot === i);
        const item_div = createItem(slot_data, i);
        tempDiv.appendChild(item_div);
    }
    return tempDiv;
}

function echestInv(slot_list) {
    var shulkerId = {value: 3};
    for (let i = 0; i < 27; i++) {
        const slot_data = slot_list.find(item => item.slot === i);
        const item_div = createItem(slot_data, i, shulkerId);
        echestDiv.appendChild(item_div);
    }
}

function playerInv(slot_list) {
    var shulkerId = {value: 2};
    for (let i = 0; i < 36; i++) {
        const slot_data = slot_list.find(item => item.slot === i); // undefined or the item
        const item_div = createItem(slot_data, i, shulkerId);

        if (i < 9) {
            hotbarDiv.appendChild(item_div);
        } else {
            inventoryDiv.appendChild(item_div);
        }
    }

    for (let i = 100; i <= 103; i++) {
        const slot_data = slot_list.find(item => item.slot === i); // undefined or the item
        const item_div = createItem(slot_data, i);
        armorDiv.insertBefore(item_div, armorDiv.firstChild);
    }

    const slot_data = slot_list.find(item => item.slot === -106);
    const item_div = createItem(slot_data, -106);
    offhandDiv.appendChild(item_div);
}

function inventory(playername) {
    getInventoryData(playername)
        .then(jsonData => {
            playerJson = jsonData;

            const player_inv_slots = jsonData.filter(item => item.inventory_type_id === 0);
            playerInv(player_inv_slots);
            
            const echest_inv_slots = jsonData.filter(item => item.inventory_type_id === 1);
            echestInv(echest_inv_slots);
            
            var max_inv_id = 0;
            playerJson.forEach((item) => max_inv_id = item.inventory_type_id > max_inv_id ? item.inventory_type_id : max_inv_id);
            
            subData = [];
            for (let i = 2; i <= max_inv_id; i++)  {
                var sub_inv_slots = jsonData.filter(item => item.inventory_type_id === i);
                //if (sub_inv_slots.length === 0) { continue; }
                var innerDiv = shulkerInv(sub_inv_slots, i);
                subData.push({inv_id: i, div: innerDiv});
            }
        })
        .catch(error => console.error('Error fetching JSON data: ', error));
}

// On mouseover create tooltip which follows cursor, on mouseout remove the tooltip

// On click freeze tooltip in place? Check for mouseout on tooltip area afterwards so you can mouse over tooltip stuff?
// For shulkers display contents, on click freeze content window, allow mouseover of THOSE contents, which you can then do other stuff with.

function display_tooltip(element) {
    if (document.querySelector(".tooltip")) {
        return;
    }

    const label = document.createElement('label');
    label.className = "tooltip";

    let name = element.children[0].getAttribute('data-title');
    if (element.children[0].getAttribute('data-title-c') !== null) {
        name = element.children[0].getAttribute('data-title-c');
        label.innerHTML = "<p class=\"name\" style=\"font-style: italic;\">" + name + "</p>";
        label.style.color = rarity_color['rare'];
    } else {
        label.innerHTML = "<p class=\"name\">" + name + "</p>";
    }

    var srcArr = element.childNodes[0].src.split("/");
    var id_name = srcArr[srcArr.length - 1].split(".png")[0];
    
    var extra_color = "";

    regex_rarity.forEach((tuple) => {
        var match = id_name.match(tuple['regex']);
        if (match != null && match.length == 1) {
            extra_color = rarity_color[tuple['rarity']];
        }
    });

    if (Object.keys(rarity).includes(id_name)) {
        extra_color = rarity_color[rarity[id_name]];
    }

    label.style.color = extra_color;

    let id = element.children[0].getAttribute('id');

    var interface = element.offsetParent.offsetParent.className;

    if (interface === "inventory") { interface = 0; }
    else if (interface === "enderchest") { interface = 1; }
    else { interface = element.offsetParent.offsetParent.id; }

    var jsonData = playerJson;

    let slot = jsonData.filter(item => item.inventory_type_id == interface).find(item => item.slot === parseInt(id));
    if (slot === undefined) {
        console.error("Error fetching item slot " + id);
        return;
    }

    if (slot['enchantments'] !== "None") {
        if (id_name != 'enchanted_book') { label.style.color = rarity_color['rare']; }
        if (id_name == 'trident' || id_name == 'elytra') { label.style.color = rarity_color['epic']; }

        enchants = slot['enchantments']
        const keys = Object.keys(enchants);
        const values = Object.values(enchants);

        for (let i = 0; i < values.length; i++) {
            var currentEnchant = keys[i].charAt(0).toUpperCase() + keys[i].slice(1)
            currentEnchant = currentEnchant.split("_").join(" ")

            if (keys[i] == "mending" || keys[i] == "channeling" || keys[i] == "silk_touch" || keys[i] == "flame") {
                label.innerHTML += "<p class=\"enchants\" style=\"color: #A8A8A8;\">" + currentEnchant + "</p>";
                continue;
            }

            switch (values[i]) {
                case 1:
                    currentEnchant += " I";
                    break;
                case 2:
                    currentEnchant += " II";
                    break;
                case 3:
                    currentEnchant += " III";
                    break;
                case 4:
                    currentEnchant += " IV";
                    break;
                case 5:
                    currentEnchant += " V";
                    break;
                default:
                    currentEnchant += "";
            }
            label.innerHTML += "<p class=\"enchants\" style=\"color: #A8A8A8;\">" + currentEnchant + "</p>";
        }
    } else if (slot)

    element.addEventListener('mousemove', follow, false);
    element.addEventListener('click', toggle_freeze_tooltip);
    element.appendChild(label);
}

function remove_tooltip(element) {
    if (!document.querySelector(".tooltip")) {
        return;
    }
    if (document.querySelector(".tooltip").hasAttribute('frozen')) {
        return;
    }
    element.querySelector(".tooltip").remove();
}

function display_shulker(element) {
    if (document.querySelector(".tooltip")) {
        return;
    }
    display_tooltip(element);
    element.removeEventListener('click', toggle_freeze_tooltip);
    element.addEventListener('click', toggle_shulker_display);
}

function remove_shulker(element) {
    remove_tooltip(element);
}

function follow(e) {
    if (document.querySelector(".tooltip") == null || document.querySelector(".tooltip").hasAttribute('frozen')) {
        return;
    }
    if (e.target.className == "tooltip") {
        return;
    }

    let tooltip = document.querySelector(".tooltip");
    let element = e.target.getBoundingClientRect();
    if (e.target.className == "quantity") {
        element = e.target.offsetParent.getBoundingClientRect();
    }

    let top = element.y;
    let left = element.x;

    let x = e.pageX - left + 15;
    let y = e.pageY - top - tooltip.clientHeight;

    tooltip.style.left = x + 'px';
    tooltip.style.top = y + 'px';
}

function toggle_freeze_tooltip(e) {
    let tooltip = document.querySelector(".tooltip");

    if (tooltip.hasAttribute('frozen')) {
        tooltip.removeAttribute('frozen');
    } else {
        tooltip.setAttribute('frozen', 'frozen');
    }
}

function toggle_shulker_display(e) {
    let shulker = document.querySelector(".shulker");
    let shulker_name = document.querySelector('.shulker-name');

    if (shulker.style.visibility === 'visible' && shulker.getAttribute('id') == e.target.offsetParent.getAttribute('id')) {
        subDiv.innerHTML = '';
        shulker_name.style.fontStyle = '';
        shulker_name.innerHTML = '';
        shulker.removeAttribute('id');
        shulker.style.visibility = 'hidden';
        return;
    }
    shulker.style.visibility = 'visible';
    get_shulker_name(e.target, shulker_name);
    var inv_id = e.target.offsetParent.getAttribute('id');
    var inv_json = subData.filter(inventory => inventory.inv_id == inv_id)[0];
    subDiv.innerHTML = inv_json.div.innerHTML;
    shulker.setAttribute('id', inv_id);
    
}

function get_shulker_name(element, name_element) {
    if (element.hasAttribute('data-title-c')) {
        name_element.innerHTML = element.getAttribute('data-title-c');
        name_element.style.fontStyle = 'italic';
    } else if (element.hasAttribute('data-title')) {
        name_element.innerHTML = element.getAttribute('data-title');
        name_element.style.fontStyle = '';
    }
}

async function preload_rarity() {
    fetch('/static/js/rarity_list.txt')
    .then((response) => response.text())
    .then((text) => {
        text.split("\n").forEach((row) => {
            var rowData = row.split(", ");
            if (rowData[0].includes("*")) {
                var data = rowData[0].replace("*", "[A-Za-z0-9]+");
                regex_rarity.push({regex: data, rarity: rowData[1]});
            } else {
                rarity[rowData[0]] = rowData[1];
            }
        })
    })
}