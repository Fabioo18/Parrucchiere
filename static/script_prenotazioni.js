document.addEventListener("DOMContentLoaded", function () {
    console.log("FullCalendar sta caricando...");

    var calendarEl = document.getElementById('calendar');
    var orarioSelect = document.getElementById('orario');
    var dataInput = document.getElementById('data');

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

                // Se il giorno è indisponibile, blocca la selezione
                if (info.date.getDay() === 0 || info.date.getDay() === 1) {
                    alert("Questo giorno non è disponibile per le prenotazioni.");
                    return;
                }

                dataInput.value = info.dateStr;

                // Recupera gli orari disponibili per la data selezionata
                fetch(`/api/orari_disponibili/${info.dateStr}`)
                    .then(response => response.json())
                    .then(orari => {
                        console.log("Orari disponibili:", orari);

                        // Pulisce la select degli orari
                        orarioSelect.innerHTML = "";

                        if (orari.length === 0) {
                            var option = document.createElement("option");
                            option.text = "Nessun orario disponibile";
                            orarioSelect.appendChild(option);

                            // Colora il giorno in rosso se non ci sono orari disponibili
                            let cella = document.querySelector(`[data-date='${info.dateStr}']`);
                            if (cella) cella.classList.add('indisponibile');

                            // Disabilita il campo data
                            dataInput.value = "";
                            alert("Questo giorno non ha orari disponibili. Scegli un altro giorno.");
                        } else {
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

    // Validazione per i servizi selezionati
    document.getElementById('booking-form').addEventListener('submit', function(event) {
        var selectedServices = document.querySelectorAll('input[name="servizi"]:checked');
        if (selectedServices.length === 0) {
            event.preventDefault();
            alert("Per favore, seleziona almeno un servizio.");
        }
    });
});
