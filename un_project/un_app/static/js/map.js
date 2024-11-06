// Initialize map using L.CRS.Simple to remove latitude/longitude constraints
const map = L.map('map', {
    center: [0, 0],
    zoom: 2,              // Set an initial zoom level
    minZoom: -2,           // Set a minimum zoom to allow zooming out further
    maxZoom: 10,           // Adjust max zoom if needed
    crs: L.CRS.Simple      // Use simple coordinate system
});

// Add map tiles (adjust the URL pattern if needed based on your tile structure)
L.tileLayer('/static/map_tiles/{z}/{x}/{y}.png', {
    maxZoom: 10,
    minZoom: -2,
    tileSize: 256,
    noWrap: true,
}).addTo(map);

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
    'default': L.icon({  // Add a default fallback icon
        iconUrl: '/static/images/building_icons/default_building_icon.png',
        iconSize: [30, 30],
        iconAnchor: [15, 30],
        popupAnchor: [0, -30],
})
    // Add more owners as needed
};

// Fetch building data and add markers
fetch('/un_api/buildings/')
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
                <strong>${building.name}</strong><br>
                Owner: ${building.owner}<br>
                Builder: ${building.builders}<br>
                Height: ${building.height}<br>
                Price: ${building.price}<br>
                Coords: ${building.x_coordinate}/~/${building.z_coordinate}<br>
            `);
        });
    });








