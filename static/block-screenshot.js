// Bloqueia screenshot via tecla PrintScreen (limitado)
document.addEventListener("keyup", function(e) {
    if (e.key === "PrintScreen") {
        navigator.clipboard.writeText("Captura de tela desativada.");
        alert("Screenshot desativado.");
    }
});
document.addEventListener("keydown", function(e) {
    if ((e.ctrlKey || e.metaKey) && e.key === "s") e.preventDefault(); // Bloqueia Ctrl+S
});
