function getQueryParams() {
    const params = new URLSearchParams(window.location.search);
    const genres = params.get('genres'); // Fetch genres
    console.log('Selected genres:', genres.split(',')); // Debugging purposes
    return genres;
}

function navigateToYear(age) {
    window.location.href = `/year_of_release.html?age=${encodeURIComponent(age)}`;
}

// Use this function to process genres on page load
document.addEventListener('DOMContentLoaded', () => {
    const genres = getQueryParams();
    console.log('Genres passed to Age Range page:', genres);
    // You can now use these genres in your page logic
});

// Handle age range selection
document.querySelectorAll('.age-button').forEach(button => {
    button.addEventListener('click', () => {
        document.querySelectorAll('.age-button').forEach(btn => btn.classList.remove('selected'));
        button.classList.add('selected');
        const selectedAge = button.getAttribute('data-age');
        const genres = getQueryParams(); // Get genres from the URL

        // Redirect to the next page with age and genres
        window.location.href = `/year_of_release.html?age=${selectedAge}`;
    });
});



