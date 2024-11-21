function toggleSelection(button) {
    button.classList.toggle('selected'); // Toggle the 'selected' class
    updateDoneButtonState(); // Update 'Done' button state
}


function selectAllGenres() {
    const buttons = document.querySelectorAll('.genre-button');
    buttons.forEach(button => button.classList.add('selected')); // Add the 'selected' class
    updateDoneButtonState();
}

function updateDoneButtonState() {
    const buttons = document.querySelectorAll('.genre-button.selected');
    document.getElementById('done-button').disabled = buttons.length === 0; // Enable 'Done' button if any are selected
}

function goToAgeRangePage() {
    const selectedGenres = Array.from(document.querySelectorAll('.genre-button.selected'))
        .map(button => button.textContent.trim()); // Get selected genres

    if (selectedGenres.length > 0) {
        // Redirect to the Age_range.html page
        window.location.href = `/Age_range.html`;
    } else {
        // Simple alert if no genres are selected
        alert('Please select at least one genre before proceeding.');
    }
}