// Select all profile options
const profileLinks = document.querySelectorAll(".profile-options a");

// Select all content sections
const contentSections = document.querySelectorAll(".content-section");

// Add click event listeners to profile links
profileLinks.forEach((link) => {
    link.addEventListener("click", (e) => {
        e.preventDefault(); // Prevent default link behavior

        // Remove 'active' class from all links and content sections
        profileLinks.forEach((l) => l.classList.remove("active"));
        contentSections.forEach((section) => section.classList.remove("active"));

        // Add 'active' class to the clicked link and corresponding section
        link.classList.add("active");
        const targetId = link.getAttribute("data-target");
        document.getElementById(targetId).classList.add("active");
    });
});
