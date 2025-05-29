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
    if not all([INFLUX_URL, INFLUX_TOKEN, ORG, BUCKET]):
        st.error("Las credenciales de InfluxDB no están completamente configuradas.")
        return pd.DataFrame()
    if not measurement or not field:
        st.warning(f"Measurement ('{measurement}') o field ('{field}') no especificado para la consulta.")
        return pd.DataFrame()

    client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=ORG)
    query_api = client.query_api()
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
            stats["Última Lectura"] = round(df[column_name].iloc[0], 2)
            stats["Lectura Anterior"] = round(df[column_name].iloc[1], 2)
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

grafana_urls = {
    "Humidity vs Temperature": "https://santianchez05.grafana.net/d-solo/09ff8bd6-e9d7-4852-9bc7-c7ae01600f54/humidity-vs-temperature?orgId=1&from=1747325219746&to=1747368419746&timezone=browser&panelId=1&__feature.dashboardSceneSolo=true",
    "Heat Index": "https://santianchez05.grafana.net/d-solo/09ff8bd6-e9d7-4852-9bc7-c7ae01600f54/humidity-vs-temperature?orgId=1&from=1747325219746&to=1747368419746&timezone=browser&panelId=3&__feature.dashboardSceneSolo=true",
    "Humidity levels": "https://santianchez05.grafana.net/d-solo/09ff8bd6-e9d7-4852-9bc7-c7ae01600f54/humidity-vs-temperature?orgId=1&from=1747325219746&to=1747368419746&timezone=browser&panelId=4&__feature.dashboardSceneSolo=true",
    "Temperature levels": "https://santianchez05.grafana.net/d-solo/09ff8bd6-e9d7-4852-9bc7-c7ae01600f54/humidity-vs-temperature?orgId=1&from=1747325219746&to=1747368419746&timezone=browser&panelId=5&__feature.dashboardSceneSolo=true",
    "Humidity Heatmap": "https://santianchez05.grafana.net/d-solo/09ff8bd6-e9d7-4852-9bc7-c7ae01600f54/humidity-vs-temperature?orgId=1&from=1747325219746&to=1747368419746&timezone=browser&panelId=6&__feature.dashboardSceneSolo=true",
    "Temperature Heatmap": "https://santianchez05.grafana.net/d-solo/09ff8bd6-e9d7-4852-9bc7-c7ae01600f54/humidity-vs-temperature?orgId=1&from=1747325219746&to=1747368419746&timezone=browser&panelId=7&__feature.dashboardSceneSolo=true",
    "UV Light Intensity": "https://santianchez05.grafana.net/d-solo/09ff8bd6-e9d7-4852-9bc7-c7ae01600f54/humidity-vs-temperature?orgId=1&from=1747325219746&to=1747368419746&timezone=browser&panelId=2&__feature.dashboardSceneSolo=true"
}

for panel_name, panel_url in grafana_urls.items():
    if not panel_url.startswith("http"): # Simple check if URL is placeholder
        st.warning(f"⚠️ URL para '{panel_name}' parece no estar configurada correctamente. Por favor, verifica la URL en el código de `app.py`.")
        st.markdown(f"### {panel_name}\n*URL no configurada o incorrecta*")
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

temp_measurement, temp_field = "airSensor", "temperature"
hum_measurement, hum_field = "airSensor", "humidity"
uv_measurement, uv_field = "uv_sensor", "uv_index" # Asumiendo 'uv_index' para el valor procesado. Si usas 'uv_raw', ajústalo.

temp_df = query_sensor_data_for_streamlit(temp_measurement, temp_field, range_minutes_data)
hum_df = query_sensor_data_for_streamlit(hum_measurement, hum_field, range_minutes_data)
uv_df = query_sensor_data_for_streamlit(uv_measurement, uv_field, range_minutes_data)

stats_temp = calculate_stats(temp_df, temp_field)
stats_hum = calculate_stats(hum_df, hum_field)
stats_uv = calculate_stats(uv_df, uv_field)

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
last_temp = stats_temp.get("Última Lectura") if stats_temp else None
last_hum = stats_hum.get("Última Lectura") if stats_hum else None
last_uv = stats_uv.get("Última Lectura") if stats_uv else None

if last_hum is not None:
    if last_hum < 35:
        recommendations.append("💧 **Humedad Baja:** La humedad ambiental es inferior al 35%. Considera aumentar la humedad.")
    elif last_hum > 75:
        recommendations.append("💧 **Humedad Alta:** La humedad ambiental es superior al 75%. Asegura una buena ventilación.")
else:
    recommendations.append("❓ Humedad: No hay datos recientes para generar recomendaciones.")

if last_temp is not None:
    if last_temp > 28:
        recommendations.append("🌡️ **Temperatura Alta:** La temperatura supera los 28°C. Considera proveer sombra o mejorar la ventilación.")
    elif last_temp < 15:
        recommendations.append("🌡️ **Temperatura Baja:** La temperatura es inferior a 15°C. Protege los cultivos del frío.")
else:
    recommendations.append("❓ Temperatura: No hay datos recientes para generar recomendaciones.")

if last_uv is not None:
    # La escala del índice UV va de 0 a 11+. Umbrales de ejemplo.
    if last_uv > 7:
        recommendations.append("☀️ **Radiación UV Alta (Índice > 7):** Considera proveer sombra parcial.")
    elif last_uv < 2:
        recommendations.append("☀️ **Radiación UV Baja (Índice < 2):** Asegura suficiente exposición a la luz indirecta.")
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
st.caption(f"Hora actual del servidor (aproximada): {pd.Timestamp.now(tz='America/Bogota').strftime('%Y-%m-%d %H:%M:%S %Z')}")
