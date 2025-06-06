// Set map bounds using coordinates of the Minecraft world
const x_top_left = -1616; // x-coordinate of the top-left corner
const z_top_left = -416;  // z-coordinate of the top-left corner
const x_bottom_right = 895; // x-coordinate of the bottom-right corner
const z_bottom_right = 959; // z-coordinate of the bottom-right corner

// Initialize map using L.CRS.Simple to remove latitude/longitude constraints
const map = L.map('map', {
    center: [0, 0],
    zoom: 2,              // Set an initial zoom level
    minZoom: -4,           // Set a minimum zoom to allow zooming out further
    maxZoom: 5,           // Adjust max zoom if needed
    crs: L.CRS.Simple      // Use simple coordinate system
});

// Define the image bounds using top-left and bottom-right corners
const imageBounds = [
    [-z_top_left, x_top_left],      // Top-left corner: invert z-coordinate
    [-z_bottom_right, x_bottom_right]  // Bottom-right corner: invert z-coordinate
];

// Add the PNG as an image overlay layer
//L.imageOverlay('/static/images/maps/Official UN Map (10_21_24).png', imageBounds).addTo(map);
const imageOverlay = L.imageOverlay('/static/images/maps/map.png', imageBounds, {
    // This ensures the image uses its native resolution at max zoom
    maxNativeZoom: 10,
    // Disable image smoothing
    className: 'pixelated-image'
}).addTo(map);

const style = document.createElement('style');
style.textContent = `
    .pixelated-image {
        image-rendering: -moz-crisp-edges;
        image-rendering: -webkit-crisp-edges;
        image-rendering: pixelated;
        image-rendering: crisp-edges;
    }
`;
document.head.appendChild(style);

// Fit the map view to the image bounds
map.fitBounds(imageBounds);
map.setZoom(0);

L.Control.HomeButton = L.Control.extend({
    options: {
        position: 'topleft'
    },

    onAdd: function(map) {
        const container = L.DomUtil.create('div', 'home-button leaflet-bar');
        container.innerHTML = '🏠︎'; // House symbol
        container.title = 'Return to (0, 0)';

        container.onclick = function() {
            // Convert Minecraft coordinates (0,0) to map coordinates
            map.setView([-0, 0], 0); // Using initial zoom level of 2
        };

        return container;
    }
});

// Add the home button to the map
new L.Control.HomeButton().addTo(map);

// Add coordinate display functionality
map.on('mousemove', function(e) {
    // Convert the map coordinates back to Minecraft coordinates
    let z = -Math.round(e.latlng.lat); // Negative because we inverted the z-coordinate
    let x = Math.round(e.latlng.lng);
    
    // Update the coordinates display
    document.getElementById('coordinates').innerHTML = 
        `X: ${x} | Z: ${z}`;
});

// Define custom icons for different owners
const icons = {
    'NOI': L.icon({
        iconUrl: '/static/images/building_icons/noi_building_icon.png',  // Add custom icon images here
        iconSize: [30, 30],
        iconAnchor: [15, 30],
        popupAnchor: [0, -30],
    }),
    'EOMR': L.icon({
        iconUrl: '/static/images/building_icons/eomr_building_icon.png',
        iconSize: [30, 30],
        iconAnchor: [15, 30],
        popupAnchor: [0, -30],
    }),
    'IOK': L.icon({
        iconUrl: '/static/images/building_icons/iok_building_icon.png',
        iconSize: [30, 30],
        iconAnchor: [15, 30],
        popupAnchor: [0, -30],
    }),
    'NEL': L.icon({
        iconUrl: '/static/images/building_icons/nel_building_icon.png',
        iconSize: [30, 30],
        iconAnchor: [15, 30],
        popupAnchor: [0, -30],
    }),
    'QC': L.icon({
        iconUrl: '/static/images/building_icons/qc_building_icon.png',
        iconSize: [30, 30],
        iconAnchor: [15, 30],
        popupAnchor: [0, -30],
    }),
    'BEL': L.icon({
        iconUrl: '/static/images/building_icons/bel_building_icon.png',
        iconSize: [30, 30],
        iconAnchor: [15, 30],
        popupAnchor: [0, -30],
    }),
    'CDS': L.icon({
        iconUrl: '/static/images/building_icons/cds_building_icon.png',
        iconSize: [30, 30],
        iconAnchor: [15, 30],
        popupAnchor: [0, -30],
    }),
    'CRP': L.icon({
        iconUrl: '/static/images/building_icons/crp_building_icon.png',
        iconSize: [30, 30],
        iconAnchor: [15, 30],
        popupAnchor: [0, -30],
    }),
    'UN': L.icon({
        iconUrl: '/static/images/building_icons/un_building_icon.png',
        iconSize: [30, 30],
        iconAnchor: [15, 30],
        popupAnchor: [0, -30],
    }),
    '': L.icon({  // Add a default fallback icon
        iconUrl: '/static/images/building_icons/default_building_icon.png',
        iconSize: [30, 30],
        iconAnchor: [15, 30],
        popupAnchor: [0, -30],
})
    // Add more owners as needed
};

// Fetch building data and add markers
let url_split = document.URL.split('/'); // Get url as array
url_split.pop(); // Remove blank spaace
url_split.pop(); // Remove current page, we are left with parent page

let dir = url_split.join('/'); // restructure array as string
let url = dir + '/un_api/buildings/'; // adds parent dir to url
fetch(url)
    .then(response => response.json())
    .then(data => {
        data.forEach(building => {

            // Invert the z-coordinate for the y-axis value
            const x = parseFloat(building.x_coordinate);
            const y = parseFloat(building.z_coordinate) * -1;

            // Select icon based on the owner's abbreviation
            const icon = icons[building.owner_abbreviation] || icons['default'];

            // Add marker at the transformed coordinates
            const marker = L.marker([y, x], { icon: icon }).addTo(map);
            marker.bindPopup(`
                <strong style="font-size: 1.2em;">${building.name}</strong><br>
                <u>Owner:</u> ${building.owner}<br>
                <u>Builder:</u> ${building.builders}<br>
                <u>Territory:</u> ${building.territory}<br>
                <u>Height:</u> ${building.height}<br>
                <u>Price:</u> ${building.price}<br>
                <u>Coords:</u> ${building.x_coordinate}/~/${building.z_coordinate}<br>
            `);
        });
    });
