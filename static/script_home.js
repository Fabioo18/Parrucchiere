document.addEventListener("DOMContentLoaded", function() {
    // Effetto hover sul bottone
    let pulsante = document.querySelector(".btn");

    pulsante.addEventListener("mouseover", function() {
        this.style.backgroundColor = "#e6b56d";
        this.style.transform = "scale(1.05)";
        this.style.transition = "all 0.3s ease";
    });

    pulsante.addEventListener("mouseleave", function() {
        this.style.backgroundColor = "#cda45e";
        this.style.transform = "scale(1)";
        this.style.transition = "all 0.3s ease";
    });

    // Aggiungere animazioni al carico della pagina
    const servizi = document.querySelectorAll('.servizio');

    // Animazione per quando gli utenti scorrono la pagina
    const animaServizi = () => {
        const scrollY = window.scrollY;

        servizi.forEach(servizio => {
            const offset = servizio.getBoundingClientRect().top + window.scrollY;
            if (scrollY + window.innerHeight - 100 >= offset) {
                servizio.classList.add('visibile');
            }
        });
    };

    window.addEventListener('scroll', animaServizi);
    animaServizi(); // Chiamato una volta per vedere subito le animazioni al caricamento
});

document.addEventListener("DOMContentLoaded", () => {
    const popup = document.getElementById("popup");
    const closePopupButton = document.getElementById("close-popup");

    if (popup) {
        // Mostra il popup
        popup.classList.add("show");

        // Chiudi il popup quando si clicca sul pulsante "Chiudi"
        closePopupButton.addEventListener("click", () => {
            popup.classList.remove("show");
        });

        // Chiudi il popup automaticamente dopo 5 secondi
        setTimeout(() => {
            popup.classList.remove("show");
        }, 5000);
    }
});
