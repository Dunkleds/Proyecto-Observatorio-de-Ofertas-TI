DROP VIEW IF EXISTS gold.vw_resumen_general;
DROP VIEW IF EXISTS gold.vw_ofertas_por_fuente;
DROP VIEW IF EXISTS gold.vw_top_skills;
DROP VIEW IF EXISTS gold.vw_top_empresas;
DROP VIEW IF EXISTS gold.vw_ofertas_por_mes;
DROP VIEW IF EXISTS gold.vw_skills_por_fuente;
DROP VIEW IF EXISTS gold.vw_demanda_data_engineering;

CREATE VIEW gold.vw_resumen_general AS
SELECT
    COUNT(*) AS total_ofertas_ti,
    COUNT(DISTINCT company) AS total_empresas,
    COUNT(DISTINCT source) AS total_fuentes,
    COUNT(DISTINCT location) AS total_ubicaciones,
    SUM(COALESCE(total_skills_detected, 0)) AS total_skills_detectadas
FROM silver.jobs_it;

CREATE VIEW gold.vw_ofertas_por_fuente AS
SELECT
    source,
    COUNT(*) AS total_ofertas
FROM silver.jobs_it
GROUP BY source
ORDER BY total_ofertas DESC;

CREATE VIEW gold.vw_top_skills AS
SELECT
    skill_name,
    COUNT(*) AS total_menciones
FROM silver.job_skills
GROUP BY skill_name
ORDER BY total_menciones DESC;

CREATE VIEW gold.vw_top_empresas AS
SELECT
    company,
    COUNT(*) AS total_ofertas
FROM silver.jobs_it
WHERE company IS NOT NULL
GROUP BY company
ORDER BY total_ofertas DESC;

CREATE VIEW gold.vw_ofertas_por_mes AS
SELECT
    DATE_TRUNC('month', published_at) AS mes,
    COUNT(*) AS total_ofertas
FROM silver.jobs_it
WHERE published_at IS NOT NULL
GROUP BY DATE_TRUNC('month', published_at)
ORDER BY mes;

CREATE VIEW gold.vw_skills_por_fuente AS
SELECT
    js.source,
    js.skill_name,
    COUNT(*) AS total_menciones
FROM silver.job_skills js
GROUP BY js.source, js.skill_name
ORDER BY js.source, total_menciones DESC;

CREATE VIEW gold.vw_demanda_data_engineering AS
SELECT
    skill_name,
    COUNT(*) AS total_menciones
FROM silver.job_skills
WHERE skill_name IN (
    'Python',
    'SQL',
    'PostgreSQL',
    'MySQL',
    'BigQuery',
    'AWS',
    'Azure',
    'GCP',
    'Docker',
    'Kubernetes',
    'Spark',
    'PySpark',
    'Airflow',
    'dbt',
    'ETL',
    'ELT',
    'Data Warehouse',
    'Data Lake',
    'Power BI',
    'Looker',
    'Tableau'
)
GROUP BY skill_name
ORDER BY total_menciones DESC;
