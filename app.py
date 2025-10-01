import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime
try:
    import streamlit_authenticator as stauth
except Exception:
    st.warning("Falta 'streamlit-authenticator'. Ejecuta: pip install streamlit-authenticator")
    st.stop()

st.set_page_config(page_title="Dashboard Grupo Maipú", page_icon="📈", layout="wide", initial_sidebar_state="expanded")

# --- Credenciales desde .streamlit/credentials.toml (formato simple) ---
from configparser import ConfigParser
creds_path = os.path.join(".streamlit", "credentials.toml")
config = ConfigParser()
if not os.path.exists(creds_path):
    st.error("No se encontró .streamlit/credentials.toml. Revisa README para generarlo.")
    st.stop()

with open(creds_path, "r", encoding="utf-8") as f:
    lines = [l.strip() for l in f.readlines() if l.strip()]

cookie_name = "dashboard_gm"
cookie_key = "cambia_esto"
cookie_expiry_days = 7
users = {}
current_section = None
for l in lines:
    if l.startswith("[") and l.endswith("]"):
        current_section = l[1:-1]
        continue
    if current_section == "credentials":
        if l.startswith("cookie_name"):
            cookie_name = l.split("=",1)[1].strip().strip('"')
        if l.startswith("cookie_key"):
            cookie_key = l.split("=",1)[1].strip().strip('"')
        if l.startswith("cookie_expiry_days"):
            cookie_expiry_days = int(l.split("=",1)[1].strip())
    elif current_section and current_section.startswith("users."):
        key = current_section.split(".",1)[1]
        users.setdefault(key, {})
        if "=" in l:
            k,v = l.split("=",1)
            users[key][k.strip()] = v.strip().strip('"')

names = [u.get("name", k) for k,u in users.items()]
usernames = list(users.keys())
passwords = [u.get("password", "") for u in users.values()]
roles = {k: u.get("role","visor") for k,u in users.items()}
emails = {k: u.get("email","") for k,u in users.items()}

credentials = {"usernames": {u: {"name": n, "password": p, "email": emails.get(u,"")} for u,n,p in zip(usernames,names,passwords)}}

authenticator = stauth.Authenticate(credentials, cookie_name, cookie_key, cookie_expiry_days)
name, authentication_status, username = authenticator.login(fields={'Form name':'Ingreso', 'Username':'Usuario', 'Password':'Contraseña'})

if not authentication_status:
    if authentication_status is False:
        st.error("Usuario o contraseña incorrectos")
    st.stop()

st.sidebar.success(f"Conectado: {name} ({username}) · Rol: {roles.get(username,'visor')}")

with st.sidebar.expander("Cargar Datos", expanded=True):
    datos_fuente = st.radio("Fuente de datos", ["Subir archivo","Data local (./data)"])
    df = None
    if datos_fuente == "Subir archivo":
        file = st.file_uploader("Carga Excel/CSV (no se guarda en el servidor)", type=["xlsx","xls","csv"])
        if file is not None:
            try:
                if file.name.endswith(".csv"):
                    df = pd.read_csv(file)
                else:
                    df = pd.read_excel(file)
            except Exception as e:
                st.error(f"Error leyendo archivo: {e}")
    else:
        path = st.text_input("Ruta local (por ej.: data/ejemplo.xlsx)", value="data/ejemplo.xlsx")
        if st.button("Cargar ejemplo"):
            try:
                if path.endswith(".csv"):
                    df = pd.read_csv(path)
                else:
                    df = pd.read_excel(path)
            except Exception as e:
                st.error(f"Error leyendo {path}: {e}")

if df is None:
    st.info("Sube un archivo para comenzar. Tus datos permanecen en memoria y no se almacenan en el servidor.")
    st.stop()

cols = [c.lower() for c in df.columns]
mapa = {
    'cliente': next((c for c in df.columns if c.lower() in ['cliente','customer','client','razon_social','nombre_cliente']), None),
    'fecha': next((c for c in df.columns if c.lower() in ['fecha','date','order_date','periodo']), None),
    'monto': next((c for c in df.columns if c.lower() in ['monto','importe','venta','sales','revenue','amount','total']), None),
    'categoria': next((c for c in df.columns if c.lower() in ['categoria','segmento','producto','familia','category','segment']), None),
    'region': next((c for c in df.columns if c.lower() in ['region','zona','ciudad','country','pais','comuna','provincia']), None),
}
if mapa['fecha']:
    try:
        df[mapa['fecha']] = pd.to_datetime(df[mapa['fecha']])
    except:  # noqa
        pass

with st.sidebar:
    st.markdown("---")
    st.subheader("Filtros")
    if mapa['fecha'] and pd.api.types.is_datetime64_any_dtype(df[mapa['fecha']]):
        min_d, max_d = df[mapa['fecha']].min(), df[mapa['fecha']].max()
        date_range = st.date_input("Rango de fechas", value=(min_d.date(), max_d.date()))
        if isinstance(date_range, tuple) and len(date_range) == 2:
            df = df[(df[mapa['fecha']] >= pd.to_datetime(date_range[0])) & (df[mapa['fecha']] <= pd.to_datetime(date_range[1]))]
    if mapa['region']:
        regiones = sorted(df[mapa['region']].dropna().astype(str).unique())[:500]
        sel_reg = st.multiselect("Región/Zona", regiones)
        if sel_reg:
            df = df[df[mapa['region']].astype(str).isin(sel_reg)]
    if mapa['categoria']:
        cats = sorted(df[mapa['categoria']].dropna().astype(str).unique())[:500]
        sel_cat = st.multiselect("Categoría/Segmento", cats)
        if sel_cat:
            df = df[df[mapa['categoria']].astype(str).isin(sel_cat)]

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Registros", f"{len(df):,}")
with col2:
    if mapa['monto'] and pd.api.types.is_numeric_dtype(df[mapa['monto']]):
        st.metric("Ventas (Σ)", f"${df[mapa['monto']].sum():,.0f}")
    else:
        st.metric("Campos numéricos", df.select_dtypes(include=np.number).shape[1])
with col3:
    if mapa['cliente']:
        st.metric("Clientes únicos", df[mapa['cliente']].nunique())
    else:
        st.metric("Columnas", df.shape[1])
with col4:
    if mapa['fecha'] and pd.api.types.is_datetime64_any_dtype(df[mapa['fecha']]):
        st.metric("Periodo", f"{df[mapa['fecha']].min().date()} → {df[mapa['fecha']].max().date()}")
    else:
        st.metric("Periodo", "No disponible")

st.markdown("---")

if mapa['monto'] and mapa['fecha'] and pd.api.types.is_datetime64_any_dtype(df[mapa['fecha']]) and pd.api.types.is_numeric_dtype(df[mapa['monto']]):
    df_ts = df.groupby(pd.Grouper(key=mapa['fecha'], freq='MS'))[mapa['monto']].sum().reset_index()
    fig = px.line(df_ts, x=mapa['fecha'], y=mapa['monto'], title="Ventas por mes")
    st.plotly_chart(fig, use_container_width=True)

if mapa['categoria'] and mapa['monto'] and pd.api.types.is_numeric_dtype(df[mapa['monto']]):
    top_cat = df.groupby(mapa['categoria'])[mapa['monto']].sum().nlargest(10).reset_index()
    fig2 = px.bar(top_cat, x=mapa['categoria'], y=mapa['monto'], title="Top categorías por ventas")
    st.plotly_chart(fig2, use_container_width=True)

if 'lat' in cols and 'lon' in cols:
    st.map(df.rename(columns={'lat':'lat','lon':'lon'})[['lat','lon']].dropna().head(5000))

st.subheader("Detalle de datos filtrados")
st.dataframe(df.head(1000))

role = {k: users[k].get("role","visor") for k in users}.get(username, "visor")
if role in ["admin","analista"]:
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Descargar CSV filtrado", csv, file_name=f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", mime="text/csv")

authenticator.logout(location='sidebar')
