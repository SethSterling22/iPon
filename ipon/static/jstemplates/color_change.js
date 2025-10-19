function cambiarFondoColor() {
    oldColor = hexToRgb('E55806');
    newColor = hexToRgb('004E86');
    
    orange = hexToRgb('D44E05'); 
    blue = hexToRgb('023F6B');

    paleorange = hexToRgb('F28D77');
    paleblue = hexToRgb('3189C2');

    // Seleccionar todos los elementos
    const allElements = document.querySelectorAll('*');

        if (is_driver){
        allElements.forEach(element => {
            // Comprobar el color de fondo actual si el usuario tiene el modo Driver activado
            if (getComputedStyle(element).backgroundColor === oldColor || rgbToHex(getComputedStyle(element).backgroundColor) === oldColor) {
                element.style.backgroundColor = newColor;

                
            }
            ///////////// Cambios de estilos para las tarjetas de pons /////////////
            if (getComputedStyle(element).borderColor === oldColor || rgbToHex(getComputedStyle(element).borderColor) === oldColor) {
                element.style.borderColor = newColor;

                
            }

            if (getComputedStyle(element).backgroundColor === paleorange || rgbToHex(getComputedStyle(element).backgroundColor) === paleorange) {
                element.style.backgroundColor = paleblue;

                
            }


            ///////////// Cambios de estilos para las tarjetas de pons /////////////

            // Cambiar el color de fondo de hover directamente
            if (element.classList.contains('footer-title')) {
                element.onmouseover = function() {
                    element.style.backgroundColor = blue;
                };
                element.onmouseout = function() {
                    element.style.backgroundColor = newColor; 
                };
            }
            // Cambiar el color de fondo de hover directamente
            if (element.classList.contains('back-title')) {
                element.onmouseover = function() {
                    element.style.backgroundColor = blue;
                };
                element.onmouseout = function() {
                    element.style.backgroundColor = newColor; 
                };
            }
        });
    } else {
        allElements.forEach(element => {
            // Comprobar el color de fondo si el usuario tiene el modo Driver  desactivado
            if (getComputedStyle(element).backgroundColor === newColor || rgbToHex(getComputedStyle(element).backgroundColor) === newColor) {
                element.style.backgroundColor = oldColor;
            
            }

            // Cambiar el color de fondo de hover directamente
            if (element.classList.contains('footer-title')) {
                element.onmouseover = function() {
                    element.style.backgroundColor = orange;
                };
                element.onmouseout = function() {
                    element.style.backgroundColor = oldColor;
                };
            }
        });
    }
}

function hexToRgb(hex) {
    let r = 0, g = 0, b = 0;
    hex = hex.replace(/^#/, '');

    if (hex.length === 6) {
        r = parseInt(hex.substring(0, 2), 16);
        g = parseInt(hex.substring(2, 4), 16);
        b = parseInt(hex.substring(4, 6), 16);
    }
    return `rgb(${r}, ${g}, ${b})`;
}

function rgbToHex(rgb) {
    const result = rgb.match(/\d+/g);
    return result ? `#${((1 << 24) + (parseInt(result[0]) << 16) + (parseInt(result[1]) << 8) + parseInt(result[2])).toString(16).slice(1)}` : null;
}


document.addEventListener('DOMContentLoaded', () => {
    // Llama a la función para probar el cambio de color
    cambiarFondoColor(); // Llama a la función al cargar la página
});

