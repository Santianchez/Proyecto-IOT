import streamlit as st
from influxdb_client import InfluxDBClient # type: ignore
import pandas as pd # type: ignore

# Configuración desde archivo local
# Asegúrate que este archivo config.py esté en el mismo directorio o ajusta la importación
try:
    from config import INFLUX_URL, INFLUX_TOKEN, ORG, BUCKET
except ImportError:
    st.error("Error: No se pudo encontrar el archivo de configuración 'config.py' o las variables no están definidas.")
    st.stop()

# --- INICIO: FUNCIONES PARA CONSULTAR DATOS PARA STREAMLIT ---
def query_sensor_data_for_streamlit(measurement, field, range_minutes=60, limit=100):
    """
    Consulta datos de series temporales desde InfluxDB para un measurement y field específico.
    Devuelve un DataFrame de Pandas.
    """
    # Validaciones básicas de entrada
    if not all([INFLUX_URL, INFLUX_TOKEN, ORG, BUCKET]):
        st.error("Las credenciales de InfluxDB no están completamente configuradas.")
        return pd.DataFrame()
    if not measurement or not field:
        st.warning(f"Measurement ('{measurement}') o field ('{field}') no especificado para la consulta.")
        return pd.DataFrame()

    client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=ORG)
    query_api = client.query_api()

    # Query Flux ajustada para usar los nombres de campo y medición correctos
    # Tomados del PDF del proyecto integrador para el Anexo Técnico [cite: 37]
    query = f'''
    from(bucket: "{BUCKET}")
      |> range(start: -{range_minutes}m)
      |> filter(fn: (r) => r["_measurement"] == "{measurement}" and r["_field"] == "{field}")
      |> sort(columns: ["_time"], desc: true)
      |> limit(n:{limit})
    '''
    try:
        result = query_api.query_data_frame(query)
        if isinstance(result, list):
            result = pd.concat(result) if result else pd.DataFrame() # type: ignore
        if not result.empty:
            # Seleccionar y renombrar columnas relevantes
            if "_time" in result.columns and "_value" in result.columns:
                return result[["_time", "_value"]].rename(columns={"_time": "Timestamp", "_value": field})
            else:
                st.warning(f"Columnas '_time' o '_value' no encontradas en la consulta para {measurement}/{field}.")
                return pd.DataFrame()
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error al consultar datos para '{measurement}/{field}' desde InfluxDB: {e}")
        return pd.DataFrame()
    finally:
        client.close()

def calculate_stats(df, column_name):
    """Calcula estadísticas básicas para una columna de un DataFrame."""
    if not df.empty and column_name in df.columns and not df[column_name].empty:
        stats = {
            "Mínimo": round(df[column_name].min(), 2),
            "Máximo": round(df[column_name].max(), 2),
            "Promedio": round(df[column_name].mean(), 2),
        }
        if len(df[column_name]) > 1:
            stats["Última Lectura"] = round(df[column_name].iloc[0], 2) # Asumiendo datos ordenados desc por tiempo
            stats["Lectura Anterior"] = round(df[column_name].iloc[1], 2)
            # Tendencia simple
            if stats["Última Lectura"] > stats["Lectura Anterior"]:
                stats["Tendencia"] = "Subiendo ⬆️"
            elif stats["Última Lectura"] < stats["Lectura Anterior"]:
                stats["Tendencia"] = "Bajando ⬇️"
            else:
                stats["Tendencia"] = "Estable ➡️"
        elif len(df[column_name]) == 1:
             stats["Última Lectura"] = round(df[column_name].iloc[0], 2)
        return stats
    return {}
# --- FIN: FUNCIONES PARA CONSULTAR DATOS ---

# --- CONFIGURACIÓN DE LA PÁGINA STREAMLIT ---
st.set_page_config(page_title="🥕 Monitoreo de Microcultivos Urbanos", layout="wide", initial_sidebar_state="expanded")
st.title("🥕 Monitoreo Inteligente de Microcultivos Urbanos")
st.markdown("""
Bienvenido al sistema de monitoreo para tus microcultivos. Esta aplicación complementa el dashboard principal de Grafana,
permitiéndote explorar datos crudos recientes, ver estadísticas clave y obtener recomendaciones para el cuidado de tus plantas.
""")
st.info(f"ℹ️ Mostrando datos del bucket: `{BUCKET}` en la organización: `{ORG}`.")

# --- SECCIÓN DE ENLACES A PANELES DE GRAFANA ---
st.header("📊 Paneles Detallados en Grafana")
st.markdown("Haz clic en los siguientes enlaces para ver las visualizaciones detalladas en una nueva pestaña directamente en Grafana.")

# URLs de tus paneles de Grafana (MODIFICAR ESTAS URLS)
# Debes obtener la URL "Share" > "Embed" (solo la URL del src) o "Share" > "Link" (modo d-solo) para CADA panel.
# La estructura es: https://TU_USUARIO.grafana.net/d-solo/ID_DEL_DASHBOARD/NOMBRE_DASHBOARD?orgId=1&panelId=ID_DEL_PANEL_ESPECIFICO&refresh=10s&theme=light
# (Los parámetros from y to son opcionales si quieres que Grafana maneje el tiempo por defecto del panel)

grafana_urls = {
    "Temperatura (DHT22)": "URL_GRAFANA_PANEL_TEMPERATURA_LINEA", # ¡TU URL AQUÍ!
    "Índice de Calor (DHT22)": "URL_GRAFANA_PANEL_INDICE_CALOR_LINEA", # ¡TU URL AQUÍ!
    "Humedad (DHT22)": "URL_GRAFANA_PANEL_HUMEDAD_LINEA", # ¡TU URL AQUÍ!
    "Niveles de Temperatura (General)": "URL_GRAFANA_PANEL_TEMPERATURA_NIVELES_LINEA", # ¡TU URL AQUÍ!
    "Mapa de Calor de Humedad": "URL_GRAFANA_PANEL_HUMEDAD_HEATMAP", # ¡TU URL AQUÍ!
    "Mapa de Calor de Temperatura": "URL_GRAFANA_PANEL_TEMPERATURA_HEATMAP", # ¡TU URL AQUÍ!
    "Intensidad de Luz UV (VEML6070)": "URL_GRAFANA_PANEL_UV_LINEA" # ¡TU URL AQUÍ!
}

# Mostrar los enlaces
for panel_name, panel_url in grafana_urls.items():
    if panel_url == f"URL_GRAFANA_PANEL_{panel_name.upper().replace(' (DHT22)', '').replace(' (VEML6070)', '').replace(' ', '_')}" or not panel_url.startswith("http"):
        st.warning(f"⚠️ URL para '{panel_name}' no configurada. Por favor, actualiza la URL en el código de `app.py`.")
        st.markdown(f"### {panel_name}\n*URL no configurada*")
    else:
        st.markdown(
            f"""
            ### {panel_name}
            Debido a políticas de seguridad, el panel podría no mostrarse aquí directamente.
            [Haz clic aquí para abrir el panel de '{panel_name}' en una nueva pestaña.]({panel_url})
            """,
            unsafe_allow_html=True
        )
st.markdown("---")

# --- SECCIÓN DE DATOS CRUDOS Y ESTADÍSTICAS ---
st.header("📝 Datos Crudos Recientes y Estadísticas")
range_minutes_data = st.select_slider(
    "Selecciona el rango de tiempo para datos crudos y estadísticas (últimos minutos):",
    options=[10, 30, 60, 120, 180, 240, 360],
    value=60
)

# Nombres de measurement y field según el Anexo Técnico del PDF del proyecto [cite: 37]
# y tus visualizaciones de Grafana [cite: 1, 2]
temp_measurement, temp_field = "airSensor", "temperature"
hum_measurement, hum_field = "airSensor", "humidity"
uv_measurement, uv_field = "uv_sensor", "uv_index" # Asumiendo 'uv_index' para el valor procesado. Si usas 'uv_raw', ajústalo. [cite: 2]

# Consultar datos
temp_df = query_sensor_data_for_streamlit(temp_measurement, temp_field, range_minutes_data)
hum_df = query_sensor_data_for_streamlit(hum_measurement, hum_field, range_minutes_data)
uv_df = query_sensor_data_for_streamlit(uv_measurement, uv_field, range_minutes_data)

# Calcular estadísticas
stats_temp = calculate_stats(temp_df, temp_field)
stats_hum = calculate_stats(hum_df, hum_field)
stats_uv = calculate_stats(uv_df, uv_field)

# Mostrar en columnas
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader(f"🌡️ Temperatura ({temp_field})")
    if not temp_df.empty:
        st.dataframe(temp_df, height=200, use_container_width=True)
        st.write("**Estadísticas:**")
        if stats_temp: st.json(stats_temp)
        else: st.caption("No hay suficientes datos para estadísticas.")
    else:
        st.caption(f"Sin datos de '{temp_field}' en los últimos {range_minutes_data} minutos.")

with col2:
    st.subheader(f"💧 Humedad ({hum_field})")
    if not hum_df.empty:
        st.dataframe(hum_df, height=200, use_container_width=True)
        st.write("**Estadísticas:**")
        if stats_hum: st.json(stats_hum)
        else: st.caption("No hay suficientes datos para estadísticas.")
    else:
        st.caption(f"Sin datos de '{hum_field}' en los últimos {range_minutes_data} minutos.")

with col3:
    st.subheader(f"☀️ Índice UV ({uv_field})")
    if not uv_df.empty:
        st.dataframe(uv_df, height=200, use_container_width=True)
        st.write("**Estadísticas:**")
        if stats_uv: st.json(stats_uv)
        else: st.caption("No hay suficientes datos para estadísticas.")
    else:
        st.caption(f"Sin datos de '{uv_field}' en los últimos {range_minutes_data} minutos.")
st.markdown("---")

# --- SECCIÓN DE RECOMENDACIONES AUTOMATIZADAS ---
st.header("💡 Recomendaciones para tus Microcultivos")

recommendations = []
# Usar las últimas lecturas de las estadísticas calculadas
last_temp = stats_temp.get("Última Lectura") if stats_temp else None
last_hum = stats_hum.get("Última Lectura") if stats_hum else None
last_uv = stats_uv.get("Última Lectura") if stats_uv else None

# Lógica de recomendaciones (ajusta estos umbrales según sea necesario para microcultivos específicos)
if last_hum is not None:
    if last_hum < 35: # Ejemplo de umbral para microcultivos
        recommendations.append("💧 **Humedad Baja:** La humedad ambiental es inferior al 35%. Considera aumentar la humedad, por ejemplo, pulverizando agua cerca o agrupando plantas.")
    elif last_hum > 75: # Ejemplo de umbral
        recommendations.append("💧 **Humedad Alta:** La humedad ambiental es superior al 75%. Asegura una buena ventilación para prevenir moho.")
else:
    recommendations.append("❓ Humedad: No hay datos recientes para generar recomendaciones.")

if last_temp is not None:
    if last_temp > 28: # Ejemplo de umbral
        recommendations.append("🌡️ **Temperatura Alta:** La temperatura supera los 28°C. Si es posible, provee sombra o mejora la ventilación.")
    elif last_temp < 15: # Ejemplo de umbral
        recommendations.append("🌡️ **Temperatura Baja:** La temperatura es inferior a 15°C. Protege los cultivos del frío si son sensibles.")
else:
    recommendations.append("❓ Temperatura: No hay datos recientes para generar recomendaciones.")

if last_uv is not None:
    if last_uv > 7: # Ejemplo de índice UV (escala de 0-11+)
        recommendations.append("☀️ **Radiación UV Alta:** El índice UV es superior a 7. Considera proveer sombra parcial, especialmente durante las horas pico de sol.")
    elif last_uv < 2:
        recommendations.append("☀️ **Radiación UV Baja:** El índice UV es inferior a 2. Asegúrate de que los cultivos reciban suficiente luz indirecta o considera suplementos lumínicos si es necesario para su etapa de crecimiento.")
else:
    recommendations.append("❓ Índice UV: No hay datos recientes para generar recomendaciones.")

if not recommendations or all("❓" in rec for rec in recommendations):
    st.success("✅ No hay recomendaciones específicas en este momento o no hay datos suficientes.")
else:
    for rec in recommendations:
        if "❓" not in rec:
            st.info(rec)
        else:
            st.caption(rec)

# --- PIE DE PÁGINA ---
st.markdown("---")
st.caption("Proyecto Integrador - Computación Física e Internet de las Cosas | Diseño Interactivo")
st.caption(f"Hora actual del servidor: {pd.Timestamp.now(tz='America/Bogota').strftime('%Y-%m-%d %H:%M:%S %Z')}")
