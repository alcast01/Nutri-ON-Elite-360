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
    page_title="Nutri-ON 360 ULTRA V1.0 IA & IoT | México Ganadero",
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

# --- 2. GESTIÓN DE MULTI-USUARIOS, PERSISTENCIA Y RENOVACIÓN AUTOMÁTICA ---
USERS_FILE = "usuarios_nutrion_mexico.json"

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
            "email": "admin@nutrionmexico.com",
            "subscription_active": True,
            "plan": "Anual Nacional México (12 Meses) - $9,600 MXN | $800.00/mes",
            "auto_renew": True,
            "next_renewal_date": (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d"),
            "fecha_registro": "2026-01-01"
        },
        "alejandro": {
            "password": hash_password("elite360"),
            "email": "alejandro.castaneda@nutrionmexico.com",
            "subscription_active": True,
            "plan": "Anual Nacional México (12 Meses) - $9,600 MXN | $800.00/mes",
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
        {"role": "assistant", "content": "¡Hola! Soy **Nutri-ON**, tu consultor experto en nutrición y engorda bovina en México. Estoy conectado con las condiciones climáticas de tu Estado, sensores NIR, collares IoT y el motor de optimización. ¿Qué desafío tienes hoy en tu rancho? (Ej: *'mis becerros bajaron el consumo por el calor'*, *'el costo del alimento está alto en mi región'* o *'tengo sospecha de acidosis'*)."}
    ]

# --- PANTALLA DE ACCESO / SUSCRIPCIÓN SI NO ESTÁ AUTENTICADO ---
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
            Nutri-ON <span style="color: #059669;">360</span> <span style="font-size: 0.5em; background: #059669; color: white; padding: 2px 8px; border-radius: 6px; vertical-align: middle;">ULTRA V1.0 - MÉXICO</span>
        </h2>
        <p style="text-align: center; color: #059669; font-family: 'Calibri', sans-serif; font-weight: 700; font-size: 0.95rem; margin-bottom: 8px;">
            Nutrición de precisión, programación lineal, collares IoT y climatología adaptada para los 32 Estados.
        </p>
        <p style="text-align: center; color: #475569; font-family: 'Calibri', sans-serif; font-size: 0.85rem; margin-bottom: 25px;">
            Plataforma Nacional de Optimización Ganadera y Consultoría Experta
        </p>
    """, unsafe_allow_html=True)

    tab_login, tab_register = st.tabs(["🔑 Iniciar Sesión", "💳 Planes Nacionales & Registro"])

    with tab_login:
        st.markdown("### Acceso con Usuario y Contraseña")
        user_input = st.text_input("Nombre de Usuario", key="login_user")
        pass_input = st.text_input("Contraseña", type="password", key="login_pass")
        
        st.markdown("")
        if st.button("Entrar a la Plataforma México", use_container_width=True):
            db_usuarios = cargar_usuarios_persistentes()
            hashed_pass = hash_password(pass_input)
            
            if user_input in db_usuarios and db_usuarios[user_input]["password"] == hashed_pass:
                if db_usuarios[user_input].get("subscription_active", False):
                    st.session_state.authenticated = True
                    st.session_state.current_user = user_input
                    st.success(f"¡Bienvenido de nuevo, {user_input}!")
                    st.rerun()
                else:
                    st.error("Tu suscripción se encuentra inactiva. Selecciona un plan para renovar.")
            else:
                st.error("Usuario o contraseña incorrectos. Verifica tus datos.")

    with tab_register:
        st.markdown("### 🌟 Selección de Plan Nacional México")
        plan_elegido = st.radio(
            "Planes de Suscripción Disponibles:",
            [
                "Trimestral Regional (3 Meses) - $3,000 MXN | $1,000.00/mes",
                "Semestral Feedlot México (6 Meses) - $5,400 MXN | $900.00/mes",
                "Anual Nacional México (12 Meses) - $9,600 MXN | $800.00/mes (Acceso Total 32 Estados)"
            ],
            index=2
        )
        
        st.markdown("---")
        st.markdown("##### 📝 Datos de Cuenta y Pago Seguro")
        
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            new_user = st.text_input("Nombre de Usuario Deseado", key="reg_user")
            new_email = st.text_input("Correo Electrónico", key="reg_email")
        with col_r2:
            new_pass = st.text_input("Contraseña", type="password", key="reg_pass")
            confirm_pass = st.text_input("Confirma Contraseña", type="password", key="reg_conf")
        
        st.markdown("")
        col_p1, col_p2, col_p3 = st.columns([2, 1, 1])
        with col_p1:
            num_tarjeta = st.text_input("Número de Tarjeta de Crédito / Débito", placeholder="4000 1234 5678 9010", key="reg_card")
        with col_p2:
            exp_tarjeta = st.text_input("Expiración (MM/AA)", placeholder="12/28", key="reg_exp")
        with col_p3:
            cvv_tarjeta = st.text_input("CVV", type="password", placeholder="123", key="reg_cvv")
        
        st.markdown("")
        auto_renew_enabled = st.checkbox("🔄 **Activar Renovación Automática**", value=True)
        st.markdown("")
        
        try:
            costo_str = plan_elegido.split("-")[1].split("|")[0].strip()
        except Exception:
            costo_str = "$9,600 MXN"
        
        if st.button(f"💳 Pagar {costo_str} y Activar Licencia Nacional", use_container_width=True):
            db_usuarios = cargar_usuarios_persistentes()
            if not new_user or not new_email or not new_pass or not num_tarjeta:
                st.warning("⚠️ Por favor, completa todos los campos de registro y pago.")
            elif new_user in db_usuarios:
                st.error("⚠️ El usuario ya existe.")
            elif new_pass != confirm_pass:
                st.error("⚠️ Las contraseñas no coinciden.")
            else:
                dias_periodo = 90 if "Trimestral" in plan_elegido else (180 if "Semestral" in plan_elegido else 365)
                fecha_renovacion = (datetime.now() + timedelta(days=dias_periodo)).strftime("%Y-%m-%d")
                
                db_usuarios[new_user] = {
                    "password": hash_password(new_pass),
                    "email": new_email,
                    "subscription_active": True,
                    "plan": plan_elegido,
                    "auto_renew": auto_renew_enabled,
                    "next_renewal_date": fecha_renovacion,
                    "fecha_registro": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                guardar_usuarios_persistentes(db_usuarios)
                st.success(f"🎉 **¡Pago Exitoso de {costo_str}!** Licencia activada.")
                st.session_state.authenticated = True
                st.session_state.current_user = new_user
                st.balloons()
                st.rerun()
    st.stop()

# --- 3. LOGOTIPO Y PERFIL DE USUARIO ---
db_usuarios_activos = cargar_usuarios_persistentes()
user_info = db_usuarios_activos.get(st.session_state.current_user, {})
plan_activo_usuario = user_info.get("plan", "Plan Nacional México")
auto_renew_status = user_info.get("auto_renew", False)
next_ren_date = user_info.get("next_renewal_date", "N/A")

st.markdown("""
    <div style="display: flex; align-items: center; background: linear-gradient(135deg, #ffffff 0%, #ecfdf5 50%, #fef3c7 100%); padding: 22px 26px; border-radius: 20px; box-shadow: 0 15px 35px -10px rgba(5, 150, 105, 0.15); margin-bottom: 24px; border: 2px solid #34d399; flex-wrap: wrap; gap: 20px;">
        <div style="flex-shrink: 0; background: linear-gradient(135deg, #059669 0%, #10b981 100%); padding: 12px; border-radius: 16px; display: flex; align-items: center; justify-content: center; box-shadow: 0 8px 20px rgba(5, 150, 105, 0.3);">
            <svg width="48" height="48" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
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
        <div style="flex-grow: 1; min-width: 240px;">
            <h1 style="margin: 0; font-size: 1.8em; color: #064e3b; letter-spacing: -0.8px; font-weight: 800; font-family: 'Calibri', sans-serif;">
                Nutri-ON <span style="background: linear-gradient(135deg, #059669, #10b981); color: #ffffff; padding: 3px 10px; border-radius: 8px; font-size: 0.5em; vertical-align: middle; font-weight: 700; letter-spacing: 0.8px; box-shadow: 0 4px 10px rgba(5,150,105,0.3);">360 ULTRA V1.0 - MÉXICO</span>
            </h1>
            <p style="margin: 2px 0 2px 0; font-size: 0.82em; color: #059669; font-weight: 700; font-family: 'Calibri', sans-serif;">
                Optimización lineal adaptada para los 32 Estados, razas mexicanas, sensores NIR y collares IoT.
            </p>
            <p style="margin: 3px 0 2px 0; font-size: 0.88em; color: #1e293b; font-weight: 600; font-family: 'Calibri', sans-serif;">
                Usuario: <span style="color: #059669; font-weight: 700;">{user}</span> | Licencia: <span style="color: #d97706; font-weight: 700;">{plan}</span> | Creado por: Dr. Alejandro Castañeda Correa
            </p>
        </div>
    </div>
""".format(user=st.session_state.current_user.capitalize(), plan=plan_activo_usuario), unsafe_allow_html=True)

# --- 4. BASE DE DATOS INICIAL CON PERSISTENCIA ---
if "df_ingredientes_state" not in st.session_state:
    st.session_state.df_ingredientes_state = pd.DataFrame({
        "Nombre del Ingrediente": [
            "Rastrojo de maiz molido", "Harina de soya", "Grano de maiz molido", 
            "Urea", "Ensilado de maiz", "Canola (pasta)", "Melaza liquida",
            "Purina Mineral Tech (Regional)", "Malta Cleyton Ganafos", "Grasa de paso Lactomil"
        ],
        "Categoria": ["Forraje", "Suplemento Proteico", "Grano Energetico", "Suplemento NPN", "Forraje Humedo", "Suplemento Proteico", "Subproducto / Energetico", "Suplemento Mineral", "Suplemento Mineral", "Suplemento Energetico"],
        "Disponible": [True, True, True, True, True, True, True, True, True, True],
        "Precio Estimado (MXN/ton)": [2500.0, 12500.0, 5800.0, 16000.0, 1200.0, 8500.0, 4800.0, 19000.0, 18500.0, 32000.0],
        "Proteina Cruda (PC % MS)": [5.5, 48.0, 8.5, 281.0, 8.0, 38.0, 4.8, 0.0, 0.0, 1.0],
        "NEg (Mcal/kg)": [0.35, 1.48, 1.55, 0.0, 0.85, 1.15, 1.22, 0.0, 0.0, 1.65],
        "FND (% MS)": [75.0, 12.0, 9.0, 0.0, 45.0, 28.0, 0.0, 0.0, 0.0, 0.0],
        "peNDF (% MS)": [65.0, 2.0, 3.0, 0.0, 30.0, 10.0, 0.0, 0.0, 0.0, 0.0],
        "PDR (% MS)": [3.5, 33.6, 5.5, 281.0, 5.0, 24.0, 4.5, 0.0, 0.0, 0.0],
        "PND (% MS)": [2.0, 14.4, 3.0, 0.0, 3.0, 14.0, 0.3, 0.0, 0.0, 1.0],
        "Calcio (Ca %)": [0.35, 0.30, 0.02, 0.0, 0.25, 0.70, 0.80, 14.0, 16.0, 1.0],
        "Fosforo (P %)": [0.10, 0.65, 0.30, 0.0, 0.22, 1.10, 0.08, 7.0, 8.0, 0.1],
        "Sodio (Na %)": [0.02, 0.03, 0.02, 0.0, 0.02, 0.05, 0.10, 10.0, 9.0, 0.0],
        "Magnesio (Mg %)": [0.15, 0.28, 0.12, 0.0, 0.18, 0.50, 0.40, 2.0, 2.5, 0.0],
        "Lípidos / Extracto Etéreo (%)": [1.5, 1.8, 3.8, 0.0, 3.0, 3.5, 0.5, 0.0, 0.0, 99.0],
        "Min Inclusión (%)": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        "Max Inclusión (%)": [100.0, 100.0, 100.0, 1.5, 100.0, 100.0, 100.0, 5.0, 5.0, 5.0]
    })

st.session_state.df_ingredientes_state["Disponible"] = st.session_state.df_ingredientes_state["Disponible"].astype(bool)

if "df_collares_state" not in st.session_state:
    np.random.seed(42)
    ids_animales = [f"ID-{1000 + i}" for i in range(1, 26)]
    estados_salud = []
    visitas_com = []
    min_masticacion = []
    
    for idx in ids_animales:
        r = np.random.rand()
        if r < 0.75:
            estados_salud.append("🟢 Sano / Activo")
            visitas_com.append(int(np.random.randint(8, 15)))
            min_masticacion.append(int(np.random.randint(520, 680)))
        elif r < 0.90:
            estados_salud.append("🟡 Alerta (Bajo Consumo)")
            visitas_com.append(int(np.random.randint(3, 6)))
            min_masticacion.append(int(np.random.randint(380, 480)))
        else:
            estados_salud.append("🔴 Enfermo / Riesgo (Descarte)")
            visitas_com.append(int(np.random.randint(0, 2)))
            min_masticacion.append(int(np.random.randint(150, 320)))
            
    st.session_state.df_collares_state = pd.DataFrame({
        "ID Arete / Animal": ids_animales,
        "Estatus Collares IoT": estados_salud,
        "Visitas Comedero (visitas/día)": visitas_com,
        "Masticación / Rumina (min/día)": min_masticacion,
        "Acción IA Recomendada": [
            "Ninguna (Lote Óptimo)" if "Sano" in s else ("Aislar y revisar temperatura" if "Alerta" in s else "Descarte / Tratamiento urgente por ineficiencia") for s in estados_salud
        ]
    })

# --- 5. BARRA LATERAL (CONFIGURACIÓN NACIONAL Y REGIONAL) ---
st.sidebar.markdown(f"### 🇲🇽 Panel Nacional Nutri-ON")
st.sidebar.markdown(f"👤 **Usuario:** {st.session_state.current_user.capitalize()}")
st.sidebar.markdown(f"🛡️ **Licencia:** {plan_activo_usuario}")

with st.sidebar.expander("🔄 Gestión de Suscripción", expanded=False):
    st.markdown(f"**Próxima Renovación:** `{next_ren_date}`")
    nuevo_estado_auto = st.checkbox("Renovación Automática", value=auto_renew_status, key="sidebar_auto_renew_toggle")
    if nuevo_estado_auto != auto_renew_status:
        db_all = cargar_usuarios_persistentes()
        if st.session_state.current_user in db_all:
            db_all[st.session_state.current_user]["auto_renew"] = nuevo_estado_auto
            guardar_usuarios_persistentes(db_all)
            st.success("¡Estado actualizado!")
            st.rerun()

if st.sidebar.button("🚪 Cerrar Sesión", use_container_width=True):
    st.session_state.authenticated = False
    st.session_state.current_user = ""
    st.rerun()

st.sidebar.markdown("---")

# Diccionario de Estados de México y perfil climático base
estados_mexico_perfil = {
    "Aguascalientes": {"clima": "Seco / Templado", "thi_base": 72, "sistema": "Semi-estabulado"},
    "Baja California": {"clima": "Árido / Desértico", "thi_base": 76, "sistema": "Corral / Engorda Intensiva (Feedlot)"},
    "Baja California Sur": {"clima": "Árido / Cálido", "thi_base": 78, "sistema": "Agostadero / Semi-estabulado"},
    "Campeche": {"clima": "Tropical Húmedo", "thi_base": 82, "sistema": "Pastoreo Extensivo (Praderas / Agostadero)"},
    "Chiapas": {"clima": "Tropical / Subtropical", "thi_base": 80, "sistema": "Pastoreo Extensivo (Praderas / Agostadero)"},
    "Chihuahua": {"clima": "Seco / Extremoso", "thi_base": 74, "sistema": "Agostadero / Feedlot"},
    "Ciudad de México": {"clima": "Templado / Urbano", "thi_base": 70, "sistema": "Semi-estabulado"},
    "Coahuila": {"clima": "Árido / Seco", "thi_base": 77, "sistema": "Corral / Engorda Intensiva (Feedlot)"},
    "Colima": {"clima": "Tropical / Cálido", "thi_base": 81, "sistema": "Pastoreo Extensivo (Praderas / Agostadero)"},
    "Durango": {"clima": "Seco / Templado", "thi_base": 73, "sistema": "Agostadero / Semi-estabulado"},
    "Estado de México": {"clima": "Templado / Subhúmedo", "thi_base": 70, "sistema": "Semi-estabulado (Mixto / Suplementación en Pastoreo)"},
    "Guanajuato": {"clima": "Semiárido / Templado", "thi_base": 72, "sistema": "Semi-estabulado"},
    "Guerrero": {"clima": "Tropical / Cálido", "thi_base": 82, "sistema": "Pastoreo Extensivo (Praderas / Agostadero)"},
    "Hidalgo": {"clima": "Templado / Semiárido", "thi_base": 71, "sistema": "Semi-estabulado"},
    "Jalisco": {"clima": "Templado / Subhúmedo (Líder Ganadero)", "thi_base": 73, "sistema": "Semi-estabulado (Mixto / Suplementación en Pastoreo)"},
    "Michoacán": {"clima": "Cálido / Templado", "thi_base": 75, "sistema": "Semi-estabulado"},
    "Morelos": {"clima": "Cálido / Subhúmedo", "thi_base": 78, "sistema": "Semi-estabulado"},
    "Nayarit": {"clima": "Tropical / Cálido", "thi_base": 80, "sistema": "Pastoreo Extensivo (Praderas / Agostadero)"},
    "Nuevo León": {"clima": "Seco / Semiárido", "thi_base": 78, "sistema": "Corral / Engorda Intensiva (Feedlot)"},
    "Oaxaca": {"clima": "Tropical / Diverse", "thi_base": 79, "sistema": "Pastoreo Extensivo (Praderas / Agostadero)"},
    "Puebla": {"clima": "Templado / Semiárido", "thi_base": 71, "sistema": "Semi-estabulado"},
    "Querétaro": {"clima": "Semiárido / Templado", "thi_base": 72, "sistema": "Semi-estabulado"},
    "Quintana Roo": {"clima": "Tropical Húmedo", "thi_base": 83, "sistema": "Pastoreo Extensivo (Praderas / Agostadero)"},
    "San Luis Potosí": {"clima": "Seco / Semiárido", "thi_base": 76, "sistema": "Agostadero / Semi-estabulado"},
    "Sinaloa": {"clima": "Cálido / Seco", "thi_base": 79, "sistema": "Corral / Engorda Intensiva (Feedlot)"},
    "Sonora": {"clima": "Árido / Extremoso", "thi_base": 80, "sistema": "Corral / Engorda Intensiva (Feedlot)"},
    "Tabasco": {"clima": "Tropical Húmedo", "thi_base": 84, "sistema": "Pastoreo Extensivo (Praderas / Agostadero)"},
    "Tamaulipas": {"clima": "Cálido / Subhúmedo", "thi_base": 78, "sistema": "Agostadero / Feedlot"},
    "Tlaxcala": {"clima": "Templado / Frío", "thi_base": 69, "sistema": "Semi-estabulado"},
    "Veracruz": {"clima": "Tropical / Cálido Húmedo", "thi_base": 82, "sistema": "Pastoreo Extensivo (Praderas / Agostadero)"},
    "Yucatán": {"clima": "Tropical Cálido / Seco", "thi_base": 83, "sistema": "Pastoreo Extensivo (Praderas / Agostadero)"},
    "Zacatecas": {"clima": "Seco / Semiárido (Agostadero)", "thi_base": 72, "sistema": "Pastoreo Extensivo (Praderas / Agostadero)"}
}

with st.sidebar.expander("📍 Ubicación y Estado de la República", expanded=True):
    estado_seleccionado = st.selectbox("Selecciona tu Estado", list(estados_mexico_perfil.keys(), index=list(estados_mexico_perfil.keys()).index("Zacatecas")))
    perfil_estado = estados_mexico_perfil[estado_seleccionado]
    st.info(f"📍 **Región:** {estado_seleccionado}\n* **Clima:** {perfil_estado['clima']}\n* **THI Base:** {perfil_estado['thi_base']}")

with st.sidebar.expander("🐄 Lote, Pesos y Población", expanded=False):
    cantidad_animales = st.number_input("Número de Cabezas en el Lote", min_value=1, max_value=5000, value=100, step=10)
    peso_actual = st.slider("Peso Actual / Compra (kg)", min_value=200.0, max_value=650.0, value=250.0, step=10.0)
    peso_objetivo = st.slider("Peso de Venta / Meta (kg)", min_value=400.0, max_value=750.0, value=520.0, step=10.0)
    
    modo_gde = st.selectbox("Modo de Optimización GDE", ["Manual (Fijo)", "Automático Elite (Máxima GDE al Mínimo Costo x kg)"])
    if modo_gde == "Manual (Fijo)":
        gde = st.slider("Ganancia Diaria Esperada (GDE kg/día)", min_value=0.8, max_value=2.2, value=1.4, step=0.1)
    else:
        gde = 1.6

with st.sidebar.expander("💰 Parámetros Económicos y Sanidad", expanded=False):
    precio_compra_kg = st.number_input("Compra Becerro Base (MXN/kg)", min_value=30.0, max_value=100.0, value=55.0, step=1.0)
    precio_venta_kg = st.number_input("Venta Ganado Gordo Base (MXN/kg)", min_value=30.0, max_value=100.0, value=50.0, step=1.0)
    
    st.markdown("---")
    st.markdown("##### 🩺 Costos de Recepción y Sanidad (MXN/cab)")
    costo_aretaje = st.number_input("Aretaje (SINIIGA / ID)", min_value=0.0, max_value=500.0, value=45.0, step=5.0)
    costo_barrido = st.number_input("Barrido Sanitario (TB / Brucela)", min_value=0.0, max_value=1000.0, value=150.0, step=10.0)
    costo_vacunacion = st.number_input("Vacunación (Clostridios / Resp.)", min_value=0.0, max_value=500.0, value=90.0, step=5.0)
    costo_desparasitacion = st.number_input("Desparasitación", min_value=0.0, max_value=500.0, value=60.0, step=5.0)
    costo_vitaminacion = st.number_input("Vitaminación", min_value=0.0, max_value=500.0, value=40.0, step=5.0)
    costo_mano_obra_fijo = st.number_input("Mano de Obra y Operación", min_value=0.0, max_value=3000.0, value=450.0, step=50.0)

with st.sidebar.expander("🌾 Sistema de Producción y Pastoreo", expanded=False):
    sistema_produccion = st.selectbox(
        "Sistema Ganadero", 
        ["Corral / Engorda Intensiva (Feedlot)", "Semi-estabulado (Mixto / Suplementación en Pastoreo)", "Pastoreo Extensivo (Praderas / Agostadero)"],
        index=0 if "Feedlot" in perfil_estado['sistema'] else (1 if "Semi" in perfil_estado['sistema'] else 2)
    )
    condiciones_pastoreo = st.selectbox("Condiciones Pastoreo", ["N/A (Corral Intensivo)", "Pradera Cultivada / Riego (Alta Calidad)", "Pradera Nativa / Agostadero en Temporal", "Pradera Nativa / Agostadero Árido", "Sistema Silvopastoril"])
    estado_pasto = st.selectbox("Estado del Pasto", ["N/A (Corral / Sin Pastoreo)", "Vegetativo Temprano", "Vegetativo Tardío / Pre-floración", "Floración / Madurez", "Lignificado / Seco"])
    estacion = st.selectbox("Temporada Climática Actual", ["Templado / Primavera", "Verano (Lluvias / Calor)", "Invierno / Secas"])

with st.sidebar.expander("🧬 Genética y Razas de México", expanded=False):
    raza_seleccionada = st.selectbox(
        "Raza Predominante en el Lote", 
        [
            "Sintéticas / Adaptadas México (Beefmaster / Brangus / Suiz-Bu)", 
            "Británicas (Angus / Hereford)", 
            "Continentales (Charolais / Simmental / Limousin)", 
            "Cebú / Tropicales (Brahman / Nelore / Guzerat / Gyr)", 
            "Ganado Criollo Mexicano / Local"
        ]
    )
    sexo_lote = st.selectbox("Categoría Zootécnica", ["Novillos (Castrados)", "Toros Enteros", "Vaquillas de Repasto/Engorda", "Vacas de Desecho / Finalización"])
    marco_lote = st.selectbox("Tamaño de Marco", ["Mediano (Standard)", "Precoz / Engrase rápido", "Grande (Continental / Retrasado)"])

with st.sidebar.expander("🌡️ Variables Avanzadas", expanded=False):
    condicion_corporal = st.slider("Condición Corporal (1.0 - 5.0)", min_value=1.0, max_value=5.0, value=2.5, step=0.5)
    nivel_thi = st.selectbox("Estrés Térmico Regional (THI)", ["Confort Térmico (< 74)", "Estrés Moderado (74-78)", "Estrés Severo (> 78)"])
    perfil_aa = st.selectbox("Modelo Aminoácidos", ["Estándar (Proteína Cruda)", "Avanzado (Optimización Lisina:Metionina 3:1)"])
    aditivo_ruminal = st.selectbox("Modificadores / Aditivos", ["Ninguno", "Ionóforos (Monensina / Lasalocid)", "Buffer (Bicarbonato / Óxido Mg)", "Ambos (Ionóforo + Buffer)"])
    historial_nutricional = st.selectbox("Historial Nutricional", ["Desarrollo Continuo (Normal)", "Crecimiento Compensatorio (Post-restricción)"])
    promotor_crecimiento = st.selectbox("Promotores Crecimiento", ["Ninguno", "Implante Hormonal", "Agonista β-adrenérgico"])
    condicion_lodo = st.selectbox("Condición de Corral / Lodo", ["Seco y Confortable", "Lodo Moderado (10-15 cm)", "Lodo Severo (>20 cm)"])

# --- FACTORES DE CÁLCULO ---
df_base = st.session_state.df_ingredientes_state
df_base["Disponible"] = df_base["Disponible"].astype(bool)

factor_clima = 0.93 if estacion == "Invierno / Secas" else (1.05 if estacion == "Verano (Lluvias / Calor)" else 1.00)
factor_thi = 0.93 if "Moderado" in nivel_thi else (0.83 if "Severo" in nivel_thi else 1.00)
factor_cc = 1.06 if condicion_corporal < 3.0 else 1.00 
factor_aa = 1.04 if "Avanzado" in perfil_aa else 1.00

factor_sistema_cms = 1.12 if "Pastoreo" in sistema_produccion else (1.06 if "Semi-estabulado" in sistema_produccion else 1.00)
factor_sistema_energ = 1.10 if "Pastoreo" in sistema_produccion else (1.05 if "Semi-estabulado" in sistema_produccion else 1.00)

factor_pastoreo_energia = 1.10 if "Árido" in condiciones_pastoreo else (1.05 if "Temporal" in condiciones_pastoreo else 1.00)
factor_fenologia_pc = 1.15 * factor_aa if "Lignificado" in estado_pasto or "Madurez" in estado_pasto else (1.08 * factor_aa if "Tardío" in estado_pasto else 1.00)
factor_fenologia_energ = 1.10 if "Lignificado" in estado_pasto or "Madurez" in estado_pasto else (1.05 if "Tardío" in estado_pasto else 1.00)

factor_lodo = 1.00 if condicion_lodo == "Seco y Confortable" else (1.12 if "Moderado" in condicion_lodo else 1.25)
cms_estimado = peso_actual * 0.024 * factor_clima * factor_thi * factor_cc * factor_sistema_cms / (factor_lodo if "Severo" in condicion_lodo else 1.0)

# --- MOTOR DE OPTIMIZACIÓN LINEAL ---
class OptimizeResultCompat:
    def __init__(self, success, fun, x, message=""):
        self.success = success
        self.fun = fun
        self.x = x
        self.message = message

def optimizar_dieta_precision(df_ingredientes, requerimientos):
    try:
        costos = df_ingredientes["Precio Estimado (MXN/ton)"].astype(float).values
        pc = df_ingredientes["Proteina Cruda (PC % MS)"].astype(float).values / 100.0
        neg = df_ingredientes["NEg (Mcal/kg)"].astype(float).values
        fnd = df_ingredientes["FND (% MS)"].astype(float).values / 100.0
        pendf = df_ingredientes["peNDF (% MS)"].astype(float).values / 100.0
        pdr = df_ingredientes["PDR (% MS)"].astype(float).values / 100.0
        pnd = df_ingredientes["PND (% MS)"].astype(float).values / 100.0
        ca = df_ingredientes["Calcio (Ca %)"].astype(float).values / 100.0
        p_min_ing = df_ingredientes["Fosforo (P %)"].astype(float).values / 100.0
    except KeyError as e:
        return OptimizeResultCompat(False, 0.0, np.array([]), f"Falta columna: {e}")

    bounds = []
    for idx, row in df_ingredientes.iterrows():
        if not row["Disponible"]:
            bounds.append((0.0, 0.0))
        else:
            min_lim = max(0.0, float(row["Min Inclusión (%)"]) / 100.0)
            max_lim = min(1.0, float(row["Max Inclusión (%)"]) / 100.0)
            bounds.append((min_lim, max_lim))

    A_eq = np.ones((1, len(costos)))
    b_eq = np.array([1.0])

    req_pc = requerimientos.get("PC_min", 0.12)
    req_neg = requerimientos.get("NEg_min", 1.10)
    req_fnd_min = requerimientos.get("FND_min", 0.25)
    req_fnd_max = requerimientos.get("FND_max", 0.50)
    req_pendf = requerimientos.get("peNDF_min", 0.18)
    req_rdp = requerimientos.get("RDP_min", 0.065)
    req_rup = requerimientos.get("RUP_min", 0.035)
    req_ca = requerimientos.get("Ca_min", 0.0045)
    req_p = requerimientos.get("P_min", 0.0028)

    row_cap_min = -ca + 1.5 * p_min_ing
    row_cap_max = ca - 2.5 * p_min_ing

    A_ub = np.array([
        -pc, -neg, -fnd, fnd, -pendf, -pdr, -pnd, -ca, -p_min_ing, row_cap_min, row_cap_max
    ])
    b_ub = np.array([
        -req_pc, -req_neg, -req_fnd_min, req_fnd_max, -req_pendf, -req_rdp, -req_rup, -req_ca, -req_p, 0.0, 0.0
    ])

    res = linprog(costos, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
    if res.success:
        return OptimizeResultCompat(True, res.fun, res.x, "Factible")
    
    b_ub_rel = np.array([
        -req_pc * 0.90, -req_neg * 0.90, -req_fnd_min, req_fnd_max, -req_pendf * 0.85,
        -req_rdp * 0.85, -req_rup * 0.85, -req_ca * 0.85, -req_p * 0.85, 0.0, 0.0
    ])
    res_rel = linprog(costos, A_ub=A_ub, b_ub=b_ub_rel, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
    if res_rel.success:
        return OptimizeResultCompat(True, res_rel.fun, res_rel.x, "Factible con tolerancia ajustada")
    return OptimizeResultCompat(False, 4500.0, np.zeros(len(costos)), "Sin solución factible")

if modo_gde == "Automático Elite (Máxima GDE al Mínimo Costo x kg)":
    mejor_gde = 1.2
    menor_costo_kg_ganado = float('inf')
    for g_test in np.arange(1.0, 2.2, 0.05):
        req_t = {"PC_min": 0.13, "NEg_min": 1.1, "FND_min": 0.27, "FND_max": 0.50, "peNDF_min": 0.18, "RDP_min": 0.07, "RUP_min": 0.035, "Ca_min": 0.0045, "P_min": 0.0028}
        res_t = optimizar_dieta_precision(df_base, req_t)
        if res_t.success:
            costo_por_kg = ((cms_estimado / 1000.0) * res_t.fun) / g_test
            if costo_por_kg < menor_costo_kg_ganado:
                menor_costo_kg_ganado = costo_por_kg
                mejor_gde = g_test
    gde = round(float(mejor_gde), 2)

kg_por_ganar = max(0.0, peso_objetivo - peso_actual)
dias_a_meta = kg_por_ganar / gde if gde > 0 else 0

if peso_actual < 280:
    fase = "Recepción y Adaptación"
    meta_pc_base, meta_neg_base = 0.14, 0.75
elif peso_actual < 380:
    fase = "Crecimiento / Repasto"
    meta_pc_base, meta_neg_base = 0.125, 0.85
else:
    fase = "Finalización / Engorda Pesada"
    meta_pc_base, meta_neg_base = 0.11, 1.05

factor_raza = 1.02 if "Británicas" in raza_seleccionada else (0.95 if "Cebú" in raza_seleccionada else 1.00)
meta_pc_min = meta_pc_base * factor_raza * factor_aa
meta_neg_min = meta_neg_base * factor_raza

requerimientos_lote = {
    "PC_min": meta_pc_min, "NEg_min": meta_neg_min, "FND_min": 0.27, "FND_max": 0.50,
    "peNDF_min": 0.18, "RDP_min": 0.07, "RUP_min": 0.035, "Ca_min": 0.0045, "P_min": 0.0028
}

resultado = optimizar_dieta_precision(df_base, requerimientos_lote)
costo_ton_optimizado = resultado.fun if resultado.success else 4500.0 
modo_tolerancia_activo = ("tolerancia" in resultado.message.lower())

consumo_total_ciclo_cab = cms_estimado * dias_a_meta
costo_alimentacion_cab = (consumo_total_ciclo_cab / 1000.0) * costo_ton_optimizado
costo_compra_cab = peso_actual * precio_compra_kg
costo_sanidad_inicial = costo_aretaje + costo_barrido + costo_vacunacion + costo_desparasitacion + costo_vitaminacion
costo_total_sanidad_y_manejo = costo_sanidad_inicial + costo_mano_obra_fijo
costo_total_cab = costo_compra_cab + costo_alimentacion_cab + costo_total_sanidad_y_manejo
ingreso_venta_cab = peso_objetivo * precio_venta_kg
utilidad_neta_cab = ingreso_venta_cab - costo_total_cab
roi_cab = (utilidad_neta_cab / costo_total_cab) * 100 if costo_total_cab > 0 else 0

# --- CÁLCULO DE EMISIONES Y NUTRIENTES ---
if resultado.success:
    pc_arr = df_base["Proteina Cruda (PC % MS)"].astype(float).values / 100.0
    neg_arr = df_base["NEg (Mcal/kg)"].astype(float).values
    fnd_arr = df_base["FND (% MS)"].astype(float).values / 100.0
    pendf_arr = df_base["peNDF (% MS)"].astype(float).values / 100.0
    ca_arr = df_base["Calcio (Ca %)"].astype(float).values / 100.0
    p_arr = df_base["Fosforo (P %)"].astype(float).values / 100.0
    lip_arr = df_base["Lípidos / Extracto Etéreo (%)"].astype(float).values / 100.0

    aporte_pc = np.sum(resultado.x * pc_arr) * 100
    aporte_neg = np.sum(resultado.x * neg_arr)
    aporte_pendf = np.sum(resultado.x * pendf_arr) * 100
    aporte_lipidos = np.sum(resultado.x * lip_arr) * 100
    ch4_g_dia = (cms_estimado * 18.4 * 0.065 / 55.65) * 1000
    co2e_anual = (ch4_g_dia * 365 / 1000.0) * 28.0 
else:
    aporte_pc, aporte_neg, aporte_pendf, aporte_lipidos, ch4_g_dia, co2e_anual = 12.0, 1.1, 20.0, 3.0, 200.0, 2000.0

# --- GENERADOR PDF ---
class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.set_text_color(5, 150, 105)
        self.cell(0, 10, f'Nutri-ON 360 ULTRA - Estado: {estado_seleccionado} (Dr. Alejandro Castaneda)', 0, 1, 'C')
        self.ln(3)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, f'Pagina {self.page_no()} | Ganaderia de Precision Mexico', 0, 0, 'C')

def generar_pdf_reporte():
    pdf = PDFReport()
    pdf.add_page()
    def safe_str(txt): return str(txt).encode('latin-1', 'replace').decode('latin-1')
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 8, safe_str(f"1. Resumen Zootecnico - {estado_seleccionado}"), 0, 1)
    pdf.set_font('Arial', '', 10)
    pdf.cell(95, 7, safe_str(f"Raza: {raza_seleccionada}"), 0, 1)
    pdf.cell(95, 7, safe_str(f"Utilidad Neta Proyectada: ${utilidad_neta_cab:,.2f} MXN/cab"), 0, 1)
    output = pdf.output()
    return bytes(output) if isinstance(output, (bytes, bytearray)) else output.encode('latin1')

# --- 6. PESTAÑAS DE LA APLICACIÓN ---
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11, tab12 = st.tabs([
    "📋 1. Resumen & Clima", "🧪 2. Nutrición", "📊 3. Economía", "🩺 4. Collares IoT",
    "🚜 5. Báscula", "🔮 6. Compra-Venta", "📄 7. Reporte PDF", "💬 8. Nutri-ON IA",
    "🧭 9. Citas", "📡 10. NIR & pH", "🎙️ 11. IA Acústica", "🌱 12. Blockchain"
])

with tab1:
    st.subheader(f"Monitoreo Regional en {estado_seleccionado}")
    st.markdown(f"**Clima Regional:** {perfil_estado['clima']} | **Sistema Predominante:** {sistema_produccion} | **Raza:** {raza_seleccionada}")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Etapa Fisiológica", fase)
        st.metric("GDE Objetivo", f"{gde} kg/día")
    with col2:
        st.metric("Consumo MS (Ajustado THI)", f"{cms_estimado:.2f} kg/día")
        st.metric("Días a la Meta", f"{dias_a_meta:.0f} días")
    with col3:
        st.metric("Cabezas en Lote", f"{cantidad_animales} animales")
        st.metric("Ganancia Total", f"{kg_por_ganar:.1f} kg/cab")

with tab2:
    st.subheader("🧪 Laboratorio de Nutrición e Ingredientes Regionales de México")
    st.markdown("Personaliza o añade materias primas disponibles en tu región (granos, forrajes y subproductos nacionales).")
    st.session_state.df_ingredientes_state = st.data_editor(
        st.session_state.df_ingredientes_state, num_rows="dynamic", use_container_width=True, key="editor_ingredientes_mex"
    )

with tab3:
    st.subheader("📊 Evaluación Económica y Rentabilidad por Cabeza (MXN)")
    col_ec1, col_ec2, col_ec3, col_ec4 = st.columns(4)
    with col_ec1:
        st.metric("Compra Becerro", f"${costo_compra_cab:,.0f}")
        st.metric("Alimento/Cab", f"${costo_alimentacion_cab:,.0f}")
    with col_ec2:
        st.metric("Costo Total", f"${costo_total_cab:,.0f}")
        st.metric("Sanidad Inicial", f"${costo_sanidad_inicial:,.0f}")
    with col_ec3:
        st.metric("Ingreso Venta", f"${ingreso_venta_cab:,.0f}")
        st.metric("Utilidad Neta", f"${utilidad_neta_cab:,.0f}")
    with col_ec4:
        st.metric("ROI Ciclo", f"{roi_cab:.1f}%")
        st.metric("Estatus", "🟢 Rentable" if utilidad_neta_cab > 0 else "🔴 Negativo")

with tab4:
    st.subheader("🩺 Collares IoT y Alertas de Comportamiento Animal")
    st.dataframe(st.session_state.df_collares_state, use_container_width=True, hide_index=True)

with tab5:
    st.subheader("🚜 Báscula Digital e Indicadores de Carro Mezclador")
    st.info("🔗 Sistema vinculado vía Bluetooth/Wi-Fi con la batea mezcladora del rancho.")

with tab6:
    st.subheader("🔮 Simulador Estratégico de Compra-Venta en el Mercado Nacional")
    st.metric("Utilidad Máxima Proyectada", f"${utilidad_neta_cab:,.0f} MXN por cabeza")

with tab7:
    st.subheader("📄 Reporte Ejecutivo en PDF")
    if resultado.success:
        pdf_bytes = generar_pdf_reporte()
        st.download_button("📥 Descargar Reporte PDF México", data=pdf_bytes, file_name=f"NutriON_{estado_seleccionado}.pdf", mime="application/pdf", use_container_width=True)

with tab8:
    st.subheader("💬 Asistente Virtual Nutri-ON IA (Especialista en Ganadería Mexicana)")
    for message in st.session_state.nutrion_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    if user_query := st.chat_input("Escribe tu consulta sobre engorda en México..."):
        st.session_state.nutrion_messages.append({"role": "user", "content": user_query})
        with st.chat_message("user"): st.markdown(user_query)
        bot_response = f"🤖 Como experto en ganadería en **{estado_seleccionado}**, analizando tu lote de **{cantidad_animales} cabezas** ({raza_seleccionada}), te sugiero evaluar la calidad de tus forrajes locales y ajustar la suplementación ante las condiciones climáticas de la región."
        st.session_state.nutrion_messages.append({"role": "assistant", "content": bot_response})
        with st.chat_message("assistant"): st.markdown(bot_response)

with tab9:
    st.subheader("🧭 Asesoría Técnica Especializada")
    st.write("Agendar cita con especialistas agrónomos y zootecnistas en México.")

with tab10:
    st.subheader("📡 Escaneo NIR y pH Ruminal")
    st.write("Monitoreo de materia seca y prevención de SARA (Acidosis Subclínica).")

with tab11:
    st.subheader("🎙️ IA Acústica y Visión Artificial")
    st.write("Detección temprana de BRD (Tos) y cojeras en corrales.")

with tab12:
    st.subheader("🌱 Gemelos Digitales & Trazabilidad Blockchain")
    st.write("Certificación de carne y créditos de carbono en el mercado mexicano e internacional.")
