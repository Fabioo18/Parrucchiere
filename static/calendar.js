document.addEventListener('DOMContentLoaded', function () {
    var calendarEl = document.getElementById('calendar');

    var calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        locale: 'it',
        themeSystem: 'bootstrap',
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay'
        },
        events: '/api/prenotazioni',  // Carica eventi dinamicamente dall'API Flask
        eventClick: function(info) {
            alert("Dettagli Prenotazione:\n\n" +
                  "Nome: " + info.event.title.split(" - ")[0] + "\n" +
                  "Servizio: " + info.event.title.split(" - ")[1] + "\n" +
                  "Data: " + info.event.start.toISOString().split("T")[0] + "\n" +
                  "Orario: " + info.event.start.toISOString().split("T")[1].substring(0, 5)
            );
        }
    });

    calendar.render();
});
