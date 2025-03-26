// popupMobile.js

// Accede a la configuración definida en config.js
console.log("twpConfig desde popupMobile.js:", window.twpConfig);

// Usa la configuración, por ejemplo:
if (window.twpConfig.debug) {
    console.log("Modo de depuración activado");
}

// Realiza alguna acción con la configuración, por ejemplo:
const apiUrl = window.twpConfig.apiBaseUrl;
console.log("Base URL de la API:", apiUrl);

// Otros códigos que utilicen twpConfig
