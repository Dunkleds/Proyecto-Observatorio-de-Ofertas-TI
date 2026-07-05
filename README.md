# Observatorio de Ofertas TI


El proyecto consiste en un pipeline de datos orientado a ingeniería de datos, cuyo objetivo es recopilar, procesar, almacenar y analizar ofertas laborales relacionadas con el mundo tecnológico. Para ello, se utilizan fuentes públicas de ofertas laborales, procesamiento con Python, almacenamiento en PostgreSQL y generación de indicadores analíticos mediante SQL.

---

## Objetivo del proyecto

Construir un observatorio de ofertas laborales TI que permita analizar la demanda de habilidades técnicas presentes en ofertas de empleo tecnológicas.

El proyecto busca demostrar:

* Uso de Git y GitHub mediante ramas, commits, merges, Pull Requests y releases.
* Extracción de datos desde APIs y una fuente web.
* Organización del pipeline bajo una arquitectura por capas.
* Limpieza, normalización y transformación de datos.
* Carga de datos en PostgreSQL.
* Creación de vistas analíticas para indicadores finales.
* Visualización de resultados mediante un dashboard simple.

---

## Arquitectura del pipeline

El proyecto sigue una arquitectura tipo **Medallion**, separada en tres capas principales:

```text
Bronze Layer  → datos crudos
Silver Layer  → datos limpios y normalizados
Gold Layer    → datos analíticos e indicadores finales
```

### Bronze Layer

La capa bronze extrae y almacena datos crudos desde las fuentes originales, sin aplicar reglas de negocio ni limpieza profunda.

Fuentes utilizadas:

* Remotive API.
* Arbeitnow API.
* We Work Remotely RSS.
* Web scraping simple sobre We Work Remotely.

Los datos crudos se guardan localmente en:

```text
data/raw/
```

Estos archivos no se versionan en GitHub, ya que son datos generados por el pipeline.

### Silver Layer

La capa silver toma los datos crudos de la capa bronze y realiza:

* Lectura de archivos JSON.
* Detección de fuente de origen.
* Normalización de columnas.
* Limpieza de texto y eliminación de HTML.
* Deduplicación de ofertas.
* Clasificación de ofertas relacionadas con TI.
* Extracción de skills técnicas.

Los resultados se guardan localmente en:

```text
data/procesada/silver/
```

Archivos principales generados:

```text
jobs_normalized.csv
jobs_it.csv
job_skills.csv
skills_catalog.csv
```

### Gold Layer

La capa gold carga los datos silver en PostgreSQL y genera vistas analíticas en SQL.

Se crean dos schemas principales:

```text
silver
gold
```

Tablas cargadas en el schema `silver`:

```text
silver.jobs_it
silver.job_skills
silver.skills_catalog
```

Vistas creadas en el schema `gold`:

```text
gold.vw_resumen_general
gold.vw_ofertas_por_fuente
gold.vw_top_skills
gold.vw_top_empresas
gold.vw_ofertas_por_mes
gold.vw_skills_por_fuente
gold.vw_demanda_data_engineering
```

Los resultados analíticos también se exportan localmente en:

```text
data/procesada/gold/
```

---

## Estructura del repositorio

```text
.
├── README.md
├── dashboard/
│   └── app.py
├── data/
│   ├── procesada/
│   │   ├── silver/
│   │   └── gold/
│   └── raw/
├── docker-compose.yml
├── docs/
│   ├── architecture.md
│   ├── data_dictionary.md
│   ├── git_workflow.md
│   └── project_report.md
├── notebooks/
├── requirements.txt
├── sql/
│   ├── 01_create_schemas.sql
│   ├── 02_create_silver_tables.sql
│   └── 03_gold_views.sql
└── src/
    ├── config.py
    ├── extraccion/
    │   ├── arbeitnow_api.py
    │   ├── remotive_api.py
    │   ├── wwr_rss.py
    │   └── wwr_scraper.py
    ├── load/
    │   ├── __init__.py
    │   └── postgres_loader.py
    ├── main.py
    ├── main_extract.py
    ├── main_silver.py
    ├── main_gold.py
    ├── transformacion/
    │   ├── __init__.py
    │   └── silver_jobs.py
    └── utils/
```

---

## Tecnologías utilizadas

* Python.
* Pandas.
* Requests.
* BeautifulSoup.
* Feedparser.
* PostgreSQL.
* Docker Compose.
* SQL.
* SQLAlchemy.
* Streamlit.
* Git.
* GitHub.

---

## Instalación del proyecto

### 1. Clonar el repositorio

```bash
git clone https://github.com/Dunkleds/Proyecto-Observatorio-de-Ofertas-TI.git
cd Proyecto-Observatorio-de-Ofertas-TI
```

### 2. Crear ambiente virtual

```bash
python -m venv .venv
```

Activar ambiente virtual en Linux o WSL:

```bash
source .venv/bin/activate
```

Activar ambiente virtual en Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

---

## Configuración de variables de entorno

Crear un archivo `.env` en la raíz del proyecto con la siguiente configuración:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=observatorio_ti
DB_USER=postgres
DB_PASSWORD=postgres
```

El archivo `.env` no se versiona en GitHub por seguridad. Se incluye `.env.example` como referencia.

---

## Levantar PostgreSQL con Docker

Ejecutar:

```bash
docker compose up -d
```

Verificar que el contenedor esté activo:

```bash
docker ps
```

El contenedor esperado es:

```text
observatory_postgres
```

Para entrar a PostgreSQL manualmente:

```bash
docker exec -it observatory_postgres psql -U postgres -d observatorio_ti
```

---

## Ejecución del pipeline

### 1. Ejecutar Bronze Layer

```bash
python src/main_extract.py
```

Esta etapa descarga datos crudos desde las fuentes disponibles y los almacena en:

```text
data/raw/
```

### 2. Ejecutar Silver Layer

```bash
python src/main_silver.py
```

Esta etapa limpia, normaliza, deduplica, clasifica ofertas TI y extrae skills técnicas.

Los archivos generados se guardan en:

```text
data/procesada/silver/
```

### 3. Ejecutar Gold Layer

```bash
python src/main_gold.py
```

Esta etapa carga datos en PostgreSQL, crea vistas analíticas y exporta resultados finales.

Los archivos generados se guardan en:

```text
data/procesada/gold/
```

---

## Ejecución del dashboard

Luego de ejecutar la gold layer, iniciar el dashboard con:

```bash
streamlit run dashboard/app.py
```

El dashboard permite visualizar:

* Total de ofertas TI.
* Cantidad de empresas.
* Ofertas por fuente.
* Top skills más solicitadas.
* Top empresas con más ofertas.
* Evolución mensual de ofertas.
* Demanda de skills asociadas a Data Engineering.

---

## Flujo Git utilizado

El proyecto utiliza un flujo de trabajo basado en ramas:

```text
main       → rama principal estable
develop    → rama de integración
feature/*  → desarrollo de nuevas funcionalidades
refactor/* → mejoras o reestructuraciones
docs/*     → documentación
```

Ejemplos de ramas utilizadas:

```text
feature/remotive-api
feature/arbeitnow-api
feature/weworkremotely-api
feature/Scrapper_y_extractor_unificado
refactor/bronze_layer_fix
feature/silver-layer
feature/gold-layer
feature/dashboard
docs/readme
```

Durante el desarrollo se realizaron integraciones mediante Pull Requests y merges, con el objetivo de mantener un historial progresivo y analizable.

---

## Indicadores generados

La gold layer genera vistas SQL para analizar:

* Resumen general del observatorio.
* Cantidad de ofertas por fuente.
* Skills técnicas más solicitadas.
* Empresas con más ofertas.
* Evolución mensual de ofertas.
* Skills por fuente.
* Demanda de habilidades asociadas a Data Engineering.

---

## Estado del proyecto

El proyecto cuenta con las siguientes capas implementadas:

```text
Bronze Layer  → implementada
Silver Layer  → implementada
Gold Layer    → implementada
Dashboard     → implementado
```

---

## Consideraciones

Los archivos generados por el pipeline no se suben al repositorio. Esto incluye:

```text
data/raw/*.json
data/procesada/silver/*.csv
data/procesada/gold/*.csv
```

Estos archivos pueden regenerarse ejecutando nuevamente el pipeline.

---

