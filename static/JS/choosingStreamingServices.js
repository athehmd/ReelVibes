function handleServiceSelection(event) {

    return true;
}

function setupEventHandlers() {
    const buttons = document.querySelectorAll('.streaming-button');
    if (buttons.length === 0) {
        console.warn("No streaming buttons found.");
    }
    buttons.forEach(button => {
        button.addEventListener('click', handleServiceSelection);
    });
}

document.addEventListener('DOMContentLoaded', function () {
    setupEventHandlers();
});
