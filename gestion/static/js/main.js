// Mostrar u ocultar la contraseña con el botón del ojo.
// Cuando la contraseña se ve, el icono pasa a ojo tachado: pulsarlo la vuelve a ocultar.
document.querySelectorAll("[data-mostrar-contrasena]").forEach(function (boton) {
    boton.addEventListener("click", function () {
        var campo = document.getElementById(boton.dataset.mostrarContrasena);
        var mostrar = campo.type === "password";
        campo.type = mostrar ? "text" : "password";
        boton.classList.toggle("entrada__ojo--visible", mostrar);
        boton.setAttribute("aria-pressed", mostrar ? "true" : "false");
        boton.setAttribute("aria-label", mostrar ? "Ocultar contraseña" : "Mostrar contraseña");
    });
});
