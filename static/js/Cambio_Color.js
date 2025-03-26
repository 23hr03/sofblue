// Definir las rutas de los estilos (puedes ajustarlas a la ubicación de tus archivos CSS)
const estiloClaro = "{{ url_for('static', filename='css/estilo-claro.css') }}";
const estiloOscuro = "{{ url_for('static', filename='css/estilo-oscuro.css') }}";

// Obtener los botones de estilo claro y oscuro
const botonClaro = document.getElementById('boton-claro');
const botonOscuro = document.getElementById('boton-oscuro');

// Obtener el elemento de estilo CSS
const estiloCSS = document.getElementById('estilo-css');

// Establecer el estilo inicial
estiloCSS.href = estiloClaro; // Para estilo claro
localStorage.setItem('estilo', estiloClaro); // Guardar en localStorage

// Verificar si hay una preferencia de estilo guardada en localStorage
const preferenciaEstilo = localStorage.getItem('estilo');

// Aplicar la preferencia de estilo guardada (si existe)
if (preferenciaEstilo) {
    estiloCSS.href = preferenciaEstilo;
}

// Función para actualizar los botones según el estilo actual
function actualizarBotones() {
    if (estiloCSS.href.includes('css/estilo-claro.css')) {
        botonClaro.disabled = true; // Deshabilitar el botón de modo claro si ya está activo
        botonOscuro.disabled = false;
    } else {
        botonOscuro.disabled = true; // Deshabilitar el botón de modo oscuro si ya está activo
        botonClaro.disabled = false;
    }
}

// Manejar el evento de clic en el botón de estilo claro
botonClaro.addEventListener('click', () => {
    // Cambiar el estilo del enlace de estilo CSS
    estiloCSS.href = estiloClaro;

    // Guardar la preferencia de estilo en localStorage
    localStorage.setItem('estilo-css', estiloClaro);

    // Actualizar el estado de los botones
    actualizarBotones();
});

// Manejar el evento de clic en el botón de estilo oscuro
botonOscuro.addEventListener('click', () => {
    // Cambiar el estilo del enlace de estilo CSS
    estiloCSS.href = estiloOscuro;

    // Guardar la preferencia de estilo en localStorage
    localStorage.setItem('estilo-css', estiloOscuro);

    // Actualizar el estado de los botones
    actualizarBotones();
});

// Inicializar los botones según el estilo cargado
actualizarBotones();
//=========================================================================

