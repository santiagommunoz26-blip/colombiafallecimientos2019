# 🏥 Mortalidad Colombia 2019

Dashboard interactivo para el análisis exploratorio de las defunciones no fetales registradas en Colombia durante el año 2019, según datos del DANE (Departamento Administrativo Nacional de Estadística).

---

## Tabla de contenidos

1. [Vista general](#vista-general)  
2. [Estructura del proyecto](#estructura-del-proyecto)  
3. [Datos requeridos](#datos-requeridos)  
4. [Instalación y ejecución local](#instalación-y-ejecución-local)  
5. [Despliegue en Streamlit Cloud](#despliegue-en-streamlit-cloud)  
6. [Descripción de módulos](#descripción-de-módulos)  
7. [Filtros disponibles](#filtros-disponibles)  
8. [Páginas y visualizaciones](#páginas-y-visualizaciones)  
9. [Interpretación de resultados](#interpretación-de-resultados)  
10. [Decisiones de diseño](#decisiones-de-diseño)  

---

## Vista general

La aplicación ofrece cuatro vistas analíticas accesibles desde el sidebar:

| Página | Contenido principal |
|---|---|
| **General** | KPIs resumen, tendencia mensual, distribución por sexo y edad |
| **Territorio** | Mapa coroplético departamental, ranking Top 10 |
| **Causas** | Top 15 diagnósticos CIE-10, capítulos de enfermedad |
| **Demografía** | Pirámide poblacional, estado civil, nivel educativo |

Todos los gráficos responden en tiempo real a los **seis filtros** del sidebar: manera de muerte, sexo, departamento, rango de meses, grupo de edad y causa CIE-10.

---

## Estructura del proyecto

```
mortalidad_colombia/
│
├── app.py                  # Punto de entrada — orquestador principal
│
├── modules/                # Paquete de módulos
│   ├── __init__.py
│   ├── config.py           # Paleta de colores, constantes, mapeos categóricos
│   ├── data_loader.py      # Carga y preprocesamiento de datos (con caché)
│   ├── text_utils.py       # Limpieza y normalización de strings
│   ├── styles.py           # CSS global e inyección de estilos
│   ├── sidebar.py          # Sidebar: navegación, filtros, descarga CSV
│   └── pages.py            # Una función de renderizado por página
│
├── data/                   # Archivos de datos (NO incluidos en el repo)
│   ├── mortalidad_2019.xlsx
│   ├── divipola.xlsx
│   └── codigos_muerte.xlsx
│
├── colombia.geojson        # Geometrías departamentales
├── requirements.txt        # Dependencias Python
└── README.md
```

---

## Datos requeridos

Coloca los siguientes archivos en la carpeta `data/` antes de ejecutar la aplicación:

### `mortalidad_2019.xlsx`
Microdatos de defunciones no fetales DANE 2019.  
Columnas mínimas esperadas:

| Columna | Tipo | Descripción |
|---|---|---|
| `COD_DEPARTAMENTO` | int | Código DIVIPOLA del departamento |
| `COD_MUERTE` | str | Código CIE-10 de la causa de muerte |
| `MANERA_MUERTE` | str | Natural / Homicidio / Suicidio / Accidente / … |
| `SEXO` | int | 1 = Masculino, 2 = Femenino, 3 = Indeterminado |
| `MES` | int | Mes de defunción (1–12) |
| `GRUPO_EDAD1` | int | Código de grupo quinquenal (0–21) |
| `ESTADO_CIVIL` | int | Código de estado civil (1–6) |
| `NIVEL_EDUCATIVO` | int | Código de nivel educativo (1–6, 9) |

### `divipola.xlsx`
Tabla de correspondencia código → nombre de departamento.

| Columna | Descripción |
|---|---|
| `COD_DEPARTAMENTO` | Código numérico de 2 dígitos |
| `DEPARTAMENTO` | Nombre oficial del departamento |

### `codigos_muerte.xlsx`
Tabla CIE-10 con capítulos y diagnósticos de 4 caracteres.  
La tabla de datos comienza en la **fila 9** (índice 8). Columnas esperadas en ese orden:

```
cap | nom_cap | cod3 | desc3 | cod4 | desc4
```

### `colombia.geojson`
GeoJSON con los polígonos de los 33 departamentos de Colombia.  
Debe incluir una propiedad con el código de departamento (2 dígitos, con cero inicial) compatible con `COD_DEPARTAMENTO`. El módulo `data_loader.detect_geo_id` detecta automáticamente la clave correcta entre: `DPTO`, `dpto`, `COD_DPTO`, `codigo`, `CODIGO`, `id`.

> **Fuentes oficiales:** Los archivos de mortalidad y DIVIPOLA se descargan gratuitamente desde el [portal de microdatos del DANE](https://microdatos.dane.gov.co/). El GeoJSON puede obtenerse del [repositorio de mapas de Colombia en GitHub](https://github.com/michellejl/Colombia-GeoJSON) u otras fuentes cartográficas abiertas.

---

## Instalación y ejecución local

### Requisitos previos

- Python 3.9 o superior
- pip

### Pasos

```bash
# 1. Clonar o descomprimir el proyecto
git clone <url-del-repo>
cd mortalidad_colombia

# 2. Crear entorno virtual (recomendado)
python -m venv .venv
source .venv/bin/activate        # Linux / macOS
.venv\Scripts\activate           # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Agregar los archivos de datos en data/
#    (mortalidad_2019.xlsx, divipola.xlsx, codigos_muerte.xlsx)
#    y el archivo colombia.geojson en la raíz del proyecto

# 5. Ejecutar la aplicación
streamlit run app.py
```

La aplicación quedará disponible en `http://localhost:8501`.

---

## Despliegue en Streamlit Cloud

1. Subir el proyecto a un repositorio GitHub (sin los archivos `data/` si son confidenciales).
2. Acceder a [share.streamlit.io](https://share.streamlit.io) e iniciar sesión con tu cuenta de GitHub.
3. Crear una nueva aplicación apuntando al repositorio y al archivo `app.py`.
4. En la sección **Advanced settings → Secrets**, agregar las credenciales si los datos se sirven desde un bucket externo, o bien usar **Files** para subir los Excel directamente.
5. Hacer clic en **Deploy**.

> Si los archivos de datos son públicos, pueden incluirse directamente en el repositorio. En caso contrario, considera servir los Excel desde Google Drive o AWS S3 y adaptando `load_data()` en `modules/data_loader.py`.

---

## Descripción de módulos

### `app.py`
Punto de entrada. Responsabilidades:
- Configurar la página Streamlit (`st.set_page_config`).
- Llamar `inject_styles()`.
- Cargar datos con `load_data()` y `load_geo()`.
- Invocar `render_sidebar()` para obtener el DataFrame filtrado.
- Renderizar el header principal.
- Enrutar a la función de página correspondiente según `st.session_state.page`.

### `modules/config.py`
Centraliza todas las constantes de la aplicación:
- **Paleta de colores** siguiendo la regla 60-30-10.
- **`PLOTLY_LAYOUT`**: dict base aplicado a todos los gráficos para garantizar consistencia visual.
- **Mapeos categóricos**: `SEXO_MAP`, `MESES_MAP`, `GRUPOS_EDAD_MAP`, `ESTADO_CIVIL_MAP`, `NIVEL_EDUCATIVO_MAP`.
- Lista de páginas `PAGES` y orden canónico de grupos de edad `EDAD_ORDER`.

### `modules/data_loader.py`
Funciones de carga con caché (`@st.cache_data`):
- **`load_data()`**: lee los tres Excel, los une mediante merges y agrega columnas legibles (`SEXO_L`, `MES_L`, `EDAD_L`).
- **`load_geo()`**: lee el GeoJSON y enriquece las propiedades con versiones normalizadas en ASCII.
- **`detect_geo_id(geo)`**: detecta automáticamente la clave de identificador geográfico.

### `modules/text_utils.py`
Utilidades de texto independientes de Streamlit:
- **`limpiar_texto(texto)`**: corrige encoding latin-1/UTF-8, reemplaza escapes corruptos, elimina caracteres no imprimibles y aplica `title()`.
- **`normalize_text(text)`**: convierte a ASCII puro en mayúsculas para comparaciones y joins.

### `modules/styles.py`
- **`APP_CSS`**: string con todo el CSS de la aplicación.
- **`inject_styles()`**: inyecta `APP_CSS` en la aplicación mediante `st.markdown`.

### `modules/sidebar.py`
- **`render_sidebar(df)`**: dibuja cabecera de marca, botones de navegación y los seis filtros. Devuelve el DataFrame filtrado y un dict con los valores seleccionados.
- **`render_download_button(fdf, filters)`**: agrega el botón de descarga CSV con nombre de archivo dinámico.

### `modules/pages.py`
Una función por página:
- **`page_general(fdf)`**: KPIs + 4 gráficos.
- **`page_territorio(fdf, geo, GEO_ID)`**: mapa + ranking.
- **`page_causas(fdf)`**: top causas + capítulos CIE-10.
- **`page_demografia(fdf)`**: pirámide + estado civil + nivel educativo.

---

## Filtros disponibles

| Filtro | Tipo | Descripción |
|---|---|---|
| Manera de muerte | Selectbox | Natural, Homicidio, Suicidio, Accidente u Otro |
| Sexo | Selectbox | Masculino, Femenino o Todos |
| Departamento | Selectbox | Los 33 departamentos de Colombia |
| Rango de meses | Slider | Intervalo entre 1 (Enero) y 12 (Diciembre) |
| Grupo de edad | Selectbox | Grupos quinquenales: `<1 año` hasta `100+` |
| Causa de muerte | Selectbox | Cualquier diagnóstico CIE-10 de 4 caracteres |

Los filtros son **acumulativos**: se aplican en el orden listado y el conteo de registros activos se muestra en el header.

---

## Páginas y visualizaciones

### General
- **KPIs** (5 tarjetas): total de muertes, naturales, homicidios, suicidios y accidentes con su porcentaje.
- **Manera de muerte** (barras horizontales): ranking de todas las maneras de muerte en los datos filtrados.
- **Tendencia mensual** (líneas con marcadores): evolución mes a mes desglosada por manera de muerte.
- **Distribución por sexo** (dona): proporción masculino/femenino con el porcentaje mayoritario en el centro.
- **Muertes por grupo de edad** (barras con gradiente de color): distribución por grupos quinquenales.

### Territorio
- **Mapa coroplético**: intensidad de color proporcional al número de defunciones por departamento. Usa el GeoJSON y el código de departamento como clave de unión.
- **Top 10 departamentos** (barras horizontales): los diez departamentos con mayor mortalidad en el período filtrado.

### Causas
- **Top 15 causas CIE-10** (barras horizontales): diagnósticos de 4 caracteres más frecuentes, con etiquetas truncadas a 40 caracteres.
- **Capítulos CIE-10** (barras horizontales): los 10 capítulos de la clasificación con mayor peso, truncados a 35 caracteres.

### Demografía
- **Pirámide poblacional** (barras simétricas): masculino hacia la izquierda (valores negativos), femenino hacia la derecha, por grupos quinquenales.
- **Estado civil** (dona): distribución de los seis estados civiles codificados en los datos.
- **Nivel educativo** (barras con gradiente): distribución de las defunciones según el nivel educativo alcanzado.

---

## Interpretación de resultados

### Mortalidad general
- Un alto porcentaje de muertes **naturales** (típicamente > 90 %) es esperable en una población general.
- Picos mensuales pueden indicar brotes, estacionalidad de enfermedades crónicas o eventos climáticos.

### Distribución geográfica
- Los departamentos con mayor población absoluta (Bogotá D.C., Antioquia, Valle del Cauca) tienden a concentrar el mayor número de defunciones en términos absolutos.
- Para comparaciones más justas entre departamentos, considerar tasas por 100 000 habitantes (requiere datos poblacionales adicionales no incluidos en este dataset).

### Causas de muerte
- Las enfermedades del **sistema circulatorio** (Capítulo IX CIE-10) y las **neoplasias** (Capítulo II) suelen encabezar las listas en países de ingreso medio-alto.
- Un porcentaje relevante de homicidios en el Top 15 de causas refleja la situación de violencia del país en el período analizado.

### Demografía
- La pirámide de **mortalidad** no refleja la estructura de la población viva; se espera una concentración en edades mayores (enfermedades crónicas) y un segundo pico en adultos jóvenes (violencia y accidentes).
- Un alto porcentaje de registro con **nivel educativo "Sin dato"** o "Ninguno" puede reflejar subregistro en poblaciones vulnerables o personas mayores.

---

## Decisiones de diseño

| Principio | Implementación |
|---|---|
| **Regla 60-30-10** | 60 % fondo azul marino `#0a0e1a`, 30 % sidebar/tarjetas `#0f1423`, 10 % azul brillante `#3b82f6` para acentos |
| **Consistencia** | `PLOTLY_LAYOUT` centralizado en `config.py`; todos los gráficos comparten fondo transparente y familia tipográfica Inter |
| **Jerarquía visual** | Títulos de sección con `sec-title` (borde izquierdo azul + mayúsculas), KPIs con tamaño 2rem, texto secundario 0.7rem |
| **Feedback inmediato** | Transiciones CSS en hover de tarjetas KPI, controles y botones de navegación |
| **Caché de datos** | `@st.cache_data` en `load_data()` y `load_geo()` evita recargar archivos en cada interacción |
| **Modularidad** | Separación clara entre configuración, datos, estilos, sidebar y páginas; facilita mantenimiento y extensión |

---

*Desarrollado con [Streamlit](https://streamlit.io) · Datos: [DANE Colombia](https://www.dane.gov.co)*
