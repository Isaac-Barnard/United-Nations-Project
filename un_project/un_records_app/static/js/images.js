// Image modal functionality for records pages
function openModal(imageSrc, title) {
    const modal = document.getElementById('imageModal');
    const modalImg = document.getElementById('modalImage');
    
    modal.style.display = 'block';
    modalImg.src = imageSrc;
    modalImg.alt = 'Image for ' + title;
}

function closeModal() {
    document.getElementById('imageModal').style.display = 'none';
}

// Close modal when pressing Escape key
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        closeModal();
    }
});