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

    // Gestione dei messaggi flash
    const messageContainer = document.getElementById("message-container");
if (messageContainer) {
    const messages = messageContainer.querySelectorAll("p");
    messages.forEach(message => {
        const category = message.dataset.category;
        const text = message.innerHTML; // Usa innerHTML per mantenere i tag HTML

        // Mostra il popup personalizzato con SweetAlert2
        Swal.fire({
            title: category === 'success' ? 'Successo!' : 'Attenzione!',
            html: text, // Usa html invece di text per supportare i tag HTML
            icon: category === 'success' ? 'success' : 'error',
            confirmButtonText: 'OK',
            confirmButtonColor: '#3085d6',
            timer: 5000, // Chiude automaticamente dopo 5 secondi
            timerProgressBar: true
        });
    });
}
});

// document.addEventListener("DOMContentLoaded", () => {
//     const popup = document.getElementById("popup");
//     const closePopupButton = document.getElementById("close-popup");

//     if (popup) {
//         // Mostra il popup
//         popup.classList.add("show");

//         // Chiudi il popup quando si clicca sul pulsante "Chiudi"
//         closePopupButton.addEventListener("click", () => {
//             popup.classList.remove("show");
//         });

//         // Chiudi il popup automaticamente dopo 5 secondi
//         setTimeout(() => {
//             popup.classList.remove("show");
//         }, 5000);
//     }
// });
