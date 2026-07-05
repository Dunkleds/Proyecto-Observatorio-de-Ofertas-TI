from pathlib import Path
import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text


SILVER_DIR = Path("data/procesada/silver")
GOLD_DIR = Path("data/procesada/gold")

SQL_SCHEMA_FILE = Path("sql/01_create_schemas.sql")
SQL_GOLD_VIEWS_FILE = Path("sql/03_gold_views.sql")

DROP_GOLD_VIEWS_SQL = """
DROP VIEW IF EXISTS gold.vw_resumen_general;
DROP VIEW IF EXISTS gold.vw_ofertas_por_fuente;
DROP VIEW IF EXISTS gold.vw_top_skills;
DROP VIEW IF EXISTS gold.vw_top_empresas;
DROP VIEW IF EXISTS gold.vw_ofertas_por_mes;
DROP VIEW IF EXISTS gold.vw_skills_por_fuente;
DROP VIEW IF EXISTS gold.vw_demanda_data_engineering;
"""


def get_database_url() -> str:
    load_dotenv()

    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "observatorio_ti")
    db_user = os.getenv("DB_USER", "observatorio_user")
    db_password = os.getenv("DB_PASSWORD", "observatorio_pass")

    return (
        f"postgresql+psycopg2://{db_user}:{db_password}"
        f"@{db_host}:{db_port}/{db_name}"
    )


def get_engine():
    database_url = get_database_url()
    return create_engine(database_url)


def execute_sql_file(engine, sql_file: Path) -> None:
    if not sql_file.exists():
        raise FileNotFoundError(f"No se encontró el archivo SQL: {sql_file}")

    sql_script = sql_file.read_text(encoding="utf-8")

    with engine.begin() as connection:
        connection.execute(text(sql_script))


def drop_gold_views(engine) -> None:
    with engine.begin() as connection:
        connection.execute(text(DROP_GOLD_VIEWS_SQL))


def read_silver_file(filename: str) -> pd.DataFrame:
    file_path = SILVER_DIR / filename

    if not file_path.exists():
        raise FileNotFoundError(
            f"No se encontró {file_path}. "
            "Ejecuta primero la silver layer con: "
            "PYTHONPATH=src python src/main_silver.py"
        )

    return pd.read_csv(file_path)


def prepare_jobs_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    if "published_at" in df.columns:
        df["published_at"] = pd.to_datetime(df["published_at"], errors="coerce")

    if "processed_at" in df.columns:
        df["processed_at"] = pd.to_datetime(df["processed_at"], errors="coerce")

    if "total_skills_detected" in df.columns:
        df["total_skills_detected"] = pd.to_numeric(
            df["total_skills_detected"],
            errors="coerce"
        ).fillna(0).astype(int)

    return df


def load_dataframe_to_postgres(
    df: pd.DataFrame,
    table_name: str,
    schema: str,
    engine,
) -> None:
    df.to_sql(
        name=table_name,
        con=engine,
        schema=schema,
        if_exists="replace",
        index=False,
        method="multi",
        chunksize=1000,
    )


def load_silver_tables(engine) -> None:
    print("Leyendo archivos silver...")

    jobs_it_df = read_silver_file("jobs_it.csv")
    job_skills_df = read_silver_file("job_skills.csv")
    skills_catalog_df = read_silver_file("skills_catalog.csv")

    jobs_it_df = prepare_jobs_dataframe(jobs_it_df)

    print(f"Ofertas TI cargadas desde CSV: {len(jobs_it_df)}")
    print(f"Relaciones oferta-skill cargadas desde CSV: {len(job_skills_df)}")
    print(f"Skills únicas cargadas desde CSV: {len(skills_catalog_df)}")

    print("Cargando tabla silver.jobs_it...")
    load_dataframe_to_postgres(
        df=jobs_it_df,
        table_name="jobs_it",
        schema="silver",
        engine=engine,
    )

    print("Cargando tabla silver.job_skills...")
    load_dataframe_to_postgres(
        df=job_skills_df,
        table_name="job_skills",
        schema="silver",
        engine=engine,
    )

    print("Cargando tabla silver.skills_catalog...")
    load_dataframe_to_postgres(
        df=skills_catalog_df,
        table_name="skills_catalog",
        schema="silver",
        engine=engine,
    )


def export_gold_view(engine, view_name: str) -> None:
    GOLD_DIR.mkdir(parents=True, exist_ok=True)

    query = f"SELECT * FROM gold.{view_name};"
    df = pd.read_sql(query, engine)

    output_path = GOLD_DIR / f"{view_name}.csv"
    df.to_csv(output_path, index=False, encoding="utf-8")

    print(f"Vista exportada: {output_path}")


def export_gold_outputs(engine) -> None:
    views = [
        "vw_resumen_general",
        "vw_ofertas_por_fuente",
        "vw_top_skills",
        "vw_top_empresas",
        "vw_ofertas_por_mes",
        "vw_skills_por_fuente",
        "vw_demanda_data_engineering",
    ]

    print("Exportando vistas gold a CSV...")

    for view_name in views:
        export_gold_view(engine, view_name)


def run_gold_pipeline() -> None:
    print("Iniciando etapa GOLD")

    engine = get_engine()

    print("Creando schemas silver y gold...")
    execute_sql_file(engine, SQL_SCHEMA_FILE)

    print("Eliminando vistas gold anteriores...")
    drop_gold_views(engine)

    print("Cargando datos silver en PostgreSQL...")
    load_silver_tables(engine)

    print("Creando vistas analíticas gold...")
    execute_sql_file(engine, SQL_GOLD_VIEWS_FILE)

    print("Exportando resultados gold...")
    export_gold_outputs(engine)

    print("Etapa GOLD finalizada")
    print("Tablas cargadas en schema silver")
    print("Vistas creadas en schema gold")
    print("Archivos exportados en data/procesada/gold/")
