const wrapper = document.querySelector('.wrapper');
const loginLink = document.querySelector('.login-link');
const registerLink = document.querySelector('.register-link');

// Login-Register Form
registerLink.addEventListener('click', ()=> {wrapper.classList.add('active')});
loginLink.addEventListener('click', ()=> {wrapper.classList.remove('active')});

// Forgot-Reset Form

