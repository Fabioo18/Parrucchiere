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

function modificaPrenotazione() {
    var eventId = document.getElementById('deleteButton').getAttribute('data-id'); // Ottieni l'ID

    if (!eventId) {
        alert('Errore: ID non valido.');
        return;
    }

    fetch('/api/prenotazione/' + eventId)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert('Errore nel recupero della prenotazione: ' + data.error);
            } else {
                document.getElementById('editNome').value = data.nome;
                document.getElementById('editEmail').value = data.email;
                document.getElementById('editData').value = data.data;
                document.getElementById('editOrario').value = data.orario;

                // Seleziona i servizi
                let serviziSelezionati = data.servizio.split(", ");
                let opzioni = document.getElementById('editServizio').options;
                for (let i = 0; i < opzioni.length; i++) {
                    opzioni[i].selected = serviziSelezionati.includes(opzioni[i].value);
                }

                // Mostra la modale
                document.getElementById('editModal').style.display = 'block';
                document.getElementById('editForm').setAttribute('data-id', eventId);
            }
        })
        .catch(error => console.error('Errore nel recupero dei dettagli:', error));
}

function salvaModifiche() {
    var eventId = document.getElementById('editForm').getAttribute('data-id');

    var nome = document.getElementById('editNome').value;
    var email = document.getElementById('editEmail').value;
    var data = document.getElementById('editData').value;
    var orario = document.getElementById('editOrario').value;
    var servizi = Array.from(document.getElementById('editServizio').selectedOptions).map(option => option.value);

    fetch('/api/modifica_prenotazione/' + eventId, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ nome, email, data, orario, servizio: servizi.join(", ") })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Prenotazione modificata con successo!');
            closeEditModal();
            location.reload();
        } else {
            alert('Errore: ' + data.error); // Messaggio se l'orario è già occupato
        }
    })
    .catch(error => console.error('Errore nella modifica:', error));
}


function closeEditModal() {
    document.getElementById('editModal').style.display = 'none';
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
