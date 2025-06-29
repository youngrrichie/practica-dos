// Elementos DOM
const inputCode = document.getElementById('input-code');
const analizarBtn = document.getElementById('analizar-btn');
const limpiarBtn = document.getElementById('limpiar-btn');
const statusMessage = document.getElementById('status-message');
const treeContainer = document.getElementById('tree-container');
const errorContainer = document.getElementById('error-container');

// Elementos de display de máquina
const saldoValue = document.getElementById('saldo-value');
const refrescosValue = document.getElementById('refrescos-value');
const nivelValue = document.getElementById('nivel-value');

// Elementos de estadísticas
const saldoFinal = document.getElementById('saldo-final');
const refrescosTotal = document.getElementById('refrescos-total');
const estadoValidez = document.getElementById('estado-validez');
const maxNivel = document.getElementById('max-nivel');
const levelStatsEl = document.getElementById('level-stats');

const ejemploLinks = document.querySelectorAll('.ejemplo-link');

// Variables globales
let debounceTimeout;
const DEBOUNCE_TIME = 500; // tiempo en ms para debounce

// Inicialización
document.addEventListener('DOMContentLoaded', () => {
    // Eventos
    analizarBtn.addEventListener('click', analizarCodigo);
    limpiarBtn.addEventListener('click', limpiarEditor);
    inputCode.addEventListener('input', debounceAnalisis);
    
    // Configurar ejemplos
    ejemploLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            inputCode.value = link.textContent;
            analizarCodigo();
        });
    });
});

// Función para debounce (retrasar el análisis durante la escritura)
function debounceAnalisis() {
    clearTimeout(debounceTimeout);
    debounceTimeout = setTimeout(analizarCodigo, DEBOUNCE_TIME);
}

// Función principal para analizar el código ingresado
function analizarCodigo() {
    const codigo = inputCode.value.trim();
    
    if (!codigo) {
        mostrarEstadoInicial();
        return;
    }
    
    // Enviar la cadena al servidor para análisis
    fetch('/analizar', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ cadena: codigo })
    })
    .then(response => response.json())
    .then(data => {
        // Actualizar UI con resultados
        if (data.valido) {
            statusMessage.className = 'message success';
        } else {
            statusMessage.className = 'message error';
        }
        statusMessage.textContent = data.mensaje;
        
        // Siempre intentamos mostrar la visualización y estadísticas
        // (incluso si hay errores, para ver el estado de la máquina)
        visualizarMaquina(data);
        mostrarEstadisticas(data.estadisticas);
        mostrarErrores(data.estadisticas.errores);
    })
    .catch(error => {
        console.error('Error al analizar:', error);
        statusMessage.className = 'message error';
        statusMessage.textContent = 'Error al comunicarse con el servidor';
        limpiarVisualizacion();
        limpiarEstadisticas();
    });
}

// Función para limpiar el editor
function limpiarEditor() {
    inputCode.value = '';
    mostrarEstadoInicial();
}

// Función para reiniciar la UI a su estado inicial
function mostrarEstadoInicial() {
    statusMessage.className = 'message';
    statusMessage.textContent = 'Ingrese una expresión para analizar';
    limpiarVisualizacion();
    limpiarEstadisticas();
}

// Función para limpiar la visualización del árbol
function limpiarVisualizacion() {
    treeContainer.innerHTML = '';
}

// Función para limpiar las estadísticas
function limpiarEstadisticas() {
    saldoFinal.textContent = '0';
    refrescosTotal.textContent = '0';
    estadoValidez.textContent = 'Pendiente';
    maxNivel.textContent = '0';
    saldoValue.textContent = '0';
    refrescosValue.textContent = '0';
    nivelValue.textContent = '0';
    levelStatsEl.innerHTML = '';
    errorContainer.innerHTML = '';
}

// Función para visualizar la máquina expendedora
function visualizarMaquina(data) {
    // Actualizar display de la máquina
    const estadisticas = data.estadisticas || {};
    const saldo = estadisticas.saldo_final || 0;
    const refrescos = estadisticas.num_refrescos || 0;
    const valido = estadisticas.valido_semantico || false;

    saldoValue.textContent = saldo;
    refrescosValue.textContent = refrescos;
    nivelValue.textContent = '0'; // Por defecto mostramos nivel 0
    
    // Información de debug
    console.log("Datos recibidos:", data);
    console.log("Árbol para visualizar:", data.arbol);
    
    // Visualizar la máquina expendedora
    if (data.arbol) {
        visualizarArbol(data.arbol);
    } else {
        console.warn("No hay datos de árbol para visualizar");
        treeContainer.innerHTML = '<div class="tree-error">No se pudo generar el árbol de derivación</div>';
    }
}

// Función para mostrar errores
function mostrarErrores(errores = []) {
    errorContainer.innerHTML = '';
    
    if (!errores || errores.length === 0) {
        return;
    }
    
    const ul = document.createElement('ul');
    ul.className = 'errores-list';
    
    errores.forEach(error => {
        const li = document.createElement('li');
        li.textContent = error;
        li.className = 'error-item';
        ul.appendChild(li);
    });
    
    errorContainer.appendChild(ul);
}

// Función para visualizar el árbol de la máquina usando D3.js
function visualizarArbol(datos) {
    // Limpiar el contenedor antes de dibujar
    treeContainer.innerHTML = '';
    
    if (!datos) {
        return;
    }
    
    // Configurar el tamaño del SVG
    const margin = {top: 40, right: 120, bottom: 40, left: 120};
    const width = 800 - margin.left - margin.right;
    const height = 600 - margin.top - margin.bottom;
    
    // Crear el elemento SVG
    const svg = d3.select('#tree-container').append('svg')
        .attr('width', width + margin.left + margin.right)
        .attr('height', height + margin.top + margin.bottom)
        .append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`);
    
    // Crear la jerarquía d3
    const root = d3.hierarchy(datos, d => d.hijos || []);
    
    // Agregar profundidades para distribuir mejor los nodos
    root.descendants().forEach(d => {
        d.depth = d.depth * 2;
    });
    
    // Crear el diseño del árbol
    const treeLayout = d3.tree().size([height, width]);
    treeLayout(root);
    
    // Crear enlaces
    svg.selectAll('.link')
        .data(root.links())
        .enter().append('path')
        .attr('class', d => `link ${d.target.data.valido ? 'valid-link' : 'invalid-link'}`)
        .attr('d', d3.linkHorizontal()
            .x(d => d.y)
            .y(d => d.x));
    
    // Crear nodos
    const node = svg.selectAll('.node')
        .data(root.descendants())
        .enter().append('g')
        .attr('class', d => `node ${d.data.valido ? 'valid' : 'invalid'}`)
        .attr('transform', d => `translate(${d.y},${d.x})`)
        .on('mouseover', showNodeDetails)
        .on('mouseout', hideNodeDetails);
    
    // Agregar círculos a los nodos
    node.append('circle')
        .attr('r', d => {
            // Tamaño según el tipo del nodo
            switch (d.data.tipo) {
                case 'maquina': return 15;
                case 'bloque': return 13;
                case 'operaciones': return 12;
                case 'operacion_moneda': return 10;
                case 'operacion_refresco': return 10;
                case 'operacion_cambio': return 10;
                case 'operacion_subbloque': return 12;
                default: return 8;
            }
        })
        .style('fill', d => {
            // Colorear según el tipo de nodo y si es válido
            if (d.data.errores && d.data.errores.length > 0) {
                return '#e74c3c'; // rojo para nodos con errores
            }
            
            switch (d.data.tipo) {
                case 'maquina': return '#3498db'; // azul
                case 'bloque': return '#2ecc71'; // verde
                case 'operaciones': return '#9b59b6'; // púrpura
                case 'operacion_moneda': return '#f1c40f'; // amarillo (moneda)
                case 'operacion_refresco': return '#e67e22'; // naranja (refresco)
                case 'operacion_cambio': return '#16a085'; // verde azulado (cambio)
                case 'operacion_subbloque': return '#2980b9'; // azul oscuro
                default: return '#95a5a6'; // gris para otros
            }
        });
    
    // Agregar etiquetas a los nodos
    node.append('text')
        .attr('dy', '.35em')
        .attr('x', d => d.children ? -20 : 20)
        .style('text-anchor', d => d.children ? 'end' : 'start')
        .text(d => {
            // Mostrar información según el tipo de nodo
            if (d.data.texto) {
                return d.data.texto;
            }
            
            switch (d.data.tipo) {
                case 'maquina':
                    return `Máquina (S:${d.data.saldo || 0}, R:${d.data.refrescos || 0})`;
                case 'bloque':
                    return `Bloque (S:${d.data.atributos.saldo_inicial || 0}→${d.data.atributos.saldo_final || 0}, N:${d.data.nivel || 0})`;
                case 'operaciones':
                    return `Operaciones (R:${d.data.refrescos || 0})`;
                case 'operacion_moneda':
                    return `$ (S:${d.data.atributos.saldo_inicial || 0}→${d.data.atributos.saldo_final || 0})`;
                case 'operacion_refresco':
                    return `R (S:${d.data.atributos.saldo_inicial || 0}→${d.data.atributos.saldo_final || 0})`;
                case 'operacion_cambio':
                    return `< (S:${d.data.atributos.saldo_inicial || 0}→${d.data.atributos.saldo_final || 0})`;
                case 'operacion_subbloque':
                    return `Subbloque (N:${d.data.nivel || 0})`;
                default:
                    return d.data.tipo || 'Desconocido';
            }
        });
        
    // Popup para detalles al pasar el mouse
    const tooltip = svg.append("g")
        .attr("class", "tooltip")
        .style("display", "none");
        
    tooltip.append("rect")
        .attr("width", 180)
        .attr("height", 120)
        .attr("rx", 5)
        .attr("ry", 5)
        .attr("fill", "white")
        .attr("stroke", "#ccc")
        .attr("stroke-width", 1);
        
    tooltip.append("text")
        .attr("x", 10)
        .attr("y", 20)
        .attr("id", "tooltip-text")
        .style("font-size", "12px");
        
    // Funciones para mostrar/ocultar detalles de nodos
    function showNodeDetails(event, d) {
        const tooltipText = tooltip.select("#tooltip-text");
        tooltipText.selectAll("tspan").remove();
        
        // Añadir múltiples líneas de texto
        tooltipText.append("tspan")
            .attr("x", 10)
            .attr("dy", 0)
            .style("font-weight", "bold")
            .text(`Tipo: ${d.data.tipo}`);
            
        tooltipText.append("tspan")
            .attr("x", 10)
            .attr("dy", 20)
            .text(`Nivel: ${d.data.nivel || 0}`);
            
        tooltipText.append("tspan")
            .attr("x", 10)
            .attr("dy", 20)
            .text(`Saldo Inicial: ${d.data.atributos?.saldo_inicial || 0}`);
            
        tooltipText.append("tspan")
            .attr("x", 10)
            .attr("dy", 20)
            .text(`Saldo Final: ${d.data.atributos?.saldo_final || 0}`);
            
        tooltipText.append("tspan")
            .attr("x", 10)
            .attr("dy", 20)
            .text(`Refrescos: ${d.data.atributos?.refrescos || 0}`);
        
        // Mostrar errores si existen
        if (d.data.errores && d.data.errores.length > 0) {
            tooltipText.append("tspan")
                .attr("x", 10)
                .attr("dy", 20)
                .style("fill", "red")
                .text(`Errores: ${d.data.errores.length}`);
        }
        
        tooltip
            .style("display", "block")
            .attr("transform", `translate(${d.y + 20},${d.x - 60})`);
    }
    
    function hideNodeDetails() {
        tooltip.style("display", "none");
    }
}

// Función para mostrar estadísticas
function mostrarEstadisticas(estadisticas) {
    if (!estadisticas) {
        limpiarEstadisticas();
        return;
    }
    
    saldoFinal.textContent = estadisticas.saldo_final || 0;
    refrescosTotal.textContent = estadisticas.num_refrescos || 0;
    estadoValidez.textContent = estadisticas.valido_semantico ? 'Válido' : 'Inválido';
    estadoValidez.className = estadisticas.valido_semantico ? 'stat-value valid' : 'stat-value invalid';
    
    // Determinar nivel máximo a partir de errores
    let nivelMax = 0;
    if (estadisticas.errores && estadisticas.errores.length > 0) {
        // Intentar extraer nivel máximo de mensajes de error
        for (const error of estadisticas.errores) {
            const match = error.match(/nivel (\d+)/i);
            if (match && match[1]) {
                nivelMax = Math.max(nivelMax, parseInt(match[1]));
            }
        }
    }
    
    maxNivel.textContent = nivelMax;
    
    // Mostrar barras de nivel si están disponibles
    levelStatsEl.innerHTML = '';
    
    // Crear barras para refrescos y saldo
    const saldoContainer = document.createElement('div');
    saldoContainer.className = 'level-bar-container';
    
    const saldoLabel = document.createElement('div');
    saldoLabel.className = 'level-label';
    saldoLabel.innerHTML = `
        <span>Saldo</span>
        <span>${estadisticas.saldo_final || 0}</span>
    `;
    
    const saldoBar = document.createElement('div');
    saldoBar.className = 'level-bar';
    // Ancho relativo basado en un máximo de 10 monedas
    const saldoPorcentaje = Math.min(100, ((estadisticas.saldo_final || 0) / 10) * 100);
    saldoBar.style.width = `${saldoPorcentaje}%`;
    saldoBar.style.backgroundColor = '#f1c40f'; // amarillo para saldo
    
    saldoContainer.appendChild(saldoLabel);
    saldoContainer.appendChild(saldoBar);
    levelStatsEl.appendChild(saldoContainer);
    
    // Barra para refrescos
    const refrescoContainer = document.createElement('div');
    refrescoContainer.className = 'level-bar-container';
    
    const refrescoLabel = document.createElement('div');
    refrescoLabel.className = 'level-label';
    refrescoLabel.innerHTML = `
        <span>Refrescos</span>
        <span>${estadisticas.num_refrescos || 0}</span>
    `;
    
    const refrescoBar = document.createElement('div');
    refrescoBar.className = 'level-bar';
    // Ancho relativo basado en el límite de 3 refrescos por bloque
    const refrescoPorcentaje = Math.min(100, ((estadisticas.num_refrescos || 0) / 3) * 100);
    refrescoBar.style.width = `${refrescoPorcentaje}%`;
    refrescoBar.style.backgroundColor = '#2ecc71'; // verde para refrescos
    
    refrescoContainer.appendChild(refrescoLabel);
    refrescoContainer.appendChild(refrescoBar);
    levelStatsEl.appendChild(refrescoContainer);
}
