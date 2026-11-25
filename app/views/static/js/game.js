const TAMANOS_BARCO = {
  portaaviones: 4,
  acorazado: 3,
  submarino: 3,
  destructor: 2,
};

let estadoActual = null;
let orientacion = "H";
let colaBarcosPorUbicar = [];
let ubicacionesManuales = [];

function alternarOrientacion() {
  orientacion = orientacion === "H" ? "V" : "H";
  document.getElementById("orientacion-label").textContent =
    orientacion === "H" ? "Horizontal (H)" : "Vertical (V)";
}

function inicializarColaBarcos(configBarcos) {
  if (colaBarcosPorUbicar.length > 0 || ubicacionesManuales.length > 0) return;
  configBarcos.forEach((item) => {
    for (let i = 0; i < item.cantidad; i++) {
      colaBarcosPorUbicar.push({
        tipo: item.tipo,
        tamano: TAMANOS_BARCO[item.tipo] || 2,
      });
    }
  });
  actualizarTextoDespliegue();
}

function actualizarTextoDespliegue() {
  const lbl = document.getElementById("instruccion-despliegue");
  const btn = document.getElementById("btn-confirmar-flota");
  if (colaBarcosPorUbicar.length > 0) {
    const sig = colaBarcosPorUbicar[0];
    lbl.textContent = `Ubica tu ${sig.tipo.toUpperCase()} (${sig.tamano} casillas) haciendo clic en "Tu Flota".`;
    btn.disabled = true;
  } else {
    lbl.textContent = "Todos los barcos están posicionados. Haz clic en Confirmar Flota.";
    btn.disabled = false;
  }
}

function manejarClicDespliegue(fila, col) {
  if (!estadoActual || estadoActual.estado !== "DESPLIEGUE" || estadoActual.flota_lista) return;
  if (colaBarcosPorUbicar.length === 0) return;

  const barco = colaBarcosPorUbicar[0];
  const n = estadoActual.tamano_tablero;
  const coords = [];

  for (let i = 0; i < barco.tamano; i++) {
    const r = fila + (orientacion === "V" ? i : 0);
    const c = col + (orientacion === "H" ? i : 0);
    if (r >= n || c >= n) return alert("El barco se sale del tablero.");
    coords.push(`${r},${c}`);
  }

  const ocupadas = new Set();
  ubicacionesManuales.forEach((u) => {
    for (let i = 0; i < u.tamano; i++) {
      const r = u.fila + (u.orientacion === "V" ? i : 0);
      const c = u.col + (u.orientacion === "H" ? i : 0);
      ocupadas.add(`${r},${c}`);
    }
  });

  if (coords.some((c) => ocupadas.has(c))) {
    return alert("Esa posición se cruza con otro barco.");
  }

  ubicacionesManuales.push({
    tipo: barco.tipo,
    tamano: barco.tamano,
    fila,
    col,
    orientacion,
  });
  colaBarcosPorUbicar.shift();
  actualizarTextoDespliegue();
  renderizarTableros(estadoActual);
}

async function confirmarDespliegueManual() {
  const res = await fetch(`/api/salas/${CODIGO_SALA}/desplegar`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ jugador_id: JUGADOR_ID, ubicaciones: ubicacionesManuales }),
  });
  const data = await res.json();
  if (!res.ok) return alert(data.error);
  estadoActual = data;
  renderizarTodo(data);
}

async function despliegueAleatorio() {
  const res = await fetch(`/api/salas/${CODIGO_SALA}/desplegar`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ jugador_id: JUGADOR_ID, ubicaciones: null }),
  });
  const data = await res.json();
  if (!res.ok) return alert(data.error);
  estadoActual = data;
  renderizarTodo(data);
}

async function disparar(fila, col) {
  if (!estadoActual || estadoActual.estado !== "EN_CURSO" || !estadoActual.es_mi_turno) return;
  const res = await fetch(`/api/salas/${CODIGO_SALA}/disparar`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ jugador_id: JUGADOR_ID, fila, col }),
  });
  const data = await res.json();
  if (!res.ok) return alert(data.error);
  estadoActual = data.estado_sala;
  renderizarTodo(estadoActual);
}

async function guardarPartida() {
  const res = await fetch(`/api/salas/${CODIGO_SALA}/guardar`, { method: "POST" });
  const data = await res.json();
  alert(data.mensaje || data.error);
}

function renderizarTableros(data) {
  const n = data.tamano_tablero;
  const divPropio = document.getElementById("tablero-propio");
  const divRival = document.getElementById("tablero-rival");
  divPropio.style.gridTemplateColumns = `repeat(${n}, 1fr)`;
  divRival.style.gridTemplateColumns = `repeat(${n}, 1fr)`;

  const matrizPropio = data.tablero_propio.map((fila) => [...fila]);
  if (data.estado === "DESPLIEGUE" && !data.flota_lista) {
    ubicacionesManuales.forEach((u) => {
      for (let i = 0; i < u.tamano; i++) {
        const r = u.fila + (u.orientacion === "V" ? i : 0);
        const c = u.col + (u.orientacion === "H" ? i : 0);
        matrizPropio[r][c] = "BARCO";
      }
    });
  }

  divPropio.innerHTML = "";
  for (let r = 0; r < n; r++) {
    for (let c = 0; c < n; c++) {
      const val = matrizPropio[r]?.[c] || "AGUA";
      const cell = document.createElement("div");
      cell.className = `cell cell-${val}`;
      if (data.estado === "DESPLIEGUE" && !data.flota_lista) {
        cell.classList.add("cell-clickable");
        cell.onclick = () => manejarClicDespliegue(r, c);
      }
      cell.textContent = val === "TOCADO" ? "X" : val === "FALLO" ? "•" : "";
      divPropio.appendChild(cell);
    }
  }

  divRival.innerHTML = "";
  for (let r = 0; r < n; r++) {
    for (let c = 0; c < n; c++) {
      const val = data.tablero_rival[r]?.[c] || "OCULTO";
      const cell = document.createElement("div");
      cell.className = `cell cell-${val}`;
      if (data.estado === "EN_CURSO" && data.es_mi_turno && val === "OCULTO") {
        cell.classList.add("cell-clickable");
        cell.onclick = () => disparar(r, c);
      }
      cell.textContent = val === "TOCADO" ? "X" : val === "FALLO" ? "•" : "";
      divRival.appendChild(cell);
    }
  }
}

function renderizarTodo(data) {
  const banner = document.getElementById("estado-banner");
  const panelDespliegue = document.getElementById("panel-despliegue");

  if (data.estado === "ESPERANDO_RIVAL") {
    banner.textContent = `Esperando rival... Comparte el código ${data.codigo}`;
    panelDespliegue.style.display = "none";
  } else if (data.estado === "DESPLIEGUE") {
    banner.textContent = data.flota_lista
      ? "Flota lista. Esperando al rival..."
      : "Fase de despliegue: ubica tus embarcaciones";
    panelDespliegue.style.display = data.flota_lista ? "none" : "block";
    inicializarColaBarcos(data.config_barcos);
  } else if (data.estado === "EN_CURSO") {
    panelDespliegue.style.display = "none";
    banner.textContent = data.es_mi_turno ? "¡ES TU TURNO DE DISPARAR!" : "Turno del rival...";
  } else if (data.estado === "FINALIZADO") {
    panelDespliegue.style.display = "none";
    banner.textContent = `Partida finalizada · Ganador: ${data.ganador_nombre}`;
  }

  renderizarTableros(data);

  const lista = document.getElementById("bitacora-lista");
  lista.innerHTML = "";
  data.bitacora.slice().reverse().forEach((msg) => {
    const li = document.createElement("li");
    li.textContent = msg;
    lista.appendChild(li);
  });
}

async function sincronizarEstado() {
  try {
    const res = await fetch(`/api/salas/${CODIGO_SALA}/estado?jugador_id=${JUGADOR_ID}`);
    if (!res.ok) return;
    const data = await res.json();
    estadoActual = data;
    renderizarTodo(data);
  } catch (err) {
    console.error(err);
  }
}

sincronizarEstado();
setInterval(sincronizarEstado, 1200);