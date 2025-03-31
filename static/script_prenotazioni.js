document.addEventListener("DOMContentLoaded", function () {
    console.log("FullCalendar sta caricando...");

    var calendarEl = document.getElementById('calendar');
    var orarioSelect = document.getElementById('orario');
    
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

            // Quando clicchi su una data, aggiorna il campo data e mostra gli orari disponibili
            dateClick: function(info) {
                console.log("Hai cliccato su:", info.dateStr);
                document.getElementById('data').value = info.dateStr;

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

    // Aggiunta della validazione per i checkbox dei servizi
    document.getElementById('booking-form').addEventListener('submit', function(event) {
        var selectedServices = document.querySelectorAll('input[name="servizi"]:checked');
        if (selectedServices.length === 0) {
            event.preventDefault();
            alert("Per favore, seleziona almeno un servizio.");
        }
    });
});
