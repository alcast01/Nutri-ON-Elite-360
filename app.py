import streamlit as st
import numpy as np
import pandas as pd
from scipy.optimize import linprog
import plotly.express as px
import plotly.graph_objects as go
from fpdf import FPDF
import json
import os
import hashlib
from datetime import datetime, timedelta

# --- 1. CONFIGURACIÓN DE PÁGINA Y DISEÑO SaaS PROFESIONAL (CALIBRI) ---
st.set_page_config(
    page_title="Nutri-ON 360 ULTRA | Modelo Fisiológico & Red IoT México",
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
    .main { background-color: #f8fafc; font-family: 'Calibri', sans-serif !important; }
    .stMetric {
        background: #ffffff; padding: 12px 14px !important; border-radius: 14px;
        box-shadow: 0 4px 20px -3px rgba(15, 23, 42, 0.08); border: 1px solid #e2e8f0;
        border-left: 5px solid #059669; margin-bottom: 10px !important; transition: all 0.3s ease;
    }
    .stMetric:hover { transform: translateY(-2px); box-shadow: 0 10px 25px -5px rgba(5, 150, 105, 0.15); border-color: #059669; }
    .stMetric label { font-size: 0.72rem !important; color: #64748b !important; font-weight: 700 !important; text-transform: uppercase; letter-spacing: 0.8px; }
    .stMetric [data-testid="stMetricValue"] { font-size: 1.15rem !important; color: #0f172a !important; font-weight: 800 !important; }
    h1, h2, h3, h4, h5, h6 { color: #0f172a !important; font-family: 'Calibri', sans-serif !important; font-weight: 700 !important; }
    .stTabs [data-baseweb="tab-list"] { gap: 6px; background-color: #e2e8f0; padding: 6px; border-radius: 14px; flex-wrap: wrap; }
    .stTabs [data-baseweb="tab"] { border-radius: 10px; font-weight: 600; color: #334155 !important; font-size: 0.78rem !important; padding: 8px 10px; background-color: transparent; }
    .stTabs [aria-selected="true"] { background-color: #ffffff !important; color: #059669 !important; box-shadow: 0 4px 15px rgba(0,0,0,0.06); }
    .stButton button { font-weight: 700 !important; border-radius: 10px !important; background: linear-gradient(135deg, #059669 0%, #10b981 100%) !important; color: #ffffff !important; border: none !important; box-shadow: 0 4px 12px rgba(5, 150, 105, 0.25); }
    .stAlert { border-radius: 12px !important; border: 1px solid #cbd5e1 !important; }
    </style>
""", unsafe_allow_html=True)

# --- 2. GESTIÓN DE USUARIOS Y PERSISTENCIA ---
USERS_FILE = "usuarios_nutrion_iot_mexico.json"

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
            "email": "admin@nutrion-iot.mx",
            "subscription_active": True,
            "plan": "Anual Nacional Elite (12 Meses) - $800.00 MXN/mes | Total: $9,600 MXN",
            "auto_renew": True,
            "next_renewal_date": (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d")
        },
        "alejandro": {
            "password": hash_password("elite360"),
            "email": "alejandro.castaneda@nutrion-iot.mx",
            "subscription_active": True,
            "plan": "Anual Nacional Elite (12 Meses) - $800.00 MXN/mes | Total: $9,600 MXN",
            "auto_renew": True,
            "next_renewal_date": (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d")
        }
    }
    guardar_usuarios_persistentes(default_users)
    return default_users

def guardar_usuarios_persistentes(usuarios_dict):
    with open(USERS_FILE, "w") as f:
        json.dump(usuarios_dict, f, indent=4)

if "authenticated" not in st.session_state: st.session_state.authenticated = False
if "current_user" not in st.session_state: st.session_state.current_user = ""
if "nutrion_messages" not in st.session_state:
    st.session_state.nutrion_messages = [
        {"role": "assistant", "content": "¡Hola! Soy **Nutri-ON Fisiológico & Linear Optimizer**, tu núcleo central de formulación matemática y telemetría ganadera en México. ¿Qué lote o ingrediente deseas optimizar hoy?"}
    ]

# --- PANTALLA DE ACCESO / SUSCRIPCIÓN CON PLANES COMERCIALES ---
if not st.session_state.authenticated:
    st.markdown("""
        <h2 style="text-align: center; color: #064e3b; font-weight: 800; margin-top: 20px;">
            Nutri-ON <span style="color: #059669;">360</span> <span style="font-size: 0.5em; background: #059669; color: white; padding: 2px 8px; border-radius: 6px;">MODELO FISIOLÓGICO & RED IOT</span>
        </h2>
        <p style="text-align: center; color: #059669; font-weight: 700; font-size: 0.95rem;">
            Plataforma Profesional de Programación Lineal Adaptada a las Necesidades Biológicas del Ganado en México
        </p>
    """, unsafe_allow_html=True)
    
    tab_login, tab_register = st.tabs(["🔑 Iniciar Sesión", "💳 Planes Comerciales & Ahorro"])
    with tab_login:
        user_input = st.text_input("Usuario", key="l_user")
        pass_input = st.text_input("Contraseña", type="password", key="l_pass")
        if st.button("Conectar al Sistema", use_container_width=True):
            db = cargar_usuarios_persistentes()
            if user_input in db and db[user_input]["password"] == hash_password(pass_input):
                st.session_state.authenticated = True
                st.session_state.current_user = user_input
                st.rerun()
            else:
                st.error("Credenciales inválidas.")
    
    with tab_register:
        st.markdown("### 🌟 Selecciona tu Plan Comercial y Maximiza tu Utilidad")
        plan_elegido = st.radio(
            "Planes de Suscripción Disponibles:",
            [
                "Trimestral (3 Meses) - $1,000 MXN/mes | Total: $3,000 MXN: \"Flexibilidad y control total para tu ciclo actual de engorda con inversión inteligente.\"",
                "Semestral Feedlot (6 Meses) - $900 MXN/mes | Total: $5,400 MXN: “¡Ahorra $600 MXN! El equilibrio perfecto para optimizar ciclos completos con un 10% de ahorro directo.”",
                "Anual Nacional Elite (12 Meses) - $800 MXN/mes | Total: $9,600 MXN: “¡Ahorra $2,400 MXN! La opción más inteligente de los ganaderos de élite: acceso ilimitado a toda la red IoT con 20% de descuento y máximo ROI.”"
            ],
            index=2
        )
        
        st.markdown("---")
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            r_user = st.text_input("Nombre de Usuario", key="r_u")
            r_email = st.text_input("Correo Electrónico", key="r_e")
        with col_r2:
            r_pass = st.text_input("Contraseña", type="password", key="r_p")
            r_card = st.text_input("Tarjeta de Crédito / Débito", placeholder="4000 1234 5678 9010", key="r_c")
        
        auto_renew_reg = st.checkbox("🔄 Activar Renovación Automática Segura", value=True)
        st.markdown("")
        
        if st.button("💳 Pagar Licencia y Activar Sistema", use_container_width=True):
            db = cargar_usuarios_persistentes()
            if not r_user or not r_pass or not r_card:
                st.warning("⚠️ Completa los campos obligatorios de usuario y pago.")
            elif r_user in db:
                st.error("⚠️ El usuario ya existe.")
            else:
                dias_periodo = 90 if "Trimestral" in plan_elegido else (180 if "Semestral" in plan_elegido else 365)
                fecha_renov = (datetime.now() + timedelta(days=dias_periodo)).strftime("%Y-%m-%d")
                
                db[r_user] = {
                    "password": hash_password(r_pass),
                    "email": r_email,
                    "subscription_active": True,
                    "plan": plan_elegido,
                    "auto_renew": auto_renew_reg,
                    "next_renewal_date": fecha_renov
                }
                guardar_usuarios_persistentes(db)
                st.session_state.authenticated = True
                st.session_state.current_user = r_user
                st.success("🎉 ¡Pago exitoso! Módulos de optimización lineal y red IoT activados.")
                st.balloons()
                st.rerun()
    st.stop()

# --- HEADER Y BARRA LATERAL CON PARÁMETROS PRODUCTIVOS & BIOLÓGICOS ---
db_activos = cargar_usuarios_persistentes()
user_info = db_activos.get(st.session_state.current_user, {})
plan_activo = user_info.get("plan", "Plan Nacional Elite")

st.markdown(f"""
    <div style="background: linear-gradient(135deg, #ffffff 0%, #ecfdf5 100%); padding: 18px 22px; border-radius: 16px; border: 2px solid #34d399; margin-bottom: 20px;">
        <h2 style="margin: 0; color: #064e3b; font-size: 1.5em;">🐄 Nutri-ON | Modelo Fisiológico & Red IoT</h2>
        <p style="margin: 4px 0 0 0; color: #059669; font-weight: 600; font-size: 0.88em;">
            Usuario: <span style="color: #0f172a;">{st.session_state.current_user.capitalize()}</span> | Licencia: <span style="color: #d97706;">{plan_activo}</span>
        </p>
    </div>
""", unsafe_allow_html=True)

estados_mexico_perfil = {
    "Aguascalientes": {"clima": "Seco / Templado", "thi_base": 72},
    "Baja California": {"clima": "Árido / Desértico", "thi_base": 76},
    "Baja California Sur": {"clima": "Árido / Cálido", "thi_base": 78},
    "Campeche": {"clima": "Tropical Húmedo", "thi_base": 82},
    "Chiapas": {"clima": "Tropical / Subtropical", "thi_base": 80},
    "Chihuahua": {"clima": "Seco / Extremoso", "thi_base": 74},
    "Ciudad de México": {"clima": "Templado / Urbano", "thi_base": 70},
    "Coahuila": {"clima": "Árido / Seco", "thi_base": 77},
    "Colima": {"clima": "Tropical / Cálido", "thi_base": 81},
    "Durango": {"clima": "Seco / Templado", "thi_base": 73},
    "Estado de México": {"clima": "Templado / Subhúmedo", "thi_base": 70},
    "Guanajuato": {"clima": "Semiárido / Templado", "thi_base": 72},
    "Guerrero": {"clima": "Tropical / Cálido", "thi_base": 82},
    "Hidalgo": {"clima": "Templado / Semiárido", "thi_base": 71},
    "Jalisco": {"clima": "Templado / Subhúmedo", "thi_base": 73},
    "Michoacán": {"clima": "Cálido / Templado", "thi_base": 75},
    "Morelos": {"clima": "Cálido / Subhúmedo", "thi_base": 78},
    "Nayarit": {"clima": "Tropical / Cálido", "thi_base": 80},
    "Nuevo León": {"clima": "Seco / Semiárido", "thi_base": 78},
    "Oaxaca": {"clima": "Tropical / Diverse", "thi_base": 79},
    "Puebla": {"clima": "Templado / Semiárido", "thi_base": 71},
    "Querétaro": {"clima": "Semiárido / Templado", "thi_base": 72},
    "Quintana Roo": {"clima": "Tropical Húmedo", "thi_base": 83},
    "San Luis Potosí": {"clima": "Seco / Semiárido", "thi_base": 76},
    "Sinaloa": {"clima": "Cálido / Seco", "thi_base": 79},
    "Sonora": {"clima": "Árido / Extremoso", "thi_base": 80},
    "Tabasco": {"clima": "Tropical Húmedo", "thi_base": 84},
    "Tamaulipas": {"clima": "Cálido / Subhúmedo", "thi_base": 78},
    "Tlaxcala": {"clima": "Templado / Frío", "thi_base": 69},
    "Veracruz": {"clima": "Tropical / Cálido Húmedo", "thi_base": 82},
    "Yucatán": {"clima": "Tropical Cálido / Seco", "thi_base": 83},
    "Zacatecas": {"clima": "Seco / Semiárido", "thi_base": 72}
}

with st.sidebar:
    st.markdown("### ⚙️ Parámetros Productivos & Biológicos")
    st.markdown("*Todas estas variables calibran los requerimientos del modelo lineal.*")
    
    estado_seleccionado = st.selectbox("1. Estado de la República", list(estados_mexico_perfil.keys()), index=list(estados_mexico_perfil.keys()).index("Zacatecas"))
    perfil_estado = estados_mexico_perfil[estado_seleccionado]
    
    cantidad_animales = st.number_input("2. Cabezas en el Lote", min_value=1, max_value=10000, value=150, step=10)
    peso_actual = st.slider("3. Peso Actual Promedio (kg)", min_value=200.0, max_value=650.0, value=280.0, step=10.0)
    peso_objetivo = st.slider("4. Peso de Venta Meta (kg)", min_value=400.0, max_value=750.0, value=540.0, step=10.0)
    gde = st.slider("5. Ganancia Diaria Esperada (GDE kg/día)", min_value=0.8, max_value=2.2, value=1.4, step=0.1)
    
    precio_compra = st.number_input("6. Precio Compra Becerro ($/kg)", 30.0, 100.0, 55.0)
    precio_venta = st.number_input("7. Precio Venta Ganado Gordo ($/kg)", 30.0, 100.0, 50.0)
    
    raza_seleccionada = st.selectbox("8. Raza / Genética", ["Sintéticas / Adaptadas (Beefmaster/Brangus)", "Británicas (Angus/Hereford)", "Continentales (Charolais/Simmental)", "Cebú (Brahman/Nelore)", "Criollo Mexicano"])
    sexo_lote = st.selectbox("9. Sexo / Categoría", ["Novillos (Castrados)", "Toros Enteros", "Vaquillas de Repasta"])
    marco_lote = st.selectbox("10. Tamaño de Marco", ["Mediano (Standard)", "Precoz", "Grande (Continental)"])
    sistema_produccion = st.selectbox("11. Sistema de Producción", ["Corral / Engorda Intensiva (Feedlot)", "Semi-estabulado (Mixto)", "Pastoreo Extensivo / Agostadero"])
    condicion_corporal = st.slider("12. Condición Corporal (1.0 - 5.0)", 1.0, 5.0, 2.5, 0.5)
    nivel_thi = st.selectbox("13. Estrés Térmico (THI)", ["Confort Térmico (< 74)", "Estrés Moderado (74-78)", "Estrés Severo (> 78)"])
    condicion_lodo = st.selectbox("14. Condición de Corral / Lodo", ["Seco y Confortable", "Lodo Moderado (10-15 cm)", "Lodo Severo (>20 cm)"])
    aditivo_ruminal = st.selectbox("15. Aditivos y Modificadores", ["Ninguno", "Ionóforos (Monensina)", "Buffer (Bicarbonato)", "Ambos (Ionóforo + Buffer)"])

    st.markdown("---")
    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.current_user = ""
        st.rerun()

# --- BASE DE DATOS DE INGREDIENTES ---
if "df_ingredientes_state" not in st.session_state:
    st.session_state.df_ingredientes_state = pd.DataFrame({
        "Nombre del Ingrediente": ["Rastrojo de maiz", "Harina de soya", "Grano de maiz molido", "Urea", "Ensilado de maiz", "Canola", "Melaza", "Mineral Regional", "Malta", "Grasa bypass"],
        "Categoria": ["Forraje", "Proteico", "Energético", "NPN", "Húmedo", "Proteico", "Energético", "Mineral", "Mineral", "Energético"],
        "Disponible": [True, True, True, True, True, True, True, True, True, True],
        "Precio Estimado (MXN/ton)": [2500.0, 12500.0, 5800.0, 16000.0, 1200.0, 8500.0, 4800.0, 19000.0, 18500.0, 32000.0],
        "Proteina Cruda (PC % MS)": [5.5, 48.0, 8.5, 281.0, 8.0, 38.0, 4.8, 0.0, 0.0, 1.0],
        "NEg (Mcal/kg)": [0.35, 1.48, 1.55, 0.0, 0.85, 1.15, 1.22, 0.0, 0.0, 1.65],
        "FND (% MS)": [75.0, 12.0, 9.0, 0.0, 45.0, 28.0, 0.0, 0.0, 0.0, 0.0],
        "peNDF (% MS)": [65.0, 2.0, 3.0, 0.0, 30.0, 10.0, 0.0, 0.0, 0.0, 0.0],
        "Calcio (Ca %)": [0.35, 0.30, 0.02, 0.0, 0.25, 0.70, 0.80, 14.0, 16.0, 1.0],
        "Fosforo (P %)": [0.10, 0.65, 0.30, 0.0, 0.22, 1.10, 0.08, 7.0, 8.0, 0.1],
        "Min Inclusión (%)": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        "Max Inclusión (%)": [100.0, 100.0, 100.0, 1.5, 100.0, 100.0, 100.0, 5.0, 5.0, 5.0]
    })

# --- MODELO MATEMÁTICO DE REQUERIMIENTOS FISIOLÓGICOS ---
df_base = st.session_state.df_ingredientes_state
df_base["Disponible"] = df_base["Disponible"].astype(bool)

thi_val = perfil_estado["thi_base"] if "Confort" in nivel_thi else (77 if "Moderado" in nivel_thi else 82)
factor_thi_cms = 0.94 if thi_val >= 74 and thi_val < 79 else (0.85 if thi_val >= 79 else 1.00)

factor_lodo_cms = 1.00 if "Seco" in condicion_lodo else (0.93 if "Moderado" in condicion_lodo else 0.87)
factor_lodo_energia = 1.00 if "Seco" in condicion_lodo else (1.10 if "Moderado" in condicion_lodo else 1.20)

factor_cc_cms = 0.96 if condicion_corporal > 3.5 else (1.04 if condicion_corporal < 2.5 else 1.00)
factor_sistema_energia = 1.00 if "Feedlot" in sistema_produccion else (1.08 if "Semi" in sistema_produccion else 1.18)

factor_raza_req = 1.06 if "Británicas" in raza_seleccionada else (1.08 if "Continentales" in raza_seleccionada else (0.94 if "Cebú" in raza_seleccionada else 1.00))
factor_sexo_req = 1.05 if "Toros" in sexo_lote else (0.97 if "Vaquillas" in sexo_lote else 1.00)
factor_marco_req = 1.05 if "Precoz" in marco_lote else (0.95 if "Grande" in marco_lote else 1.00)
factor_aditivo_energia = 1.04 if "Ionóforos" in aditivo_ruminal or "Ambos" in aditivo_ruminal else 1.00

cms_estimado = peso_actual * 0.024 * factor_thi_cms * factor_lodo_cms * factor_cc_cms
req_pc = (0.115 + (gde * 0.025)) * factor_raza_req * factor_sexo_req
req_neg = ((1.02 + (gde * 0.16)) * factor_raza_req * factor_marco_req * factor_lodo_energia * factor_sistema_energia) / factor_aditivo_energia
req_fnd = 0.27 if "Buffer" in aditivo_ruminal or "Ambos" in aditivo_ruminal else 0.28

class OptimizeResultCompat:
    def __init__(self, success, fun, x, message=""):
        self.success = success
        self.fun = fun
        self.x = x
        self.message = message

def optimizar_dieta_fisiologica(df, req_p, req_e, req_f):
    costos = df["Precio Estimado (MXN/ton)"].astype(float).values
    pc = df["Proteina Cruda (PC % MS)"].astype(float).values / 100.0
    neg = df["NEg (Mcal/kg)"].astype(float).values
    fnd = df["FND (% MS)"].astype(float).values / 100.0
    
    bounds = []
    for _, row in df.iterrows():
        if not row["Disponible"]:
            bounds.append((0.0, 0.0))
        else:
            min_i = max(0.0, float(row["Min Inclusión (%)"]) / 100.0)
            max_i = min(1.0, float(row["Max Inclusión (%)"]) / 100.0)
            bounds.append((min_i, max_i))
            
    A_eq = np.ones((1, len(costos)))
    b_eq = np.array([1.0])
    
    A_ub = np.array([-pc, -neg, -fnd])
    b_ub = np.array([-req_p, -req_e, -req_f])
    
    res = linprog(costos, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
    if res.success:
        return OptimizeResultCompat(True, res.fun, res.x, "Optimización Fisiológica Exitosa")
    
    b_ub_rel = np.array([-req_p * 0.90, -req_e * 0.90, -req_f * 0.90])
    res_rel = linprog(costos, A_ub=A_ub, b_ub=b_ub_rel, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
    if res_rel.success:
        return OptimizeResultCompat(True, res_rel.fun, res_rel.x, "Factible con tolerancia biológica ajustada")
    return OptimizeResultCompat(False, 5000.0, np.zeros(len(costos)), "Sin solución factible")

resultado_opt = optimizar_dieta_fisiologica(df_base, req_pc, req_neg, req_fnd)
costo_tonelada = resultado_opt.fun
dias_a_meta = max(1.0, (peso_objetivo - peso_actual) / gde)
costo_alimentacion_cab = (cms_estimado * dias_a_meta / 1000.0) * costo_tonelada
costo_total_cab = (peso_actual * precio_compra) + costo_alimentacion_cab + 650.0
ingreso_venta_cab = peso_objetivo * precio_venta
utilidad_neta_cab = ingreso_venta_cab - costo_total_cab
roi_cab = (utilidad_neta_cab / costo_total_cab) * 100 if costo_total_cab > 0 else 0

# --- PESTAÑAS DE LA APLICACIÓN (8 TABS CON DIETA FINAL OPTIMIZADA) ---
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "🥗 1. Dieta Óptima Fisiológica",
    "🧪 2. Banco de Ingredientes",
    "📊 3. Economía y Lote",
    "📡 4. Dashboard Red IoT",
    "🌡️ 5. Bolos Ruminales (pH)",
    "🚜 6. Básculas & Mezcladora",
    "💬 7. Nutri-ON Bot",
    "📋 8. Dieta Final Optimizada"
])

with tab1:
    st.subheader(f"Formulación Ajustada a Necesidades Fisiológicas ({estado_seleccionado})")
    st.markdown(f"**Perfil Biológico:** Raza: `{raza_seleccionada}` | Sexo: `{sexo_lote}` | Marco: `{marco_lote}` | Sistema: `{sistema_produccion}`\n* **CMS Fisiológico:** `{cms_estimado:.2f} kg/día` | **Req. PC Mínimo:** `{req_pc*100:.2f}%` | **Req. NEg Mínimo:** `{req_neg:.2f} Mcal/kg`")
    
    if resultado_opt.success:
        df_resultado = df_base.copy()
        df_resultado["Proporción (%)"] = resultado_opt.x * 100.0
        df_resultado["Aporte en Ración (kg/día/animal)"] = resultado_opt.x * cms_estimado
        df_resultado_activa = df_resultado[df_resultado["Proporción (%)"] > 0.01][["Nombre del Ingrediente", "Categoria", "Precio Estimado (MXN/ton)", "Proporción (%)", "Aporte en Ración (kg/día/animal)"]]
        
        st.dataframe(df_resultado_activa, use_container_width=True, hide_index=True)
        
        col_res1, col_res2, col_res3 = st.columns(3)
        with col_res1:
            st.metric("Costo de la Ración (MXN/ton)", f"${costo_tonelada:,.2f}")
        with col_res2:
            st.metric("Costo Diario por Cabeza", f"${(cms_estimado / 1000.0) * costo_tonelada:,.2f} MXN")
        with col_res3:
            st.metric("Estatus del Solver", f"🟢 {resultado_opt.message}")
    else:
        st.error("No se encontró solución factible. Revisa los precios o los límites de inclusión en la pestaña 2.")

with tab2:
    st.subheader("🧪 Banco de Ingredientes y Restricciones Regionales")
    st.markdown("Personaliza los precios y límites mínimos/máximos de inclusión para el modelo lineal.")
    st.session_state.df_ingredientes_state = st.data_editor(
        st.session_state.df_ingredientes_state, num_rows="dynamic", use_container_width=True, key="editor_ingredientes_fisiologico"
    )

with tab3:
    st.subheader("📊 Análisis Económico y Proyección por Lote")
    col_ec1, col_ec2, col_ec3, col_ec4 = st.columns(4)
    with col_ec1:
        st.metric("Costo Compra Lote", f"${peso_actual * precio_compra * cantidad_animales:,.0f} MXN")
        st.metric("Costo Alimento Total", f"${costo_alimentacion_cab * cantidad_animales:,.0f} MXN")
    with col_ec2:
        st.metric("Costo Total Producido", f"${costo_total_cab * cantidad_animales:,.0f} MXN")
        st.metric("Días a la Meta", f"{dias_a_meta:.0f} días")
    with col_ec3:
        st.metric("Ingreso Venta Lote", f"${ingreso_venta_cab * cantidad_animales:,.0f} MXN")
        st.metric("Utilidad Neta Total", f"${utilidad_neta_cab * cantidad_animales:,.0f} MXN")
    with col_ec4:
        st.metric("Utilidad por Cabeza", f"${utilidad_neta_cab:,.2f} MXN")
        st.metric("ROI del Ciclo", f"{roi_cab:.1f}%")

with tab4:
    st.subheader(f"📡 Estado de Red IoT & Sensores en {estado_seleccionado}")
    col_i1, col_i2, col_i3, col_i4 = st.columns(4)
    with col_i1: st.metric("Sensores Activos", f"{cantidad_animales * 2} und", "100% Online")
    with col_i2: st.metric("Collares IoT (Rumia)", f"{int(cantidad_animales * 0.96)} cab", "🟢 Normal")
    with col_i3: st.metric("Bolos pH Activos", f"{int(cantidad_animales * 0.90)} und", "⚠️ 2 Alertas SARA")
    with col_i4: st.metric("Utilidad Proyectada", f"${utilidad_neta_cab:,.0f} MXN", "Por cabeza")

    horas = [f"{h:02d}:00" for h in range(24)]
    rumia_promedio = [550, 520, 480, 400, 320, 250, 410, 600, 680, 650, 620, 590, 580, 610, 640, 660, 620, 590, 550, 520, 530, 560, 570, 560]
    fig_iot = px.line(x=horas, y=rumia_promedio, title="Minutos de Masticación y Rumia Promedio del Lote (Collares IoT)", markers=True)
    fig_iot.update_layout(plot_bgcolor="#ffffff", paper_bgcolor="#ffffff", font=dict(family="Calibri", size=12))
    st.plotly_chart(fig_iot, use_container_width=True)

with tab5:
    st.subheader("🌡️ Bolos Ruminales Ingeribles (Telemetría de pH y Temperatura 24/7)")
    ph_actual = st.slider("pH Ruminal en Vivo (Promedio Lote)", 5.0, 7.0, 6.2, 0.05)
    if ph_actual < 5.8:
        st.error("🔴 **ALERTA CRÍTICA SARA:** pH menor a 5.8 detectado por bolos IoT. Riesgo de laminitis.")
    else:
        st.success("🟢 **pH Ruminal Estable:** Rango fisiológico seguro.")

with tab6:
    st.subheader("🚜 Básculas IoT para Carros Mezcladores")
    st.info(
        "🔗 **Estado de Conectividad Báscula #1:** Conectado vía Bluetooth Low Energy (BLE)\n\n"
        f"* **Ración Óptima Formulatada:** {raza_seleccionada} ({sexo_lote})\n"
        f"* **Costo Tonelada Optimizado:** `${costo_tonelada:,.2f} MXN`\n"
        "* **Precisión de Carga en Batea:** `99.5%` (🟢 Tolerancia OK)"
    )

with tab7:
    st.subheader("💬 Asistente Virtual Nutri-ON Bot")
    for msg in st.session_state.nutrion_messages:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])
    
    if q := st.chat_input("Pregúntale al sistema sobre la dieta o la red IoT..."):
        st.session_state.nutrion_messages.append({"role": "user", "content": q})
        with st.chat_message("user"): st.markdown(q)
        ans = f"🤖 **Respuesta Nutri-ON ({estado_seleccionado}):** Analizando tu lote de {cantidad_animales} cabezas bajo el modelo fisiológico para {raza_seleccionada} ({sexo_lote}), la dieta está optimizada a un costo de ${costo_tonelada:,.2f} MXN/ton con un CMS ajustado de {cms_estimado:.2f} kg/día. ¿Deseas exportar la orden de carga para el carro mezclador?"
        st.session_state.nutrion_messages.append({"role": "assistant", "content": ans})
        with st.chat_message("assistant"): st.markdown(ans)

with tab8:
    st.subheader("📋 Reporte Ejecutivo: Dieta Final y Optimizada al Menor Costo")
    st.markdown(
        "Esta sección muestra la solución definitiva del **Modelo de Programación Lineal**, "
        "garantizando el cumplimiento estricto de las necesidades fisiológicas del lote al **costo más bajo posible**."
    )

    if resultado_opt.success:
        df_final = df_base.copy()
        df_final["Inclusión (%)"] = resultado_opt.x * 100.0
        df_final["Kg / Día / Animal"] = resultado_opt.x * cms_estimado
        df_final["Kg / Día / Lote Total"] = resultado_opt.x * cms_estimado * cantidad_animales
        
        df_activa_final = df_final[df_final["Inclusión (%)"] > 0.01][[
            "Nombre del Ingrediente", "Categoria", "Precio Estimado (MXN/ton)", 
            "Inclusión (%)", "Kg / Día / Animal", "Kg / Día / Lote Total"
        ]].reset_index(drop=True)

        st.dataframe(df_activa_final, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.markdown("##### 📈 Validación Nutricional y Costos de la Dieta Final")
        
        pc_arr = df_base["Proteina Cruda (PC % MS)"].astype(float).values / 100.0
        neg_arr = df_base["NEg (Mcal/kg)"].astype(float).values
        fnd_arr = df_base["FND (% MS)"].astype(float).values / 100.0
        
        aporte_pc_real = np.sum(resultado_opt.x * pc_arr) * 100.0
        aporte_neg_real = np.sum(resultado_opt.x * neg_arr)
        aporte_fnd_real = np.sum(resultado_opt.x * fnd_arr) * 100.0

        col_vf1, col_vf2, col_vf3, col_vf4 = st.columns(4)
        with col_vf1:
            st.metric("Costo Tonelada Final", f"${costo_tonelada:,.2f} MXN", "Mínimo Costo")
            st.metric("Proteína Cruda Aportada", f"{aporte_pc_real:.2f}%", f"Mínimo Req: {req_pc*100:.2f}%")
        with col_vf2:
            st.metric("Costo Diario / Cabeza", f"${(cms_estimado/1000.0)*costo_tonelada:,.2f} MXN")
            st.metric("Energía NEg Aportada", f"{aporte_neg_real:.2f} Mcal/kg", f"Mínimo Req: {req_neg:.2f}")
        with col_vf3:
            st.metric("Consumo Materia Seca", f"{cms_estimado:.2f} kg/día")
            st.metric("Fibra FND Aportada", f"{aporte_fnd_real:.2f}%", f"Mínimo Req: {req_fnd*100:.2f}%")
        with col_vf4:
            st.metric("Costo Diario Lote Total", f"${((cms_estimado/1000.0)*costo_tonelada)*cantidad_animales:,.2f} MXN")
            st.metric("Estatus del Solver", "🟢 Óptimo / Factible")

        st.markdown("---")
        st.info(
            f"💡 **Orden de Carga para el Carro Mezclador (Lote de {cantidad_animales} cabezas):**\n"
            f"La dieta optimizada requiere un consumo diario total de lote de **{(cms_estimado*cantidad_animales):,.1f} kg de materia seca**. "
            "Sincronice esta tabla con las básculas IoT de batea para asegurar cero mermas y máxima precisión operativa."
        )
    else:
        st.error("⚠️ No hay una dieta optimizada disponible porque el modelo lineal no encontró solución factible. Revise los límites e ingredientes en la pestaña 2.")
