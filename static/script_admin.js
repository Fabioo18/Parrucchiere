document.addEventListener('DOMContentLoaded', function () {
    var calendarEl = document.getElementById('calendar');
    var calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        locale: 'it',
        selectable: true,
        editable: false,
        events: '/api/prenotazioni',
        contentHeight: 'auto', // Adatta l'altezza del contenuto
        aspectRatio: window.innerWidth < 768 ? 2.5 : 1.35,

        headerToolbar: {
            left: 'prev,next today', // Pulsanti di navigazione a sinistra
            right: 'title',         // Titolo (mese e anno) al centro
            center: ''                // Nessun pulsante a destra
        },

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
                Swal.fire({
                    title: 'Errore',
                    text: 'Errore nel recupero della prenotazione: ' + data.error,
                    icon: 'error',
                    confirmButtonText: 'OK'
                });
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
            Swal.fire({
                title: 'Errore',
                text: 'Errore nel recupero dei dettagli: ' + error,
                icon: 'error',
                confirmButtonText: 'OK'
            });
        });
}

function modificaPrenotazione() {
    var eventId = document.getElementById('deleteButton').getAttribute('data-id'); // Ottieni l'ID

    if (!eventId) {
        Swal.fire({
            title: 'Errore',
            text: 'Errore: ID non valido.',
            icon: 'error',
            confirmButtonText: 'OK'
        });
        return;
    }

    fetch('/api/prenotazione/' + eventId)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                Swal.fire({
                    title: 'Errore',
                    text: 'Errore nel recupero della prenotazione: ' + data.error,
                    icon: 'error',
                    confirmButtonText: 'OK'
                });
            } else {
                document.getElementById('editNome').value = data.nome;
                document.getElementById('editEmail').value = data.email;
                document.getElementById('editData').value = data.data;
                document.getElementById('editOrario').value = data.orario;

                // Seleziona i servizi
                let serviziSelezionati = data.servizio.split(", ");
                document.getElementById('editServizioTaglio').checked = serviziSelezionati.includes('Taglio');
                document.getElementById('editServizioPiega').checked = serviziSelezionati.includes('Piega');
                document.getElementById('editServizioColore').checked = serviziSelezionati.includes('Colore');
                document.getElementById('editServizioTrattamento').checked = serviziSelezionati.includes('Trattamento');
                document.getElementById('editServizioShampoo').checked = serviziSelezionati.includes('Shampoo');

                // Mostra o nascondi il campo "Operatore" in base al ruolo
                if (data.operatore_id && document.getElementById('editOperatore')) {
                    document.getElementById('editOperatore').value = data.operatore_id;
                    document.querySelector('.form-group select[name="operatore"]').style.display = currentUserRole === 'parrucchiere' ? 'block' : 'none';
                }

                // Mostra la modale
                document.getElementById('editModal').style.display = 'block';
                document.getElementById('editForm').setAttribute('data-id', eventId);
            }
        })
        .catch(error => Swal.fire({
            title: 'Errore',
            text: 'Errore nel recupero dei dettagli: ' + error,
            icon: 'error',
            confirmButtonText: 'OK'
        }));
}

function salvaModifiche() {
    var eventId = document.getElementById('editForm').getAttribute('data-id');

    var nome = document.getElementById('editNome').value.trim();
    var email = document.getElementById('editEmail').value.trim();
    var data = document.getElementById('editData').value.trim();
    var orario = document.getElementById('editOrario').value.trim();
    var operatoreId = document.getElementById('editOperatore') ? document.getElementById('editOperatore').value : null;

    // Verifica che i campi obbligatori siano compilati
    if (!nome || !email || !data || !orario) {
        Swal.fire({
            title: 'Errore',
            text: 'Tutti i campi obbligatori devono essere compilati.',
            icon: 'error',
            confirmButtonText: 'OK'
        });
        return;
    }

    // Raccogli i servizi selezionati
    var servizi = [];
    if (document.getElementById('editServizioTaglio').checked) servizi.push("Taglio");
    if (document.getElementById('editServizioPiega').checked) servizi.push("Piega");
    if (document.getElementById('editServizioColore').checked) servizi.push("Colore");
    if (document.getElementById('editServizioTrattamento').checked) servizi.push("Trattamento");
    if (document.getElementById('editServizioShampoo').checked) servizi.push("Shampoo");

    // Mostra il loader
    showLoader();

    // Prepara i dati per la richiesta
    var body = { nome, email, data, orario, servizio: servizi.join(", ") };
    if (currentUserRole === 'parrucchiere') {
        body.operatore_id = operatoreId;
    }

    // Effettua la richiesta al server
    fetch('/api/modifica_prenotazione/' + eventId, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
    })
    .then(response => response.json())
    .then(data => {
        hideLoader();
        if (data.success) {
            Swal.fire({
                title: 'Successo',
                text: 'Prenotazione modificata con successo!',
                icon: 'success',
                confirmButtonText: 'OK'
            }).then(() => {
                closeEditModal();
                location.reload();
            });
        } else {
            Swal.fire({
                title: 'Errore',
                text: 'Errore: ' + data.error,
                icon: 'error',
                confirmButtonText: 'OK'
            });
        }
    })
    .catch(error => {
        hideLoader();
        Swal.fire({
            title: 'Errore',
            text: 'Errore nella modifica: ' + error,
            icon: 'error',
            confirmButtonText: 'OK'
        });
    });
}

function closeEditModal() {
    document.getElementById('editModal').style.display = 'none';
}

function eliminaPrenotazione() {
    var eventId = document.getElementById('deleteButton').getAttribute('data-id'); // Ottieni l'ID dal pulsante

    if (!eventId) {
        Swal.fire({
            title: 'Errore',
            text: 'Errore: ID non valido.',
            icon: 'error',
            confirmButtonText: 'OK'
        });
        return;
    }

    fetch('/api/elimina_prenotazione/' + eventId, {
        method: 'DELETE',
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            Swal.fire({
                title: 'Successo',
                text: 'Prenotazione eliminata con successo!',
                icon: 'success',
                confirmButtonText: 'OK'
            }).then(() => {
                closeModal(); // Chiudi la modale
                location.reload(); // Ricarica la pagina per aggiornare il calendario
            });
        } else {
            Swal.fire({
                title: 'Errore',
                text: 'Errore nella cancellazione della prenotazione: ' + data.error,
                icon: 'error',
                confirmButtonText: 'OK'
            });
        }
    })
    .catch(error => Swal.fire({
        title: 'Errore',
        text: 'Errore durante l\'eliminazione: ' + error,
        icon: 'error',
        confirmButtonText: 'OK'
    }));
}

function closeModal() {
    document.getElementById('detailModal').style.display = 'none';
}

function showLoader() {
    Swal.fire({
        title: 'Caricamento...',
        allowOutsideClick: false,
        didOpen: () => {
            Swal.showLoading();
        }
    });
}

function hideLoader() {
    Swal.close();
}
