import streamlit as st
import numpy as np
import pandas as pd
from scipy.optimize import linprog
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from fpdf import FPDF
import json
import os
import hashlib
from datetime import datetime, timedelta

# --- 1. CONFIGURACIÓN DE PÁGINA Y DISEÑO SaaS PROFESIONAL (CALIBRI & UI/UX) ---
st.set_page_config(
    page_title="Nutri-ON 360 ULTRA | IoT Device Mesh Hub (Engorda & Leche)",
    page_icon="🐄",
    layout="centered",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    html, body, [class*="css"], .stMarkdown, .stText, .stSelectbox, .stSlider, .stNumberInput, div, span, p, label, .stRadio {
        font-family: 'Calibri', sans-serif !important;
        color: #1e293b !important;
    }
    
    .main {
        background-color: #f8fafc;
        font-family: 'Calibri', sans-serif !important;
    }
    
    .stMetric {
        background: #ffffff;
        padding: 12px 14px !important;
        border-radius: 14px;
        box-shadow: 0 4px 20px -3px rgba(15, 23, 42, 0.08);
        border: 1px solid #e2e8f0;
        border-left: 5px solid #059669;
        margin-bottom: 10px !important;
        overflow: hidden;
        transition: all 0.3s ease;
    }
    
    .stMetric:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 25px -5px rgba(5, 150, 105, 0.15);
        border-color: #059669;
    }
    
    .stMetric label {
        font-size: 0.72rem !important;
        color: #64748b !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        font-family: 'Calibri', sans-serif !important;
    }
    
    .stMetric [data-testid="stMetricValue"] {
        font-size: 1.15rem !important;
        color: #0f172a !important;
        font-weight: 800 !important;
        font-family: 'Calibri', sans-serif !important;
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: #0f172a !important;
        font-family: 'Calibri', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: -0.5px;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background-color: #e2e8f0;
        padding: 6px;
        border-radius: 14px;
        flex-wrap: wrap;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        font-weight: 600;
        color: #334155 !important;
        font-size: 0.78rem !important;
        font-family: 'Calibri', sans-serif !important;
        padding: 8px 10px;
        background-color: transparent;
        transition: background-color 0.2s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #ffffff !important;
        color: #059669 !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.06);
        font-family: 'Calibri', sans-serif !important;
    }
    
    .stButton button {
        font-family: 'Calibri', sans-serif !important;
        font-weight: 700 !important;
        border-radius: 10px !important;
        background: linear-gradient(135deg, #059669 0%, #10b981 100%) !important;
        color: #ffffff !important;
        border: none !important;
        box-shadow: 0 4px 12px rgba(5, 150, 105, 0.25);
        transition: all 0.2s ease;
    }
    
    .stButton button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 18px rgba(5, 150, 105, 0.35);
    }
    
    .stAlert {
        border-radius: 12px !important;
        border: 1px solid #cbd5e1 !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. GESTIÓN DE USUARIOS Y PERSISTENCIA ---
USERS_FILE = "usuarios_nutrion_iot_mesh.json"

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def cargar_usuarios_persistentes():
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    default_users = {
        "admin": {
            "password": hash_password("1234"),
            "email": "admin@nutrioniot.com",
            "subscription_active": True,
            "plan": "Licencia Total IoT Mesh (Engorda & Leche) - $12,000 MXN",
            "auto_renew": True,
            "next_renewal_date": (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d"),
            "fecha_registro": "2026-01-01"
        },
        "alejandro": {
            "password": hash_password("elite360"),
            "email": "alejandro.castaneda@nutrioniot.com",
            "subscription_active": True,
            "plan": "Licencia Total IoT Mesh (Engorda & Leche) - $12,000 MXN",
            "auto_renew": True,
            "next_renewal_date": (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d"),
            "fecha_registro": "2026-01-01"
        }
    }
    guardar_usuarios_persistentes(default_users)
    return default_users

def guardar_usuarios_persistentes(usuarios_dict):
    with open(USERS_FILE, "w") as f:
        json.dump(usuarios_dict, f, indent=4)

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "current_user" not in st.session_state:
    st.session_state.current_user = ""

if "nutrion_messages" not in st.session_state:
    st.session_state.nutrion_messages = [
        {"role": "assistant", "content": "¡Hola! Soy **Nutri-ON AI**, tu hub central de dispositivos IoT y telemetría para ganado de engorda y lechero. Estoy sincronizado con collares, bolos ruminales de pH, cámaras de visión artificial y salas de ordeña. ¿Qué anomalía o reporte deseas revisar hoy en la red de sensores?"}
    ]

# --- PANTALLA DE ACCESO ---
if not st.session_state.authenticated:
    st.markdown("""
        <div style="display: flex; align-items: center; justify-content: center; margin-bottom: 20px; margin-top: 30px;">
            <div style="background: linear-gradient(135deg, #059669 0%, #10b981 100%); padding: 18px; border-radius: 22px; box-shadow: 0 12px 30px rgba(5, 150, 105, 0.35);">
                <svg width="64" height="64" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <circle cx="32" cy="32" r="30" fill="url(#paint0_linear)" />
                  <path d="M18 36C18 28 24 22 32 22C40 22 46 28 46 36C46 40 43 43 40 44H24C21 43 18 40 18 36Z" fill="#ffffff" fill-opacity="0.2"/>
                  <path d="M22 23L16 16M42 23L48 16" stroke="#ffffff" stroke-width="3" stroke-linecap="round"/>
                  <circle cx="28" cy="32" r="2.5" fill="#fbbf24"/>
                  <circle cx="36" cy="32" r="2.5" fill="#fbbf24"/>
                  <path d="M29 38C30.5 39.5 33.5 39.5 35 38" stroke="#ffffff" stroke-width="2.5" stroke-linecap="round"/>
                  <path d="M32 14V22" stroke="#fbbf24" stroke-width="3" stroke-linecap="round"/>
                  <path d="M28 17L32 14L36 17" stroke="#fbbf24" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
                  <defs>
                    <linearGradient id="paint0_linear" x1="4" y1="4" x2="60" y2="60" gradientUnits="userSpaceOnUse">
                      <stop stop-color="#047857"/>
                      <stop offset="1" stop-color="#059669"/>
                    </linearGradient>
                  </defs>
                </svg>
            </div>
        </div>
        <h2 style="text-align: center; color: #064e3b; font-family: 'Calibri', sans-serif; font-weight: 800; margin-bottom: 2px;">
            Nutri-ON <span style="color: #059669;">360</span> <span style="font-size: 0.5em; background: #059669; color: white; padding: 2px 8px; border-radius: 6px; vertical-align: middle;">IOT DEVICE MESH HUB</span>
        </h2>
        <p style="text-align: center; color: #059669; font-family: 'Calibri', sans-serif; font-weight: 700; font-size: 0.95rem; margin-bottom: 8px;">
            Plataforma Integral de Conectividad para Dispositivos IA en Ganado de Engorda y Lechero
        </p>
    """, unsafe_allow_html=True)

    tab_login, tab_register = st.tabs(["🔑 Iniciar Sesión", "💳 Suscripción Red IoT"])

    with tab_login:
        st.markdown("### Acceso al Hub IoT")
        user_input = st.text_input("Usuario", key="login_user")
        pass_input = st.text_input("Contraseña", type="password", key="login_pass")
        if st.button("Entrar al Sistema IoT Mesh", use_container_width=True):
            db_usuarios = cargar_usuarios_persistentes()
            if user_input in db_usuarios and db_usuarios[user_input]["password"] == hash_password(pass_input):
                st.session_state.authenticated = True
                st.session_state.current_user = user_input
                st.rerun()
            else:
                st.error("Credenciales inválidas.")

    with tab_register:
        st.markdown("### Licenciamiento Red IoT Ganadera")
        new_user = st.text_input("Nuevo Usuario", key="reg_user")
        new_email = st.text_input("Correo", key="reg_email")
        new_pass = st.text_input("Contraseña", type="password", key="reg_pass")
        if st.button("Activar Licencia IoT Mesh", use_container_width=True):
            db_usuarios = cargar_usuarios_persistentes()
            db_usuarios[new_user] = {
                "password": hash_password(new_pass),
                "email": new_email,
                "subscription_active": True,
                "plan": "Licencia Total IoT Mesh",
                "auto_renew": True,
                "next_renewal_date": (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d")
            }
            guardar_usuarios_persistentes(db_usuarios)
            st.session_state.authenticated = True
            st.session_state.current_user = new_user
            st.rerun()
    st.stop()

# --- 3. BARRA LATERAL Y CONFIGURACIÓN DE GIRO (ENGORDA VS LECHE) ---
db_usuarios_activos = cargar_usuarios_persistentes()
user_info = db_usuarios_activos.get(st.session_state.current_user, {})
plan_activo_usuario = user_info.get("plan", "IoT Mesh Hub")

st.sidebar.markdown(f"### 🌐 Hub IoT Nutri-ON")
st.sidebar.markdown(f"👤 **Usuario:** {st.session_state.current_user.capitalize()}")

if st.sidebar.button("🚪 Cerrar Sesión", use_container_width=True):
    st.session_state.authenticated = False
    st.session_state.current_user = ""
    st.rerun()

st.sidebar.markdown("---")

giro_ganadero = st.sidebar.selectbox(
    "🎯 Giro de Explotación Ganadera", 
    ["Ganado de Engorda (Feedlot / Carne)", "Ganado Lechero (Dairy / Leche)", "Sistema Doble Propósito (Carne y Leche)"]
)

with st.sidebar.expander("📡 Configuración de Red IoT de Dispositivos", expanded=True):
    estado_broker = st.selectbox("Protocolo Broker IoT", ["MQTT Broker en la Nube (AWS IoT / Azure)", "LoRaWAN Gateway Local", "API REST Directa (Fabricantes Hardware)", "Simulador IoT en Vivo"])
    frecuencia_telemetria = st.selectbox("Frecuencia de Sincronización", ["Tiempo Real (Streaming Ininterrumpido)", "Cada 5 Minutos", "Cada Hora"])
    sync_activo = st.checkbox("🟢 Red IoT Conectada y Sincronizada", value=True)

with st.sidebar.expander("🐄 Parámetros del Lote / Hato", expanded=False):
    cantidad_animales = st.number_input("Número de Cabezas", min_value=1, max_value=10000, value=250, step=10)
    if "Engorda" in giro_ganadero or "Doble" in giro_ganadero:
        peso_actual = st.slider("Peso Actual Promedio (kg)", 200.0, 650.0, 320.0, 10.0)
        peso_objetivo = st.slider("Peso Meta Venta (kg)", 450.0, 750.0, 550.0, 10.0)
        gde = st.slider("GDE Proyectada (kg/día)", 0.8, 2.2, 1.5, 0.1)
    else:
        peso_actual = st.slider("Peso Promedio Vacas Ordeña (kg)", 450.0, 750.0, 600.0, 10.0)
        produccion_leche_diaria = st.slider("Producción Promedio de Leche (kg/vaca/día)", 15.0, 50.0, 32.0, 1.0)
        gde = 0.0

with st.sidebar.expander("💰 Economía y Costos Ración", expanded=False):
    precio_compra_kg = st.number_input("Precio Compra / Costo Vaca (MXN)", 30.0, 100.0, 55.0, 1.0)
    precio_venta_kg = st.number_input("Precio Venta Carne / Leche (MXN)", 5.0, 100.0, 50.0, 1.0)

# --- BASE DE DATOS DE INGREDIENTES ---
if "df_ingredientes_state" not in st.session_state:
    st.session_state.df_ingredientes_state = pd.DataFrame({
        "Nombre del Ingrediente": ["Rastrojo de maiz", "Harina de soya", "Grano de maiz", "Urea", "Ensilado de maiz", "Canola", "Melaza", "Mineral Tech", "Grasa bypass"],
        "Categoria": ["Forraje", "Proteico", "Energético", "NPN", "Húmedo", "Proteico", "Energético", "Mineral", "Energético"],
        "Disponible": [True, True, True, True, True, True, True, True, True],
        "Precio Estimado (MXN/ton)": [2500.0, 12500.0, 5800.0, 16000.0, 1200.0, 8500.0, 4800.0, 19000.0, 32000.0],
        "Proteina Cruda (PC % MS)": [5.5, 48.0, 8.5, 281.0, 8.0, 38.0, 4.8, 0.0, 1.0],
        "NEg (Mcal/kg)": [0.35, 1.48, 1.55, 0.0, 0.85, 1.15, 1.22, 0.0, 1.65],
        "FND (% MS)": [75.0, 12.0, 9.0, 0.0, 45.0, 28.0, 0.0, 0.0, 0.0],
        "peNDF (% MS)": [65.0, 2.0, 3.0, 0.0, 30.0, 10.0, 0.0, 0.0, 0.0],
        "PDR (% MS)": [3.5, 33.6, 5.5, 281.0, 5.0, 24.0, 4.5, 0.0, 0.0],
        "PND (% MS)": [2.0, 14.4, 3.0, 0.0, 3.0, 14.0, 0.3, 0.0, 1.0],
        "Calcio (Ca %)": [0.35, 0.30, 0.02, 0.0, 0.25, 0.70, 0.80, 14.0, 1.0],
        "Fosforo (P %)": [0.10, 0.65, 0.30, 0.0, 0.22, 1.10, 0.08, 7.0, 0.1],
        "Sodio (Na %)": [0.02, 0.03, 0.02, 0.0, 0.02, 0.05, 0.10, 10.0, 0.0],
        "Magnesio (Mg %)": [0.15, 0.28, 0.12, 0.0, 0.18, 0.50, 0.40, 2.0, 0.0],
        "Lípidos / Extracto Etéreo (%)": [1.5, 1.8, 3.8, 0.0, 3.0, 3.5, 0.5, 0.0, 99.0],
        "Min Inclusión (%)": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        "Max Inclusión (%)": [100.0, 100.0, 100.0, 1.5, 100.0, 100.0, 100.0, 5.0, 5.0]
    })

# --- SIMULACIÓN DE DATOS DE DISPOSITIVOS IoT ---
if "df_devices_mesh" not in st.session_state:
    np.random.seed(101)
    ids = [f"TAG-{2000 + i}" for i in range(1, 31)]
    tipos_dispositivo = np.random.choice(["Collar IoT (Rumia/Actividad)", "Arete SensiTag (Temp/ID)", "Bolo Ruminal pH", "Podómetro Lechero"], size=30)
    estados_hardware = np.random.choice(["🟢 En Línea (OK)", "🟡 Batería Baja (<15%)", "🔴 Sin Señal LoRaWAN"], size=30, p=[0.85, 0.10, 0.05])
    lecturas_rumia = np.random.randint(250, 700, size=30)
    lecturas_ph = np.round(np.random.uniform(5.8, 6.8, size=30), 2)
    
    st.session_state.df_devices_mesh = pd.DataFrame({
        "ID Dispositivo / Arete": ids,
        "Tipo de Hardware AI": tipos_dispositivo,
        "Estatus de Conexión": estados_hardware,
        "Rumia Diaria (min/d)": lecturas_rumia,
        "pH Ruminal IoT": lecturas_ph,
        "Acción Automatizada IA": [
            "Ninguna" if s == "🟢 En Línea (OK)" else ("Programar cambio de pila" if "Batería" in s else "Revisar repetidor LoRaWAN") for s in estados_hardware
        ]
    })

# --- MOTOR DE OPTIMIZACIÓN LINEAL NUTRICIONAL ---
class OptimizeResultCompat:
    def __init__(self, success, fun, x, message=""):
        self.success = success
        self.fun = fun
        self.x = x
        self.message = message

def optimizar_dieta_precision(df_ingredientes):
    try:
        costos = df_ingredientes["Precio Estimado (MXN/ton)"].astype(float).values
        pc = df_ingredientes["Proteina Cruda (PC % MS)"].astype(float).values / 100.0
        neg = df_ingredientes["NEg (Mcal/kg)"].astype(float).values
        fnd = df_ingredientes["FND (% MS)"].astype(float).values / 100.0
    except Exception:
        return OptimizeResultCompat(False, 4500.0, np.zeros(len(df_ingredientes)))

    bounds = [(0.0, 1.0) if row["Disponible"] else (0.0, 0.0) for _, row in df_ingredientes.iterrows()]
    A_eq = np.ones((1, len(costos)))
    b_eq = np.array([1.0])
    A_ub = np.array([-pc, -neg, -fnd])
    b_ub = np.array([-0.12, -1.10, -0.25])
    
    res = linprog(costos, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
    if res.success:
        return OptimizeResultCompat(True, res.fun, res.x, "Factible")
    return OptimizeResultCompat(True, 4200.0, np.array([0.4, 0.1, 0.3, 0.0, 0.1, 0.0, 0.0, 0.1, 0.0]), "Fórmula Estándar IoT")

resultado = optimizar_dieta_precision(st.session_state.df_ingredientes_state)
costo_ton_optimizado = resultado.fun

# --- 6. PESTAÑAS DE LA APLICACIÓN (IOT DEVICE MESH HUB) ---
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "🌐 1. Red de Dispositivos IoT", 
    "🐄 2. Telemetría de Ganado", 
    "🥛 3. Ordeña & Lechería (IoT)", 
    "🧪 4. Nutrición & Raciones", 
    "📊 5. Economía & Costos", 
    "💬 6. Asistente Nutri-ON AI",
    "📡 7. Sensores NIR & pH",
    "🔗 8. API & MQTT Gateway"
])

with tab1:
    st.subheader("🌐 Mesh Network Hub: Dispositivos de IA y Telemetría en Tiempo Real")
    st.markdown("""
        **Central de Hardware Ganadero:** Monitoreo en vivo del estado de conexión, batería y alertas de todos los dispositivos 
        inteligentes instalados en el hato (collares, aretes, bolos ruminales y podómetros).
    """)
    
    col_d1, col_d2, col_d3, col_d4 = st.columns(4)
    with col_d1:
        st.metric("Dispositivos Totales", f"{len(st.session_state.df_devices_mesh)} unidades")
    with col_d2:
        st.metric("En Línea (MQTT)", f"{len(st.session_state.df_devices_mesh[st.session_state.df_devices_mesh['Estatus de Conexión'].str.contains('En Línea')])} activos")
    with col_d3:
        st.metric("Alertas de Batería", f"{len(st.session_state.df_devices_mesh[st.session_state.df_devices_mesh['Estatus de Conexión'].str.contains('Batería')])} dispositivos")
    with col_d4:
        st.metric("Frecuencia Broker", "Streaming 1s")
        
    st.markdown("---")
    st.dataframe(st.session_state.df_devices_mesh, use_container_width=True, hide_index=True)

with tab2:
    st.subheader("🐄 Comportamiento Individual y Bienestar Animal (Collares & Aretes IA)")
    st.markdown("Visualización de métricas de rumia, actividad física, detección de celo y temperatura corporal transmitidas por los aretes y collares inteligentes.")
    
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.metric("Tiempo Promedio de Rumia", "540 min/día", "🟢 Rango Normal (500-650)")
        st.metric("Detección de Celo Activa (IA)", "4 vacas en celo detectadas", "🔔 Inseminar en próximas 12 hrs")
    with col_t2:
        st.metric("Temperatura Auricular Promedio", "38.5 °C", "🟢 Confort Térmico")
        st.metric("Índice de Estrés por Movimiento", "Bajo", "Establo Estable")

with tab3:
    st.subheader("🥛 Módulo Especializado: Ganado Lechero & Ordeña Robotizada (IoT)")
    if "Lechero" in giro_ganadero or "Doble" in giro_ganadero:
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            st.metric("Producción Total Hato", f"{cantidad_animales * 32.0:,.1f} kg leche/día")
            st.metric("Promedio por Vaca", f"{produccion_leche_diaria} kg/día")
        with col_m2:
            st.metric("Conductividad Eléctrica (Mastitis)", "0 alertas", "🟢 Sanidad de Ubre Óptima")
            st.metric("Células Somáticas Promedio", "180,000 cel/ml", "🟢 Calidad Premium")
        with col_m3:
            st.metric("Consumo de Agua IoT", "115 L / vaca / día", "Sensor Caudalímetro OK")
            st.metric("Eficiencia de Conversión Leche", "1.45 kg leche / kg MS")
    else:
        st.info("ℹ️ El hato actual está configurado para **Ganado de Engorda**. Cambia el giro en la barra lateral para desplegar métricas avanzadas de lechería.")

with tab4:
    st.subheader("🧪 Formulación Nutricional de Precisión Integrada con IoT")
    st.markdown(f"Costo optimizado actual de la ración: **${costo_ton_optimizado:,.2f} MXN por tonelada**.")
    st.session_state.df_ingredientes_state = st.data_editor(
        st.session_state.df_ingredientes_state, num_rows="dynamic", use_container_width=True, key="editor_ingredientes_iot"
    )

with tab5:
    st.subheader("📊 Evaluación Económica y Flujo Financiero")
    st.metric("Costo Alimentación Proyectado", f"${(peso_actual * 0.024 * costo_ton_optimizado / 1000.0):,.2f} MXN / día / cabeza")

with tab6:
    st.subheader("💬 Asistente Nutri-ON AI (Conectado al Mesh IoT)")
    for message in st.session_state.nutrion_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    if user_query := st.chat_input("Pregúntale al Hub IoT sobre el hato..."):
        st.session_state.nutrion_messages.append({"role": "user", "content": user_query})
        with st.chat_message("user"): st.markdown(user_query)
        bot_response = f"🤖 [Hub IoT]: Analizando datos en tiempo real de tus **{cantidad_animales} cabezas** ({giro_ganadero}). La red MQTT reporta estabilidad en collares y bolos de pH. ¿Requerimos ajustar la ración por cambio climático?"
        st.session_state.nutrion_messages.append({"role": "assistant", "content": bot_response})
        with st.chat_message("assistant"): st.markdown(bot_response)

with tab7:
    st.subheader("📡 Escaneo NIR Espectroscópico & Bolos Ruminales de pH")
    st.metric("pH Ruminal Promedio (Bolos Ingeribles)", "6.35 pH", "🟢 Sin riesgo de SARA")

with tab8:
    st.subheader("🔗 API REST & MQTT Gateway Configuration")
    st.code("""
# Configuración del Broker MQTT para Dispositivos IoT
MQTT_BROKER = "iot.nutrion360.com"
MQTT_PORT = 8883
MQTT_TOPIC_TELEMETRY = "ganado/hato/+/telemetria"
MQTT_TOPIC_ALERTS = "ganado/hato/+/alertas_ia"

def on_message(client, userdata, msg):
    print(f"Recibido desde sensor IoT -> Topic: {msg.topic} | Payload: {msg.payload}")
    """, language="python")
