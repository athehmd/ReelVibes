document.addEventListener('DOMContentLoaded', () => {
    const rangeInput = document.getElementById('year-range');
    const yearDisplay = document.getElementById('selected-year');

    function updateSliderBackground() {
        const value = rangeInput.value;
        const min = rangeInput.min || 1950; // Minimum year
        const max = rangeInput.max || 2024; // Maximum year

        const percentage = ((value - min) / (max - min)) * 100;
        rangeInput.style.background = `linear-gradient(to right, #9c27b0 0%, #9c27b0 ${percentage}%, #d9d9d9 ${percentage}%, #d9d9d9 100%)`;
    }

    // Update the year display dynamically
    rangeInput.addEventListener('input', () => {
        yearDisplay.textContent = `${rangeInput.value}`; // Update correctly
        updateSliderBackground();
    });

    // Initialize on page load
    yearDisplay.textContent = `${rangeInput.value}`;
    updateSliderBackground();

    // Apply button functionality
    document.getElementById('apply-button').addEventListener('click', () => {
        const selectedYear = rangeInput.value; // Get the current slider value
        const ageRange = new URLSearchParams(window.location.search).get('age') || 'All';

        // Redirect with correct query parameters
        window.location.href = `/movie_selection.html?age=${encodeURIComponent(ageRange)}&start_year=${encodeURIComponent(selectedYear)}`;
    });
});
