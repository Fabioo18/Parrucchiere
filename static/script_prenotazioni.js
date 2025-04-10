document.addEventListener("DOMContentLoaded", function () {
    console.log("FullCalendar sta caricando...");

    var calendarEl = document.getElementById('calendar');
    var orarioSelect = document.getElementById('orario');
    var dataInput = document.getElementById('data');
    var modal = document.getElementById('booking-modal');  // Modale
    var closeModal = document.querySelector('.close');     // Pulsante di chiusura del modale

    // Recupera l'operatore_id dalla pagina
    var operatoreId = document.querySelector('input[name="operatore_id"]').value;

    // Se il calendario è stato trovato nella pagina
    if (calendarEl) {
        console.log("Trovato il div #calendar!");

        var calendar = new FullCalendar.Calendar(calendarEl, {
            initialView: 'dayGridMonth',
            locale: 'it',
            selectable: true,
            editable: false,
            events: `/api/cliente_prenotazioni/${operatoreId}`, // Carica solo le prenotazioni dell'operatore selezionato
            eventColor: "#FF0000",
            eventTextColor: "white",
            aspectRatio: window.innerWidth < 768 ? 1 : 1.35,

            headerToolbar: {
                left: 'prev,next today', // Pulsanti di navigazione a sinistra
                right: 'title',         // Titolo (mese e anno) al centro
                center: ''                // Nessun pulsante a destra
            },

            // Coloriamo i giorni non prenotabili (domenica e lunedì)
            dayCellClassNames: function(arg) {
                const oggi = new Date();
                oggi.setHours(0, 0, 0, 0);
                const dataCella = new Date(arg.date);
                if (
                    dataCella.getDay() === 0 || // Domenica
                    dataCella.getDay() === 1 || // Lunedì
                    dataCella < oggi            // Data passata
                ) {
                    return 'indisponibile';
                }
                return '';
            },

            // Quando clicchi su una data
            dateClick: function(info) {
                console.log("Hai cliccato su:", info.dateStr);

                const oggi = new Date();
                oggi.setHours(0, 0, 0, 0); // Azzeriamo ore/minuti
                const dataSelezionata = new Date(info.dateStr);

                // Blocco per date passate
                if (dataSelezionata < oggi) {
                    Swal.fire({
                        title: 'Errore',
                        text: "Non è possibile selezionare una data passata.",
                        icon: 'error',
                        confirmButtonText: 'OK'
                    });
                    return;
                }

                // Blocco per domenica o lunedì
                if (dataSelezionata.getDay() === 0 || dataSelezionata.getDay() === 1) {
                    Swal.fire({
                        title: 'Errore',
                        text: "Questo giorno non è disponibile per le prenotazioni.",
                        icon: 'error',
                        confirmButtonText: 'OK'
                    });
                    return;
                }

                // Recupera gli orari disponibili per la data selezionata e operatore
                fetch(`/api/orari_disponibili_operatore/${operatoreId}/${info.dateStr}`)
                .then(response => response.json())
                .then(orari => {
                    console.log("Orari disponibili:", orari);

                    if (orari.length === 0) {
                        Swal.fire({
                            title: 'Nessun orario disponibile',
                            text: "Non ci sono orari prenotabili disponibili per oggi.",
                            icon: 'info',
                            confirmButtonText: 'OK'
                        });
                    } else {
                        dataInput.value = info.dateStr;
                        modal.style.display = "block";

                        orarioSelect.innerHTML = "";
                        orari.forEach(orario => {
                            var option = document.createElement("option");
                            option.value = orario;
                            option.text = orario;
                            orarioSelect.appendChild(option);
                        });
                    }
                })
                .catch(error => {
                    console.error("Errore nel recupero degli orari:", error);
                    Swal.fire({
                        title: 'Errore',
                        text: "Si è verificato un errore nel recupero degli orari.",
                        icon: 'error',
                        confirmButtonText: 'OK'
                    });
                });

            }
        });

        calendar.render();
        console.log("Calendario renderizzato con successo!");
    } else {
        console.error("Errore: il div #calendar non esiste!");
    }

    // Gestione del modale: chiusura quando si clicca sulla 'X'
    closeModal.onclick = function() {
        modal.style.display = "none";
    }

    // Chiudere il modale cliccando fuori dalla finestra
    window.onclick = function(event) {
        if (event.target === modal) {
            modal.style.display = "none";
        }
    }

    // Validazione per i servizi selezionati (form)
    document.getElementById('booking-form').addEventListener('submit', function(event) {
        var selectedServices = document.querySelectorAll('input[name="servizi"]:checked');

        if (selectedServices.length === 0) {
            event.preventDefault();
            Swal.fire({
                title: 'Errore',
                text: "Per favore, seleziona almeno un servizio.",
                icon: 'error',
                confirmButtonText: 'OK'
            });
        } else {
            console.log(`Servizi selezionati: ${selectedServices.length}`);
        }
    });

    // Gestione dei messaggi flash
    const messageContainer = document.getElementById("message-container");
    if (messageContainer) {
        const messages = messageContainer.querySelectorAll("p");
        messages.forEach(message => {
            const category = message.dataset.category;
            const text = message.textContent;

            // Mostra il popup personalizzato con SweetAlert2
            Swal.fire({
                title: category === 'success' ? 'Successo!' : 'Attenzione!',
                text: text,
                icon: category === 'success' ? 'success' : 'error',
                confirmButtonText: 'OK',
                confirmButtonColor: '#3085d6',
                timer: 5000, // Chiude automaticamente dopo 5 secondi
                timerProgressBar: true
            });
        });
    }
});