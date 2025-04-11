document.addEventListener('DOMContentLoaded', () => {
    const cards = document.querySelectorAll('.card');

    cards.forEach(card => {
        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left - rect.width / 2;
            const y = e.clientY - rect.top - rect.height / 2;

            const rotateX = (-y / 20).toFixed(2);
            const rotateY = (x / 20).toFixed(2);

            card.style.transform = `rotateY(${rotateY}deg) rotateX(${rotateX}deg)`;
            card.style.boxShadow = `${-x / 30}px ${y / 30}px 2rem rgba(0, 0, 0, 0.3)`;
        });

        card.addEventListener('mouseleave', () => {
            card.style.transition = 'transform 0.5s ease, box-shadow 0.5s ease';
            card.style.transform = 'rotateY(0deg) rotateX(0deg)';
            card.style.boxShadow = '0 0.5rem 1rem rgba(0, 0, 0, 0.15)';
        });
    });
});
