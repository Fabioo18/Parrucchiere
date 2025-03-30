document.addEventListener('DOMContentLoaded', function () {
    var calendarEl = document.getElementById('calendar');
    var calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        locale: 'it',
        selectable: true,
        editable: false,
        events: '/api/prenotazioni',
        eventClick: function(info) {
            var eventId = info.event.id;
            showEventDetail(eventId);
        }
    });
    calendar.render();
});

function showEventDetail(eventId) {
    fetch('/api/prenotazione/' + eventId)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert('Errore nel recupero della prenotazione: ' + data.error);
            } else {
                var detailContent = `
                    <h3>Dettagli Prenotazione</h3>
                    <p><strong>Nome:</strong> ${data.nome}</p>
                    <p><strong>Email:</strong> ${data.email}</p>
                    <p><strong>Servizio:</strong> ${data.servizio}</p>
                    <p><strong>Data:</strong> ${data.data}</p>
                    <p><strong>Orario:</strong> ${data.orario}</p>
                `;
                document.getElementById('detailContent').innerHTML = detailContent;
                document.getElementById('deleteButton').setAttribute('data-id', eventId);  // Memorizza l'ID della prenotazione nel pulsante
                document.getElementById('detailModal').style.display = 'block';
            }
        })
        .catch(error => {
            console.error('Errore nel recupero dei dettagli:', error);
        });
}

function eliminaPrenotazione() {
    var eventId = document.getElementById('deleteButton').getAttribute('data-id'); // Ottieni l'ID dal pulsante

    if (!eventId) {
        alert('Errore: ID non valido.');
        return;
    }

    fetch('/api/elimina_prenotazione/' + eventId, {
        method: 'DELETE',
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Prenotazione eliminata con successo!');
            closeModal(); // Chiudi la modale
            location.reload(); // Ricarica la pagina per aggiornare il calendario
        } else {
            alert('Errore nella cancellazione della prenotazione: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Errore durante l\'eliminazione:', error);
    });
}

function closeModal() {
    document.getElementById('detailModal').style.display = 'none';
}
