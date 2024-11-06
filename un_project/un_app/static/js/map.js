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

// Fetch building data and add markers
fetch('/un_api/buildings/')
    .then(response => response.json())
    .then(data => {
        data.forEach(building => {

            // Invert the z-coordinate for the y-axis value
            const x = parseFloat(building.x_coordinate);
            const y = parseFloat(building.z_coordinate) * -1;

            // Add marker at the transformed coordinates
            const marker = L.marker([y, x]).addTo(map);
            marker.bindPopup(`
                <strong>${building.name}</strong><br>
                Owner: ${building.owner}<br>
                Height: ${building.height}<br>
                Price: ${building.price}<br>
            `);
        });
    });








