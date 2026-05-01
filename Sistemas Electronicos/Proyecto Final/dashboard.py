#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Piano Theremin — Dashboard Streamlit en tiempo real
====================================================
Conéctate por Bluetooth al BT-05 de la Raspberry Pi
y visualiza el estado del instrumento en tiempo real.

Instalación:
    pip install streamlit pyserial

Uso:
    streamlit run theremin_dashboard.py
"""

import streamlit as st
import serial
import serial.tools.list_ports
import json
import time
import threading
from collections import deque
from datetime import datetime

# ──────────────────────────────────────────────────────────────────────────────
# Configuración de página
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Piano Theremin Monitor",
    page_icon="🎹",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────────────────────────
# Frecuencias de notas (para mostrar Hz)
# ──────────────────────────────────────────────────────────────────────────────
NOTAS_HZ = {
    'Do3': 130.81, 'Do#3': 138.59, 'Re3': 146.83, 'Re#3': 155.56,
    'Mi3': 164.81, 'Fa3': 174.61, 'Fa#3': 185.00, 'Sol3': 196.00,
    'Sol#3': 207.65, 'La3': 220.00, 'La#3': 233.08, 'Si3': 246.96,
    'Do4': 261.63, 'Do#4': 277.18, 'Re4': 293.66, 'Re#4': 311.13,
    'Mi4': 329.63, 'Fa4': 349.23, 'Fa#4': 369.99, 'Sol4': 392.00,
    'Sol#4': 415.30, 'La4': 440.00, 'La#4': 466.16, 'Si4': 493.88,
    'Do5': 523.25,
}

ESCALAS = {
    "Do Mayor completa": ['Do3','Re3','Mi3','Fa3','Sol3','La3','Si3','Do4','Re4','Mi4','Fa4','Sol4','La4','Si4','Do5'],
    "Do Mayor (octava)": ['Do4','Re4','Mi4','Fa4','Sol4','La4','Si4','Do5'],
    "Pentatónica":       ['Do4','Re4','Mi4','Sol4','La4','Do5'],
    "Blues":             ['Do4','Re#4','Fa4','Sol4','Sol#4','Si4','Do5'],
    "Cromática":         ['Do4','Do#4','Re4','Re#4','Mi4','Fa4','Fa#4','Sol4','Sol#4','La4','La#4','Si4','Do5'],
}

MODOS_COLOR = {
    "LIBRE":        "#7C3AED",
    "PIANO":        "#1D9E75",
    "THEREMIN":     "#185FA5",
    "APRENDIZAJE":  "#BA7517",
    "GRABANDO":     "#A32D2D",
    "REPRODUCIENDO":"#3B6D11",
    "DESCONECTADO": "#5F5E5A",
}

# ──────────────────────────────────────────────────────────────────────────────
# Estado compartido (session_state)
# ──────────────────────────────────────────────────────────────────────────────
def init_state():
    defaults = {
        "connected":        False,
        "serial_port":      None,
        "serial_obj":       None,
        "modo":             "DESCONECTADO",
        "nota_actual":      "—",
        "distancia_cm":     0.0,
        "escala_nombre":    "Do Mayor completa",
        "escala_notas":     ESCALAS["Do Mayor completa"],
        "aciertos":         0,
        "intentos":         0,
        "nota_objetivo":    None,
        "historial_notas":  deque(maxlen=40),
        "historial_dist":   deque(maxlen=80),
        "secuencia_notas":  [],
        "log_eventos":      deque(maxlen=50),
        "ultimo_update":    None,
        "bt_thread_running":False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ──────────────────────────────────────────────────────────────────────────────
# Hilo lector de Bluetooth
# ──────────────────────────────────────────────────────────────────────────────
def leer_bluetooth():
    """Lee continuamente del puerto serie y actualiza session_state."""
    ser = st.session_state.serial_obj
    buffer = ""
    while st.session_state.bt_thread_running and ser and ser.is_open:
        try:
            if ser.in_waiting > 0:
                chunk = ser.read(ser.in_waiting).decode("utf-8", errors="ignore")
                buffer += chunk
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    line = line.strip()
                    if line:
                        procesar_mensaje(line)
        except Exception as e:
            st.session_state.log_eventos.appendleft(f"[ERROR] {e}")
            break
        time.sleep(0.03)

def procesar_mensaje(raw: str):
    """Parsea un JSON recibido por BT y actualiza el estado."""
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        # Línea de texto plano (modo piano/theremin sin BT estructurado)
        # Formato: "🎵[LIBRE] Dist: 12.3cm | Nota: Do4 | ████░░..."
        _parsear_texto_plano(raw)
        return

    ts = datetime.now().strftime("%H:%M:%S")

    # ── Nota en tiempo real ──
    if "nota" in data and "distancia" in data:
        nota = data["nota"]
        dist = float(data.get("distancia", 0))
        st.session_state.nota_actual    = nota
        st.session_state.distancia_cm   = dist
        st.session_state.ultimo_update  = ts
        st.session_state.historial_notas.appendleft(nota)
        st.session_state.historial_dist.appendleft(dist)

    # ── Desafío de aprendizaje ──
    if "comando" in data and data["comando"] == "desafio":
        st.session_state.nota_objetivo = data.get("nota")
        st.session_state.modo = "APRENDIZAJE"
        st.session_state.log_eventos.appendleft(f"[{ts}] 🎯 Toca: {data.get('nota')}")

    # ── Estado general ──
    if "estado" in data:
        estado = data["estado"]
        if estado == "aprendizaje_iniciado":
            st.session_state.modo = "APRENDIZAJE"
        elif estado == "modo_libre":
            st.session_state.modo = "LIBRE"
            st.session_state.nota_objetivo = None
        elif estado == "acierto":
            st.session_state.log_eventos.appendleft(f"[{ts}] ✅ ¡Correcto!")
        elif estado == "fallo":
            esperada = data.get("esperada", "?")
            tocada   = data.get("tocada", "?")
            st.session_state.log_eventos.appendleft(f"[{ts}] ❌ Esperaba {esperada}, tocaste {tocada}")
        elif estado == "estadisticas_reseteadas":
            st.session_state.aciertos = 0
            st.session_state.intentos = 0

    # ── Estadísticas ──
    if "estadisticas" in data:
        stats = data["estadisticas"]
        st.session_state.aciertos = int(stats.get("aciertos", 0))
        st.session_state.intentos = int(stats.get("intentos", 0))

    # ── Secuencia grabada ──
    if "secuencia" in data:
        st.session_state.secuencia_notas = data["secuencia"]
        st.session_state.log_eventos.appendleft(f"[{ts}] 📼 Secuencia: {len(data['secuencia'])} notas")

    # ── Cambio modo ──
    if "modo" in data:
        st.session_state.modo = data["modo"].upper()

def _parsear_texto_plano(line: str):
    """Parsea salida de consola de basico.py / grabacion.py."""
    import re
    # "🎵[LIBRE] Dist: 12.3cm | Nota:  Do4 | ████"
    dist_m = re.search(r"Dist:\s*([\d.]+)cm", line)
    nota_m = re.search(r"Nota:\s*(\S+)", line)
    modo_m = re.search(r"\[(\w+)\]", line)

    if dist_m:
        st.session_state.distancia_cm = float(dist_m.group(1))
        st.session_state.historial_dist.appendleft(st.session_state.distancia_cm)
    if nota_m:
        nota = nota_m.group(1).strip()
        if nota in NOTAS_HZ:
            st.session_state.nota_actual = nota
            st.session_state.historial_notas.appendleft(nota)
            st.session_state.ultimo_update = datetime.now().strftime("%H:%M:%S")
    if modo_m:
        raw_modo = modo_m.group(1).upper()
        if raw_modo in MODOS_COLOR:
            st.session_state.modo = raw_modo

# ──────────────────────────────────────────────────────────────────────────────
# Enviar comando JSON
# ──────────────────────────────────────────────────────────────────────────────
def enviar(cmd: dict):
    ser = st.session_state.serial_obj
    if ser and ser.is_open:
        try:
            ser.write((json.dumps(cmd) + "\n").encode("utf-8"))
            ts = datetime.now().strftime("%H:%M:%S")
            st.session_state.log_eventos.appendleft(f"[{ts}] → {json.dumps(cmd)}")
        except Exception as e:
            st.toast(f"Error enviando: {e}", icon="❌")

# ──────────────────────────────────────────────────────────────────────────────
# CSS personalizado
# ──────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Nota grande central */
.nota-grande {
    font-size: 5rem;
    font-weight: 800;
    text-align: center;
    line-height: 1;
    letter-spacing: -2px;
}
.hz-label {
    font-size: 1.1rem;
    text-align: center;
    opacity: 0.6;
    margin-top: -0.3rem;
}
/* Tarjeta de modo */
.modo-badge {
    display: inline-block;
    padding: 0.35rem 1.2rem;
    border-radius: 999px;
    font-size: 0.95rem;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
}
/* Tecla de piano */
.piano-key {
    display: inline-block;
    text-align: center;
    font-size: 0.7rem;
    font-weight: 600;
    border-radius: 0 0 4px 4px;
    cursor: default;
    transition: background 0.15s;
}
/* Barra de distancia */
.dist-bar-outer {
    background: #2d2d2d;
    border-radius: 8px;
    height: 18px;
    width: 100%;
    overflow: hidden;
}
.dist-bar-inner {
    height: 100%;
    border-radius: 8px;
    background: linear-gradient(90deg, #1D9E75, #7C3AED);
    transition: width 0.2s ease;
}
/* Log de eventos */
.log-line {
    font-family: monospace;
    font-size: 0.78rem;
    padding: 2px 0;
    border-bottom: 1px solid rgba(255,255,255,0.05);
}
/* Stat card */
.stat-num {
    font-size: 2.5rem;
    font-weight: 800;
    line-height: 1;
}
.stat-label {
    font-size: 0.8rem;
    opacity: 0.6;
    text-transform: uppercase;
    letter-spacing: 1px;
}
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# SIDEBAR — Conexión y controles
# ──────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎹 Piano Theremin")
    st.markdown("---")

    # ── Detección de puertos ──
    puertos = [p.device for p in serial.tools.list_ports.comports()]
    if not puertos:
        puertos = ["/dev/rfcomm0", "/dev/ttyS0", "COM3", "COM4"]

    puerto_sel = st.selectbox(
        "Puerto Bluetooth",
        puertos,
        help="En Linux: /dev/rfcomm0 tras hacer 'rfcomm bind'. En Windows: COMx"
    )
    baud = st.selectbox("Baudrate", [9600, 115200, 57600], index=0)

    col_c, col_d = st.columns(2)
    with col_c:
        if st.button("🔌 Conectar", use_container_width=True,
                     disabled=st.session_state.connected):
            try:
                ser = serial.Serial(puerto_sel, baud, timeout=1)
                st.session_state.serial_obj       = ser
                st.session_state.serial_port      = puerto_sel
                st.session_state.connected        = True
                st.session_state.modo             = "LIBRE"
                st.session_state.bt_thread_running = True
                t = threading.Thread(target=leer_bluetooth, daemon=True)
                t.start()
                st.session_state.log_eventos.appendleft(
                    f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Conectado a {puerto_sel}"
                )
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

    with col_d:
        if st.button("⏏ Desconectar", use_container_width=True,
                     disabled=not st.session_state.connected):
            st.session_state.bt_thread_running = False
            time.sleep(0.1)
            if st.session_state.serial_obj:
                st.session_state.serial_obj.close()
            st.session_state.connected   = False
            st.session_state.serial_obj  = None
            st.session_state.modo        = "DESCONECTADO"
            st.rerun()

    # Estado de conexión
    if st.session_state.connected:
        st.success(f"✅ {st.session_state.serial_port}")
    else:
        st.warning("⚠️ Sin conexión")

    st.markdown("---")

    # ── Comandos rápidos ──
    st.markdown("### 🎮 Comandos")

    if st.button("▶ Modo Libre",        use_container_width=True): enviar({"comando": "libre"})
    if st.button("📚 Modo Aprendizaje", use_container_width=True): enviar({"comando": "iniciar"})
    if st.button("⏭ Siguiente nota",    use_container_width=True): enviar({"comando": "siguiente"})
    if st.button("📊 Pedir stats",       use_container_width=True): enviar({"comando": "estadisticas"})
    if st.button("🗑 Reset estadísticas",use_container_width=True): enviar({"comando": "reset"})

    st.markdown("---")

    # ── Enviar nota específica ──
    st.markdown("### 🎯 Pedir nota concreta")
    nota_pedir = st.selectbox("Nota", list(NOTAS_HZ.keys()))
    if st.button("Enviar nota", use_container_width=True):
        enviar({"comando": "nota", "nota": nota_pedir})

    st.markdown("---")

    # ── Escala visual ──
    st.markdown("### 🎼 Escala activa")
    escala_sel = st.selectbox("", list(ESCALAS.keys()),
                              index=list(ESCALAS.keys()).index(st.session_state.escala_nombre))
    if escala_sel != st.session_state.escala_nombre:
        st.session_state.escala_nombre = escala_sel
        st.session_state.escala_notas  = ESCALAS[escala_sel]

    st.markdown("---")
    st.markdown("### ⚙️ Refresco")
    refresh_rate = st.slider("Segundos entre refrescos", 0.5, 5.0, 1.0, 0.5)

# ──────────────────────────────────────────────────────────────────────────────
# MAIN — Dashboard
# ──────────────────────────────────────────────────────────────────────────────

# ── Fila 1: Modo + Nota actual + Distancia ──────────────────────────────────
col_modo, col_nota, col_dist = st.columns([1.4, 2, 1.6])

with col_modo:
    modo   = st.session_state.modo
    color  = MODOS_COLOR.get(modo, "#888")
    st.markdown(f"""
    <div style="background:{color}22;border:2px solid {color};border-radius:12px;padding:1rem 1.2rem;margin-bottom:0.5rem">
        <div style="font-size:0.75rem;opacity:0.7;text-transform:uppercase;letter-spacing:1px">Modo actual</div>
        <div style="font-size:1.8rem;font-weight:800;color:{color};margin-top:0.2rem">{modo}</div>
    </div>
    """, unsafe_allow_html=True)

    # Nota objetivo (aprendizaje)
    if st.session_state.nota_objetivo:
        obj = st.session_state.nota_objetivo
        hz  = NOTAS_HZ.get(obj, 0)
        st.markdown(f"""
        <div style="background:#BA751722;border:2px solid #BA7517;border-radius:12px;padding:0.8rem 1.2rem">
            <div style="font-size:0.7rem;opacity:0.7;text-transform:uppercase;letter-spacing:1px">🎯 Objetivo</div>
            <div style="font-size:2.2rem;font-weight:800;color:#BA7517">{obj}</div>
            <div style="font-size:0.8rem;opacity:0.6">{hz:.1f} Hz</div>
        </div>
        """, unsafe_allow_html=True)

with col_nota:
    nota = st.session_state.nota_actual
    hz   = NOTAS_HZ.get(nota, 0)

    # Color según si acierta o no
    if st.session_state.nota_objetivo and nota != "—":
        nota_color = "#4ADE80" if nota == st.session_state.nota_objetivo else "#F87171"
    else:
        nota_color = "#C4B5FD"

    st.markdown(f"""
    <div style="text-align:center;padding:0.5rem 0">
        <div style="font-size:0.8rem;opacity:0.5;text-transform:uppercase;letter-spacing:2px;margin-bottom:0.3rem">Nota en directo</div>
        <div style="font-size:5.5rem;font-weight:900;color:{nota_color};line-height:1;letter-spacing:-3px">{nota}</div>
        <div style="font-size:1rem;opacity:0.5;margin-top:0.2rem">{"%.2f Hz" % hz if hz else ""}</div>
    </div>
    """, unsafe_allow_html=True)

with col_dist:
    dist     = st.session_state.distancia_cm
    dist_max = 40.0
    pct      = min(dist / dist_max, 1.0) * 100 if dist > 0 else 0
    ts       = st.session_state.ultimo_update or "—"

    st.markdown(f"""
    <div style="background:#1a1a2e;border-radius:12px;padding:1rem 1.2rem">
        <div style="font-size:0.75rem;opacity:0.7;text-transform:uppercase;letter-spacing:1px">Distancia sensor</div>
        <div style="font-size:2.8rem;font-weight:800;margin:0.2rem 0;line-height:1">{dist:.1f} <span style="font-size:1rem;opacity:0.5">cm</span></div>
        <div class="dist-bar-outer" style="margin:0.5rem 0">
            <div class="dist-bar-inner" style="width:{pct:.1f}%"></div>
        </div>
        <div style="display:flex;justify-content:space-between;font-size:0.7rem;opacity:0.4">
            <span>5 cm</span><span>↔</span><span>40 cm</span>
        </div>
        <div style="font-size:0.7rem;opacity:0.35;margin-top:0.4rem">Último dato: {ts}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ── Fila 2: Teclado visual + Escala activa ───────────────────────────────────
col_piano, col_escala = st.columns([2, 1])

with col_piano:
    st.markdown("#### 🎹 Teclado visual")

    escala_notas = st.session_state.escala_notas
    nota_actual  = st.session_state.nota_actual

    # Generamos HTML del teclado con las notas de la escala activa
    keys_html = '<div style="display:flex;gap:4px;flex-wrap:wrap;padding:0.5rem 0">'
    for i, n in enumerate(escala_notas):
        is_sharp = "#" in n
        is_active = (n == nota_actual)
        # Color según posición en escala (gradiente morado-verde)
        ratio    = i / max(len(escala_notas) - 1, 1)
        r_bg     = int(28  + ratio * (29  - 28))
        g_bg     = int(26  + ratio * (158 - 26))
        b_bg     = int(105 + ratio * (117 - 105))

        if is_active:
            bg = "#F5C518"
            text_col = "#1a1040"
            border = "3px solid #F5C518"
            shadow = "0 0 12px #F5C51888"
        elif is_sharp:
            bg = "#1a1040"
            text_col = "#9980fa"
            border = "1px solid #3d2b8a"
            shadow = "none"
        else:
            bg = f"rgb({r_bg},{g_bg},{b_bg})33"
            text_col = f"rgb({r_bg+80},{g_bg+80},{b_bg+80})"
            border = f"1px solid rgb({r_bg},{g_bg},{b_bg})88"
            shadow = "none"

        hz_n = NOTAS_HZ.get(n, 0)
        keys_html += f"""
        <div style="
            background:{bg};border:{border};border-radius:8px;
            padding:0.5rem 0.3rem;min-width:52px;text-align:center;
            box-shadow:{shadow};transition:all 0.15s;flex:1;max-width:72px
        ">
            <div style="font-size:0.85rem;font-weight:700;color:{text_col}">{n}</div>
            <div style="font-size:0.62rem;color:{text_col};opacity:0.6">{hz_n:.0f}Hz</div>
        </div>"""

    keys_html += "</div>"
    st.markdown(keys_html, unsafe_allow_html=True)

with col_escala:
    st.markdown("#### 🎼 Escala activa")
    total = len(escala_notas)
    nota_idx = escala_notas.index(nota_actual) if nota_actual in escala_notas else -1

    for i, n in enumerate(escala_notas):
        is_current = (i == nota_idx)
        ratio = i / max(total - 1, 1)
        r = int(124 + ratio * (-95))
        g = int(58  + ratio * (100))
        b = int(237 + ratio * (-120))
        bar_w = int(ratio * 80) + 20

        if is_current:
            bg     = "#F5C518"
            tc     = "#1a1040"
            weight = "font-weight:800"
        else:
            bg     = f"rgba({r},{g},{b},0.2)"
            tc     = f"rgba({r+80},{g+80},{b+80},0.9)"
            weight = "font-weight:400"

        hz_n = NOTAS_HZ.get(n, 0)
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:8px;margin:3px 0">
            <div style="background:{bg};color:{tc};{weight};
                border-radius:6px;padding:2px 8px;min-width:56px;font-size:0.82rem;
                text-align:center">{n}</div>
            <div style="background:{bg};height:8px;width:{bar_w}px;border-radius:4px;opacity:0.7"></div>
            <div style="font-size:0.7rem;opacity:0.4">{hz_n:.0f}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# ── Fila 3: Historial de notas + Stats + Secuencia ───────────────────────────
col_hist, col_stats, col_seq = st.columns([2, 1, 1.5])

with col_hist:
    st.markdown("#### 📈 Últimas notas tocadas")
    hist = list(st.session_state.historial_notas)
    if hist:
        hist_html = '<div style="display:flex;flex-wrap:wrap;gap:5px;padding:0.3rem 0">'
        for i, n in enumerate(hist[:30]):
            opacity = max(0.2, 1 - i * 0.04)
            is_cur  = (i == 0)
            bg = "#F5C518" if is_cur else f"rgba(124,58,237,{opacity*0.3:.2f})"
            tc = "#1a1040" if is_cur else f"rgba(200,185,255,{opacity:.2f})"
            sz = "0.85rem" if is_cur else "0.75rem"
            hist_html += f'<span style="background:{bg};color:{tc};border-radius:6px;padding:2px 7px;font-size:{sz};font-weight:{"700" if is_cur else "400"}">{n}</span>'
        hist_html += "</div>"
        st.markdown(hist_html, unsafe_allow_html=True)

        # Mini gráfico de distancia (sparkline ASCII-style)
        dist_hist = list(st.session_state.historial_dist)[:30]
        if len(dist_hist) > 3:
            dist_min, dist_max_ = min(dist_hist), max(dist_hist)
            rng = dist_max_ - dist_min if dist_max_ != dist_min else 1
            bars = "▁▂▃▄▅▆▇█"
            spark = ""
            for d in reversed(dist_hist[:20]):
                idx = int((d - dist_min) / rng * 7)
                spark += bars[idx]
            st.markdown(f"""
            <div style="font-family:monospace;font-size:1.1rem;
                color:#7C3AED;opacity:0.7;letter-spacing:2px;margin-top:0.5rem">
                {spark}
            </div>
            <div style="font-size:0.7rem;opacity:0.35">Historial de distancia (más reciente →)</div>
            """, unsafe_allow_html=True)
    else:
        st.caption("Sin datos aún")

with col_stats:
    st.markdown("#### 🏆 Estadísticas")
    aciertos = st.session_state.aciertos
    intentos = st.session_state.intentos
    pct = (aciertos / intentos * 100) if intentos > 0 else 0

    st.markdown(f"""
    <div style="text-align:center;margin-bottom:0.8rem">
        <div class="stat-num" style="color:#4ADE80">{aciertos}</div>
        <div class="stat-label">Aciertos</div>
    </div>
    <div style="text-align:center;margin-bottom:0.8rem">
        <div class="stat-num" style="color:#C4B5FD">{intentos}</div>
        <div class="stat-label">Intentos</div>
    </div>
    <div style="text-align:center">
        <div class="stat-num" style="color:#F5C518">{pct:.0f}<span style="font-size:1.2rem">%</span></div>
        <div class="stat-label">Precisión</div>
    </div>
    """, unsafe_allow_html=True)

    if intentos > 0:
        st.progress(pct / 100)

with col_seq:
    st.markdown("#### 📼 Secuencia grabada")
    seq = st.session_state.secuencia_notas
    if seq:
        seq_html = '<div style="display:flex;flex-wrap:wrap;gap:4px">'
        for i, (n, dur) in enumerate(seq):
            seq_html += f'<div style="background:rgba(163,45,45,0.25);border:1px solid #A32D2D44;border-radius:6px;padding:2px 6px;font-size:0.75rem;text-align:center"><div style="font-weight:700;color:#F87171">{n}</div><div style="opacity:0.5;font-size:0.6rem">{dur:.1f}s</div></div>'
        seq_html += "</div>"
        st.markdown(seq_html, unsafe_allow_html=True)
        st.caption(f"Total: {len(seq)} notas")
    else:
        st.caption("Sin secuencia grabada")

st.markdown("---")

# ── Fila 4: Log de eventos ─────────────────────────────────────────────────
st.markdown("#### 🖥 Log de eventos")
log = list(st.session_state.log_eventos)
if log:
    log_html = '<div style="background:#0d0d1a;border-radius:8px;padding:0.8rem;max-height:160px;overflow-y:auto;font-family:monospace">'
    for line in log[:20]:
        icon_color = "#4ADE80" if "✅" in line else "#F87171" if "❌" in line else "#C4B5FD" if "→" in line else "#85B7EB"
        log_html += f'<div style="font-size:0.78rem;color:{icon_color};padding:1px 0;border-bottom:1px solid rgba(255,255,255,0.04)">{line}</div>'
    log_html += "</div>"
    st.markdown(log_html, unsafe_allow_html=True)
else:
    st.caption("Sin eventos registrados aún")

# ──────────────────────────────────────────────────────────────────────────────
# Auto-refresco
# ──────────────────────────────────────────────────────────────────────────────
if st.session_state.connected:
    time.sleep(refresh_rate)
    st.rerun()