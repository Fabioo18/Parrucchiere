document.querySelector('.hamburger').addEventListener('click', function (event) {
    const navMenu = document.querySelector('.header-nav ul');
    navMenu.classList.toggle('show');
    event.stopPropagation(); // Impedisce che il clic sull'hamburger chiuda immediatamente il menu
});

// Chiudi il menu quando si clicca su un link
document.querySelectorAll('.header-nav ul li a').forEach(link => {
    link.addEventListener('click', function () {
        const navMenu = document.querySelector('.header-nav ul');
        navMenu.classList.remove('show');
    });
});

// Chiudi il menu quando si clicca fuori
document.addEventListener('click', function (event) {
    const navMenu = document.querySelector('.header-nav ul');
    const hamburger = document.querySelector('.hamburger');
    if (!navMenu.contains(event.target) && !hamburger.contains(event.target)) {
        navMenu.classList.remove('show');
    }
});