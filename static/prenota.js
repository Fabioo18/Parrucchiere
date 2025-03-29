document.getElementById("prenotaForm").addEventListener("submit", function(event) {
    event.preventDefault();
    
    let nome = document.getElementById("nome").value;
    let data = document.getElementById("data").value;
    let servizio = document.getElementById("servizio").value;

    fetch("/prenotazioni", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ nome: nome, data: data, servizio: servizio })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("risultato").innerText = data.message;
    });
});
