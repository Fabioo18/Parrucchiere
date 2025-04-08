document.addEventListener('DOMContentLoaded', function () {
    const form = document.querySelector('.auth-form');
    const passwordInput = form.querySelector('input[name="password"]');
    const confirmPasswordInput = form.querySelector('input[name="confirm_password"]');

    form.addEventListener('submit', function (e) {
        e.preventDefault();

        const password = passwordInput.value.trim();
        const confirmPassword = confirmPasswordInput.value.trim();

        if (password !== confirmPassword) {
            Swal.fire({
                title: 'Errore',
                text: 'Le password non corrispondono. Riprova.',
                icon: 'error',
                confirmButtonText: 'OK'
            });
            return;
        }

        // Usa FormData per inviare i dati come form-data
        const formData = new FormData();
        formData.append('password', password);
        formData.append('confirm_password', confirmPassword);

        // Invia la richiesta al server
        fetch(window.location.href, {
            method: 'POST',
            body: formData
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    Swal.fire({
                        title: 'Successo!',
                        text: data.message,
                        icon: 'success',
                        timer: 3000,
                        showConfirmButton: false
                    }).then(() => {
                        window.location.href = '/login'; // Reindirizza al login
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
    });
});