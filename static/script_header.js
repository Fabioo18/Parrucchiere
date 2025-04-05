document.addEventListener("DOMContentLoaded", function() {
    // Carica l'HTML del header in ogni pagina
    const headerPlaceholder = document.getElementById('header-placeholder');
    if (headerPlaceholder) {
        fetch('header.html')
            .then(response => response.text())
            .then(data => {
                headerPlaceholder.innerHTML = data;
            })
            .catch(error => console.log('Errore nel caricamento dell\'header:', error));
    }
});
