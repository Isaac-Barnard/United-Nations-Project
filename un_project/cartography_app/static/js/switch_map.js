function switchMap(mapId, newUrl, buttonElement) {
    // Switch image
    const img = document.getElementById(`map-image-${mapId}`);
    img.src = newUrl;

    // Find the parent .variant-buttons container
    const group = buttonElement.closest(".variant-buttons");

    // Remove active from all buttons in this group
    const buttons = group.querySelectorAll(".map-filter-button");
    buttons.forEach(btn => btn.classList.remove("active"));

    // Add active to clicked button
    buttonElement.classList.add("active");
}