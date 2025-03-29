document.addEventListener("DOMContentLoaded", function() {
    let pulsante = document.querySelector(".btn");

    pulsante.addEventListener("mouseover", function() {
        this.style.backgroundColor = "#e6b56d";
        this.style.transform = "scale(1.05)";
    });

    pulsante.addEventListener("mouseleave", function() {
        this.style.backgroundColor = "#cda45e";
        this.style.transform = "scale(1)";
    });
});
