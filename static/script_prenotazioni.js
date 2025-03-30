document.addEventListener("DOMContentLoaded", function () {
    console.log("FullCalendar sta caricando...");

    var calendarEl = document.getElementById('calendar');
    if (calendarEl) {
        console.log("Trovato il div #calendar!");

        var calendar = new FullCalendar.Calendar(calendarEl, {
            initialView: 'dayGridMonth',
            locale: 'it',
            selectable: true, // Permette la selezione di una data
            editable: false,
            events: '/api/cliente_prenotazioni',
            eventColor: "#FF0000",
            eventTextColor: "white",

            // Quando clicchi su una data, aggiorna il campo data del form
            dateClick: function(info) {
                console.log("Hai cliccato su:", info.dateStr);
                document.getElementById('data').value = info.dateStr;
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
            event.preventDefault(); // Blocca l'invio del modulo
            alert("Per favore, seleziona almeno un servizio.");
        }
    });
});
