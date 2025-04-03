document.addEventListener("DOMContentLoaded", function () {
    console.log("FullCalendar sta caricando...");

    var calendarEl = document.getElementById('calendar');
    var orarioSelect = document.getElementById('orario');
    var dataInput = document.getElementById('data');
    var modal = document.getElementById('booking-modal');  // Modale
    var closeModal = document.querySelector('.close');     // Pulsante di chiusura del modale

    // Se il calendario è stato trovato nella pagina
    if (calendarEl) {
        console.log("Trovato il div #calendar!");

        var calendar = new FullCalendar.Calendar(calendarEl, {
            initialView: 'dayGridMonth',
            locale: 'it',
            selectable: true,
            editable: false,
            events: '/api/cliente_prenotazioni',
            eventColor: "#FF0000",
            eventTextColor: "white",

            // Coloriamo i giorni non prenotabili (domenica e lunedì)
            dayCellClassNames: function(arg) {
                if (arg.date.getDay() === 0 || arg.date.getDay() === 1) { // Domenica = 0, Lunedì = 1
                    return 'indisponibile';
                }
                return '';
            },

            // Quando clicchi su una data
            dateClick: function(info) {
                console.log("Hai cliccato su:", info.dateStr);

                // Verifica se il giorno è domenica o lunedì e impedisci il click
                if (info.date.getDay() === 0 || info.date.getDay() === 1) {
                    alert("Questo giorno non è disponibile per le prenotazioni.");
                    return;  // Impedisce l'apertura del modale
                }

                // Recupera gli orari disponibili per la data selezionata
                fetch(`/api/orari_disponibili/${info.dateStr}`)
                    .then(response => response.json())
                    .then(orari => {
                        console.log("Orari disponibili:", orari);

                        // Se non ci sono orari disponibili per quella data, metti il giorno in rosso e impedisci il click
                        if (orari.length === 0) {
                            let cella = document.querySelector(`[data-date='${info.dateStr}']`);
                            if (cella) {
                                cella.classList.add('indisponibile');
                                cella.style.pointerEvents = 'none'; // Impedisce il click
                            }
                            alert("Questo giorno non ha orari disponibili. Scegli un altro giorno.");
                        } else {
                            // Rimuovi il rosso se ci sono orari disponibili
                            let cella = document.querySelector(`[data-date='${info.dateStr}']`);
                            if (cella) {
                                cella.classList.remove('indisponibile');
                                cella.style.pointerEvents = 'auto'; // Rende di nuovo cliccabile
                            }

                            dataInput.value = info.dateStr;
                            modal.style.display = "block";  // Mostra il modale

                            // Pulisce la select degli orari
                            orarioSelect.innerHTML = "";
                            orari.forEach(orario => {
                                var option = document.createElement("option");
                                option.value = orario;
                                option.text = orario;
                                orarioSelect.appendChild(option);
                            });
                        }
                    })
                    .catch(error => console.error("Errore nel recupero degli orari:", error));
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
        
        // Verifica se sono stati selezionati dei servizi
        if (selectedServices.length === 0) {
            event.preventDefault();
            alert("Per favore, seleziona almeno un servizio.");
        } else {
            console.log(`Servizi selezionati: ${selectedServices.length}`);
        }
    });
});
