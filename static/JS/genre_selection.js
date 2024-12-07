// Function to navigate to the genre selection page
function goToGenrePage() {
    window.location.href = "/genre_selection";
}

// Event Handlers for streaming service selection buttons
function setupEventHandlers() {
    const buttons = document.querySelectorAll('.genre-button');
    if (buttons.length === 0) {
        console.warn("No genre buttons found.");
    }
    buttons.forEach(button => {
        button.onclick = goToGenrePage;
    });
}

// Toggle visibility of modal or other UI components
function toggleModal(modalId, show) {
    const modal = document.getElementById(modalId);
    if (!modal) {
        console.warn(`Modal with ID ${modalId} not found.`);
        return;
    }
    modal.style.display = show ? 'block' : 'none';
}

// Initialization of the page functionalities
document.addEventListener('DOMContentLoaded', function () {
    setupEventHandlers();
    // Additional initializations can be added here
});
