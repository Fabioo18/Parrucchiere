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
});