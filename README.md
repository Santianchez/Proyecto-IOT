#  мониторинг интеллектуальных городских микрокультур (Proyecto Integrador)

Este proyecto, desarrollado para el curso "Computación Física e Интернет вещей" de la carrera de Diseño Interactivo, presenta un sistema de monitoreo ambiental para microcultivos urbanos, enfocado en apoyar prácticas sostenibles de cultivo y contribuir a la seguridad alimentaria.

## 🌱 Concepto del Proyecto

El sistema permite a los usuarios supervisar en tiempo real las condiciones ambientales críticas para el crecimiento de microcultivos en entornos domésticos o comunitarios. A través de la recolección de datos de temperatura, humedad ambiental y radiación ultravioleta, se busca empoderar a los agricultores urbanos con información valiosa para la toma de decisiones informadas, optimizando el cuidado de sus plantas y mejorando la producción.

## 🛠️ Tecnologías Utilizadas

* **Microcontrolador:** ESP32-S3 (o ESP8266 como se ve en una de tus gráficas de UV [cite: 2])
* **Sensores:**
    * DHT22 (Temperatura y Humedad Ambiental)
    * VEML6070 (Radiación Ultravioleta)
* **Base de Datos:** InfluxDB Cloud (para almacenamiento de series temporales)
* **Visualización Principal (Dashboard):** Grafana (con 7 paneles especializados)
* **Aplicación Web Complementaria:** Streamlit (para visualización de datos crudos, análisis estadísticos básicos y recomendaciones automatizadas)
* **Lenguaje de Programación (Backend y App):** Python
* **Broker MQTT (si aplica en tu arquitectura completa):** MyMQTT (mencionado en el PDF del curso [cite: 5])

## 📄 Descripción de la Solución

La solución integral consta de:

1.  **Sistema de Captura de Datos:** Un microcontrolador ESP32 (o similar) conectado a los sensores DHT22 y VEML6070 recopila periódicamente los datos ambientales.
2.  **Almacenamiento en la Nube:** Los datos son enviados y almacenados en una instancia de InfluxDB Cloud.
3.  **Dashboard en Grafana:** Un tablero de control principal en Grafana, accesible mediante URL, presenta 7 visualizaciones detalladas de los datos históricos y en tiempo real, incluyendo:
    * Gráfica de Temperatura (DHT22)
    * Gráfica de Índice de Calor (DHT22)
    * Gráfica de Humedad (DHT22)
    * Gráfica de Niveles de Temperatura (perspectiva adicional)
    * Mapa de Calor de Humedad
    * Mapa de Calor de Temperatura
    * Gráfica de Intensidad de Luz UV (VEML6070)
4.  **Aplicación Web en Streamlit:** Una aplicación web interactiva que:
    * Proporciona enlaces directos a los paneles individuales de Grafana para una visualización detallada.
    * Muestra una selección de datos crudos recientes directamente desde InfluxDB.
    * Presenta un análisis estadístico básico (mínimos, máximos, promedios) de los datos.
    * Ofrece recomendaciones automatizadas para el cuidado de los microcultivos basadas en umbrales predefinidos. [cite: 19]

## 🚀 Cómo Ejecutar la Aplicación Streamlit

1.  **Clona este repositorio:**
    ```bash
    git clone URL_DE_TU_REPOSITORIO
    cd NOMBRE_DEL_DIRECTORIO
    ```
2.  **Instala las dependencias:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Asegúrate de que el archivo `config.py`** tenga las credenciales correctas para tu instancia de InfluxDB. Las credenciales del curso son[cite: 37]:
    * URL: `https://us-east-1-1.aws.cloud2.influxdata.com`
    * Token: `rnRx-Nk8dXeumEsQeDT4hk78QFWNTOVim7UrH5fnYKVSoQQIkhCwKq03-UMKN-SONj-DbfmrMDOHUI61qRJaiw==`
    * Organización: `0925ccf91ab36478`
    * Bucket: `homeiot` [cite: 39]

4.  **Ejecuta la aplicación con Streamlit:**
    ```bash
    streamlit run app.py
    ```
5.  **Accede a la interfaz en tu navegador:**
    Normalmente en `http://localhost:8501`

##  deliverables del Proyecto (Según PDF Guía)

Este repositorio y la solución implementada buscan cumplir con los siguientes entregables del "Proyecto Integrador":
* **Tablero de Visualización en Grafana:** Implementado y accesible. [cite: 13]
* **Aplicación Web con Streamlit:** Contenida en `app.py`, cumple con mostrar datos crudos, análisis y recomendaciones. [cite: 17, 18, 19]
* **Brochure de Presentación:** (Se desarrollará por separado) [cite: 21]
* **Video de Presentación:** (Se desarrollará por separado)

## 📁 Estructura del Repositorio Sugerida
