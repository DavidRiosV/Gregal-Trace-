// Mostrar u ocultar la contraseña con el botón del ojo
document.querySelectorAll("[data-mostrar-contrasena]").forEach(function (boton) {
    boton.addEventListener("click", function () {
        var campo = document.getElementById(boton.dataset.mostrarContrasena);
        var oculta = campo.type === "password";
        campo.type = oculta ? "text" : "password";
        boton.setAttribute("aria-label", oculta ? "Ocultar contraseña" : "Mostrar contraseña");
    });
});
