document.addEventListener('DOMContentLoaded', function () {
    const messageContainer = document.getElementById("message-container");
    if (messageContainer) {
        const messages = messageContainer.querySelectorAll("p");
        messages.forEach(message => {
            const category = message.dataset.category;
            const text = message.innerHTML;

            Swal.fire({
                title: category === 'success' ? 'Successo!' : 'Errore!',
                text: text,
                icon: category === 'success' ? 'success' : 'error',
                confirmButtonText: 'OK',
                confirmButtonColor: category === 'success' ? '#28a745' : '#dc3545'
            });
        });
    }

    const forgotPasswordLink = document.getElementById('forgot-password');

    if (forgotPasswordLink) {
        forgotPasswordLink.addEventListener('click', function (e) {
            e.preventDefault();

            Swal.fire({
                title: 'Reimposta password',
                html: `
                    <p>Non preoccuparti. Inserisci la tua email e ti invieremo le istruzioni per reimpostare la password.</p>
                    <input type="email" id="email" class="swal2-input" placeholder="Email">
                `,
                showCancelButton: true,
                confirmButtonText: 'Invia',
                cancelButtonText: 'Annulla',
                preConfirm: () => {
                    const email = document.getElementById('email').value;
                    if (!email) {
                        Swal.showValidationMessage('Inserisci un indirizzo email valido');
                    }
                    return email;
                }
            }).then((result) => {
                if (result.isConfirmed) {
                    const email = result.value;

                    // Invia la richiesta al server
                    fetch('/forgot_password', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ email })
                    })
                        .then(response => response.json())
                        .then(data => {
                            console.log(data); // Log della risposta del server
                            if (data.success) {
                                Swal.fire({
                                    title: 'Email inviata!',
                                    text: 'Controlla la tua casella di posta per il link di reimpostazione.',
                                    icon: 'success',
                                    timer: 3000,
                                    showConfirmButton: false
                                });
                            } else {
                                Swal.fire({
                                    title: 'Errore',
                                    text: data.error || 'Qualcosa è andato storto.',
                                    icon: 'error',
                                    confirmButtonText: 'OK'
                                });
                            }
                        })
                        .catch(error => {
                            console.error('Errore nella richiesta:', error);
                            Swal.fire({
                                title: 'Errore',
                                text: 'Impossibile inviare la richiesta. Riprova più tardi.',
                                icon: 'error',
                                confirmButtonText: 'OK'
                            });
                        });
                }
            });
        });
    }
});