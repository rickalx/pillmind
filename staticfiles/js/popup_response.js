/**
 * Función para abrir una ventana emergente
 */
function showAddAnotherPopup(triggeringLink) {
    var name = triggeringLink.id.replace(/^add_/, '');
    name = id_to_windowname(name);
    href = triggeringLink.href;
    if (href.indexOf('?') === -1) {
        href += '?_popup=1';
    } else {
        href += '&_popup=1';
    }
    var win = window.open(href, name, 'height=500,width=800,resizable=yes,scrollbars=yes');
    win.focus();
    return false;
}

/**
 * Función para cerrar la ventana emergente y actualizar el select
 */
function dismissAddRelatedObjectPopup(win, objId, objRepr) {
    // Obtener el select que se está actualizando
    var name = win.name;
    var elem = document.getElementById(name);
    
    // Crear una nueva opción
    var option = new Option(objRepr, objId);
    
    // Agregar la opción al select
    elem.options[elem.options.length] = option;
    
    // Seleccionar la nueva opción
    elem.selectedIndex = elem.options.length - 1;
    
    // Cerrar la ventana emergente
    win.close();
}

/**
 * Función para convertir un ID a un nombre de ventana
 */
function id_to_windowname(id) {
    id = id.replace(/\./g, '__dot__');
    id = id.replace(/\-/g, '__dash__');
    return id;
}
