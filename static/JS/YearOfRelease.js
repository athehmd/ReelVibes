document.addEventListener('DOMContentLoaded', () => {
    const rangeInput = document.getElementById('year-range');
    const yearDisplay = document.getElementById('selected-year');
    const form = document.querySelector('form');
    const applyButton = document.getElementById('apply-button');

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

    applyButton.addEventListener('click', (event) => {
        // Prevent form submission until we set the hidden input value
        event.preventDefault();

        const selectedYear = rangeInput.value;
        console.log(`Selected year: ${selectedYear}`); // For debugging

        // Set the hidden input value
        document.getElementById('start_year').value = selectedYear;

        // Manually submit the form after setting the hidden input value
        form.submit();
    });
    
});
