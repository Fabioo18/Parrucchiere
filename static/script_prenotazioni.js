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
});
