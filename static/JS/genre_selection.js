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


function goToAgeRangePage(service) {
    console.log('Service: ', service)
    const selectedGenres = Array.from(document.querySelectorAll('.genre-button.selected'))
        .map(button => button.textContent.trim().replace(/\s+/g, ''));

    if (selectedGenres.length > 0) {
        // Construct the URL with service and genres as query parameters
        const genreParam = encodeURIComponent(selectedGenres.join(','));
        const url = `/Age_range.html?service=${encodeURIComponent(service)}&genres=${genreParam}`;
        console.log('Redirecting to: ', url);
        // Redirect to the Age_range.html page
        window.location.href = url;
    } else {
        alert('Please select at least one genre before proceeding.');
    }
}
