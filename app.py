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
    page_title="NutriON 360 Ultra | Precisión Nutricional, IA y Collares IoT",
    page_icon="🐄",
    layout="centered",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    /* UNIFICACIÓN GLOBAL DE FUENTE Y COLOR BASE SaaS */
    html, body, [class*="css"], .stMarkdown, .stText, .stSelectbox, .stSlider, .stNumberInput, div, span, p, label, .stRadio {
        font-family: 'Calibri', sans-serif !important;
        color: #1e293b !important;
    }
    
    .main {
        background-color: #f8fafc;
        font-family: 'Calibri', sans-serif !important;
    }
    
    /* TARJETAS DE MÉTRICAS AVANZADAS (CARDS) */
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
    
    /* ENCABEZADOS Y TÍTULOS CORPORATIVOS */
    h1, h2, h3, h4, h5, h6 {
        color: #0f172a !important;
        font-family: 'Calibri', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: -0.5px;
    }

    /* PESTAÑAS (TABS) MODERNAS */
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
    
    /* BOTONES ESTILIZADOS */
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
    
    /* CONTENEDOR DE ALERTAS E INFO */
    .stAlert {
        border-radius: 12px !important;
        border: 1px solid #cbd5e1 !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. GESTIÓN DE MULTI-USUARIOS, PERSISTENCIA Y RENOVACIÓN AUTOMÁTICA ---
USERS_FILE = "usuarios_nutrion_360_ultra.json"

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
            "email": "admin@nutrion360.com",
            "subscription_active": True,
            "plan": "Anual Ultra AI & IoT (12 Meses) - $9,600 MXN | $800.00/mes",
            "auto_renew": True,
            "next_renewal_date": (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d"),
            "fecha_registro": "2026-01-01"
        },
        "alejandro": {
            "password": hash_password("elite360"),
            "email": "alejandro.castaneda@nutrion360.com",
            "subscription_active": True,
            "plan": "Anual Ultra AI & IoT (12 Meses) - $9,600 MXN | $800.00/mes",
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
        {"role": "assistant", "content": "¡Hola! Soy **NutriON**, tu asistente virtual con Inteligencia Artificial para **NutriON 360 Ultra V4.0**. Estoy conectado en tiempo real con sensores NIR, bolos ruminales de pH, collares IoT y el motor de optimización lineal de precisión. ¿En qué te puedo ayudar hoy?"}
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
            NutriON <span style="color: #059669;">360</span> <span style="font-size: 0.5em; background: #059669; color: white; padding: 2px 8px; border-radius: 6px; vertical-align: middle;">ULTRA V4.0 AI & IOT</span>
        </h2>
        <p style="text-align: center; color: #059669; font-family: 'Calibri', sans-serif; font-weight: 700; font-size: 0.95rem; margin-bottom: 8px;">
            Nutrición de precisión, programación lineal avanzada, collares IoT y salud animal.
        </p>
        <p style="text-align: center; color: #475569; font-family: 'Calibri', sans-serif; font-size: 0.85rem; margin-bottom: 25px;">
            Plataforma Global de Optimización, Smart Collars y Consultoría Experta Remota
        </p>
    """, unsafe_allow_html=True)

    tab_login, tab_register = st.tabs(["🔑 Iniciar Sesión", "💳 Planes Ultra AI & Registro"])

    with tab_login:
        st.markdown("### Acceso con Usuario y Contraseña")
        user_input = st.text_input("Nombre de Usuario", key="login_user")
        pass_input = st.text_input("Contraseña", type="password", key="login_pass")
        
        st.markdown("")
        if st.button("Entrar a la Plataforma Ultra AI", use_container_width=True):
            db_usuarios = cargar_usuarios_persistentes()
            hashed_pass = hash_password(pass_input)
            
            if user_input in db_usuarios and db_usuarios[user_input]["password"] == hashed_pass:
                if db_usuarios[user_input].get("subscription_active", False):
                    st.session_state.authenticated = True
                    st.session_state.current_user = user_input
                    st.success(f"¡Bienvenido de nuevo, {user_input}!")
                    st.rerun()
                else:
                    st.error("Tu suscripción se encuentra inactiva. Selecciona un plan y realiza el pago para renovar.")
            else:
                st.error("Usuario o contraseña incorrectos. Verifica tus datos.")

    with tab_register:
        st.markdown("### 🌟 Selección de Plan Ultra AI & IoT")
        st.markdown("Elige el periodo de suscripción con acceso total a sensores NIR, collares IoT y motor de precisión:")
        
        plan_elegido = st.radio(
            "Planes de Suscripción NutriON 360 Disponibles:",
            [
                "Trimestral Pro AI (3 Meses) - $3,000 MXN | $1,000.00/mes",
                "Semestral Feedlot IoT (6 Meses) - $5,400 MXN | $900.00/mes",
                "Anual Ultra AI & IoT (12 Meses) - $9,600 MXN | $800.00/mes (Acceso Total)"
            ],
            index=2
        )
        
        st.markdown("---")
        st.markdown("##### 📝 Datos de Cuenta, Pago Seguro y Renovación Automática")
        
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            new_user = st.text_input("Nombre de Usuario Deseado", key="reg_user")
            new_email = st.text_input("Correo Electrónico (para notificaciones y avisos)", key="reg_email")
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
        
        auto_renew_enabled = st.checkbox(
            "🔄 **Activar Renovación Automática** (La suscripción se cobrará y renovará automáticamente al cumplirse el periodo elegido, garantizando monitoreo ininterrumpido).",
            value=True
        )
        
        st.markdown("")
        
        try:
            costo_str = plan_elegido.split("-")[1].split("|")[0].strip()
        except Exception:
            costo_str = "$9,600 MXN"
        
        if st.button(f"💳 Pagar {costo_str} y Activar Licencia Ultra AI", use_container_width=True):
            db_usuarios = cargar_usuarios_persistentes()
            
            if not new_user or not new_email or not new_pass or not num_tarjeta:
                st.warning("⚠️ Por favor, completa todos los campos de registro y de pago.")
            elif new_user in db_usuarios:
                st.error("⚠️ El nombre de usuario ya existe. Elige otro o inicia sesión.")
            elif new_pass != confirm_pass:
                st.error("⚠️ Las contraseñas no coinciden.")
            elif len(num_tarjeta.replace(" ", "")) < 15:
                st.error("⚠️ Número de tarjeta inválido. Verifica los dígitos.")
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
                
                st.success(f"🎉 **¡Pago Exitoso de {costo_str} ({plan_elegido})!** Transacción aprobada.")
                if auto_renew_enabled:
                    st.info(f"🔄 **Renovación Automática Activada:** Tu próxima renovación está programada para el **{fecha_renovacion}**.")
                st.success(f"📧 **Notificación Enviada:** Se ha enviado el comprobante fiscal y tus accesos a **{new_email}**.")
                
                st.session_state.authenticated = True
                st.session_state.current_user = new_user
                st.balloons()
                st.rerun()

    st.stop()

# --- 3. LOGOTIPO VETERINARIO Y DE CAMPO (USUARIO AUTENTICADO) ---
db_usuarios_activos = cargar_usuarios_persistentes()
user_info = db_usuarios_activos.get(st.session_state.current_user, {})
plan_activo_usuario = user_info.get("plan", "Plan Ultra AI & IoT")
auto_renew_status = user_info.get("auto_renew", False)
next_ren_date = user_info.get("next_renewal_date", "N/A")

st.markdown(f"""
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
                NutriON <span style="background: linear-gradient(135deg, #059669, #10b981); color: #ffffff; padding: 3px 10px; border-radius: 8px; font-size: 0.5em; vertical-align: middle; font-weight: 700; letter-spacing: 0.8px; box-shadow: 0 4px 10px rgba(5,150,105,0.3);">360 ULTRA V4.0</span>
            </h1>
            <p style="margin: 2px 0 2px 0; font-size: 0.82em; color: #059669; font-weight: 700; font-family: 'Calibri', sans-serif;">
                Optimización lineal de precisión, sensores NIR, collares IoT y salud animal en tiempo real.
            </p>
            <p style="margin: 3px 0 2px 0; font-size: 0.88em; color: #1e293b; font-weight: 600; font-family: 'Calibri', sans-serif;">
                Usuario: <span style="color: #059669; font-weight: 700;">{st.session_state.current_user.capitalize()}</span> | Licencia: <span style="color: #d97706; font-weight: 700;">{plan_activo_usuario}</span> | Creado por: Dr. Alejandro Castañeda Correa
            </p>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- 4. BASE DE DATOS INICIAL CON PERSISTENCIA (SESSION STATE) ---
if "df_ingredientes_state" not in st.session_state:
    st.session_state.df_ingredientes_state = pd.DataFrame({
        "Nombre del Ingrediente": [
            "Rastrojo de maiz molido", "Harina de soya", "Grano de maiz molido", 
            "Urea", "Ensilado de maiz", "Canola (pasta)", "Melaza liquida",
            "Purina Mineral Tech (Tlaltenango)", "Malta Cleyton Ganafos", "Grasa de paso Lactomil"
        ],
        "Categoria": ["Forraje", "Suplemento Proteico", "Grano Energetico", "Suplemento NPN", "Forraje Humedo", "Suplemento Proteico", "Subproducto / Energetico", "Suplemento Mineral", "Suplemento Mineral", "Suplemento Energetico"],
        "Disponible": [True, True, True, True, True, True, True, True, True, True],
        "Precio Estimado (MXN/ton)": [2500.0, 12500.0, 5800.0, 16000.0, 1200.0, 8500.0, 4800.0, 19000.0, 18500.0, 32000.0],
        "Proteina Cruda (PC % MS)": [5.5, 48.0, 8.5, 281.0, 8.0, 38.0, 4.8, 0.0, 0.0, 1.0],
        "NEg (Mcal/kg)": [0.35, 1.48, 1.55, 0.0, 0.85, 1.15, 1.22, 0.0, 0.0, 1.65],
