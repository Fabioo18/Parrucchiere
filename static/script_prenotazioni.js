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
                    alert("Non è possibile selezionare una data passata.");
                    return;
                }

                // Blocco per domenica o lunedì
                if (dataSelezionata.getDay() === 0 || dataSelezionata.getDay() === 1) {
                    alert("Questo giorno non è disponibile per le prenotazioni.");
                    return;
                }

                // Recupera gli orari disponibili per la data selezionata
                // Recupera gli orari disponibili per la data selezionata
                fetch(`/api/orari_disponibili/${info.dateStr}`)
                .then(response => response.json())
                .then(orari => {
                    console.log("Orari disponibili:", orari);

                    // Rimuoviamo orari troppo vicini all'ora attuale se la data selezionata è oggi
                    const oggi = new Date();
                    const dataSelezionata = new Date(info.dateStr);
                    let orariFiltrati = orari;

                    if (dataSelezionata.toDateString() === oggi.toDateString()) {
                        const oraAttuale = oggi.getHours();
                        const minutiAttuali = oggi.getMinutes();

                        orariFiltrati = orari.filter(orario => {
                            const [h, m] = orario.split(':').map(Number);
                            const orarioPrenotazione = new Date();
                            orarioPrenotazione.setHours(h, m, 0, 0);

                            // Richiediamo almeno 30 minuti di anticipo
                            return (orarioPrenotazione - oggi) >= 30 * 60 * 1000;
                        });
                    }

                    if (orariFiltrati.length === 0) {
                        let cella = document.querySelector(`[data-date='${info.dateStr}']`);
                        if (cella) {
                            cella.classList.add('indisponibile');
                            cella.style.pointerEvents = 'none';
                        }
                        alert("Non ci sono orari prenotabili disponibili per oggi.");
                    } else {
                        let cella = document.querySelector(`[data-date='${info.dateStr}']`);
                        if (cella) {
                            cella.classList.remove('indisponibile');
                            cella.style.pointerEvents = 'auto';
                        }

                        dataInput.value = info.dateStr;
                        modal.style.display = "block";

                        orarioSelect.innerHTML = "";
                        orariFiltrati.forEach(orario => {
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

        if (selectedServices.length === 0) {
            event.preventDefault();
            alert("Per favore, seleziona almeno un servizio.");
        } else {
            console.log(`Servizi selezionati: ${selectedServices.length}`);
        }
    });
});
