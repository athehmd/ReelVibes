// Function to handle streaming service selection
function handleServiceSelection(event) {
    // Allow the form to submit normally
    // This will trigger the POST request with the button's value
    return true;
}

// Event Handlers for streaming service selection buttons
function setupEventHandlers() {
    const buttons = document.querySelectorAll('.streaming-button');
    if (buttons.length === 0) {
        console.warn("No streaming buttons found.");
    }
    buttons.forEach(button => {
        // Add click event listener that allows form submission
        button.addEventListener('click', handleServiceSelection);
    });
}

// Initialization of the page functionalities
document.addEventListener('DOMContentLoaded', function () {
    setupEventHandlers();
});