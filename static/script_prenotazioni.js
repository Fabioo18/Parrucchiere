document.addEventListener("DOMContentLoaded", function() {
    const form = document.getElementById('booking-form');
    const inputs = form.querySelectorAll('input, select');
    const messageContainer = document.getElementById('message-container');

    // Animazione dei campi quando sono in focus
    inputs.forEach(input => {
        input.addEventListener('focus', function() {
            input.style.transition = 'all 0.3s ease';
            input.style.borderColor = '#3498db';
            input.style.boxShadow = '0 0 8px rgba(52, 152, 219, 0.3)';
        });

        input.addEventListener('blur', function() {
            input.style.borderColor = '#ccc';
            input.style.boxShadow = 'none';
        });
    });

    // Animazione dei messaggi di errore o successo
    if (messageContainer) {
        const messages = messageContainer.querySelectorAll('p');
        messages.forEach(message => {
            message.style.opacity = '0';
            message.style.transition = 'opacity 1s ease-in-out';

            // Aggiungi la transizione a tutti i messaggi
            setTimeout(() => {
                message.style.opacity = '1';
            }, 100); // Ritardo per la visibilità
        });
    }

    // Validazione del modulo prima dell'invio
    form.addEventListener('submit', function(event) {
        let isValid = true;
        inputs.forEach(input => {
            if (!input.value.trim()) {
                isValid = false;
                input.style.borderColor = '#e74c3c';
                input.style.boxShadow = '0 0 8px rgba(231, 76, 60, 0.3)';
            }
        });

        if (!isValid) {
            event.preventDefault(); // Impedisce l'invio se ci sono campi vuoti
            alert("Per favore, compila tutti i campi.");
        }
    });
});
