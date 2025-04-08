document.addEventListener("DOMContentLoaded", function () {
    // Effetto hover sul bottone
    let pulsante = document.querySelector(".btn");

    if (pulsante) {
        pulsante.addEventListener("mouseover", function () {
            this.style.backgroundColor = "#e6b56d";
            this.style.transform = "scale(1.05)";
            this.style.transition = "all 0.3s ease";
        });

        pulsante.addEventListener("mouseleave", function () {
            this.style.backgroundColor = "#cda45e";
            this.style.transform = "scale(1)";
            this.style.transition = "all 0.3s ease";
        });
    }

    // Aggiungere animazioni al carico della pagina
    const servizi = document.querySelectorAll('.servizio');

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
    animaServizi();

    // Gestione dei messaggi flash
    const messageContainer = document.getElementById("message-container");
    if (messageContainer) {
        const messages = messageContainer.querySelectorAll("p");
        messages.forEach(message => {
            const category = message.dataset.category;
            const text = message.innerHTML;

            Swal.fire({
                title: category === 'success' ? 'Successo!' : 'Attenzione!',
                html: text,
                icon: category === 'success' ? 'success' : 'error',
                confirmButtonText: 'OK',
                confirmButtonColor: '#3085d6',
                timer: 5000,
                timerProgressBar: true
            });
        });
    }

    // Seleziona il pulsante "Prenota Ora"
    const prenotaOraButton = document.getElementById("prenota-ora-btn");

    if (prenotaOraButton) {
        prenotaOraButton.addEventListener("click", function (event) {
            event.preventDefault(); // Previeni il comportamento predefinito del link
            console.log("Bottone 'Prenota Ora' cliccato");

            // Mostra il popup per selezionare l'operatore
            fetch('/api/operatori')
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`Errore HTTP: ${response.status}`);
                    }
                    return response.json();
                })
                .then(operatori => {
                    console.log("Operatori ricevuti:", operatori);

                    if (!operatori || operatori.length === 0) {
                        Swal.fire({
                            title: 'Nessun Operatore Disponibile',
                            text: 'Al momento non ci sono operatori disponibili.',
                            icon: 'info',
                            confirmButtonText: 'OK'
                        });
                        return;
                    }

                    let operatoriHtml = '<div style="display: flex; flex-direction: column; gap: 10px;">';
                    operatori.forEach(operatore => {
                        operatoriHtml += `<button class="swal2-confirm swal2-styled operatore-select-btn" data-operatore-id="${operatore.id}" style="margin: 5px 0;">${operatore.nome}</button>`;
                    });
                    operatoriHtml += '</div>';

                    Swal.fire({
                        title: 'Seleziona un Operatore',
                        html: operatoriHtml,
                        showConfirmButton: false,
                        showCancelButton: true,
                        cancelButtonText: 'Annulla',
                        didOpen: () => {
                            const popup = Swal.getPopup();
                            if (popup) {
                                const buttons = popup.querySelectorAll('.operatore-select-btn');
                                buttons.forEach(button => {
                                    button.addEventListener('click', () => {
                                        const operatoreId = button.getAttribute('data-operatore-id');
                                        console.log(`Operatore selezionato: ID ${operatoreId}`);
                                        window.location.href = `/prenotazioni?operatore_id=${operatoreId}`;
                                        Swal.close();
                                    });
                                });
                            } else {
                                console.error("Impossibile trovare il popup SweetAlert2.");
                            }
                        }
                    });

                })
                .catch(error => {
                    console.error("Errore nel recupero degli operatori:", error);
                    Swal.fire({
                        title: 'Errore',
                        text: 'Si è verificato un errore nel caricamento degli operatori. Riprova più tardi.',
                        icon: 'error',
                        confirmButtonText: 'OK'
                    });
                });
        });
    }

    // Gestisci altri pulsanti (ad esempio, "Gestione Prenotazioni")
    const gestionePrenotazioniButton = document.querySelector(".btn-gestione-prenotazioni");
    if (gestionePrenotazioniButton) {
        gestionePrenotazioniButton.addEventListener("click", function () {
            // Reindirizza direttamente alla pagina di gestione prenotazioni
            window.location.href = "/admin/prenotazioni";
        });
    }
});
