from __future__ import annotations
from datetime import datetime
from pathlib import Path
import hashlib
import json
import re

import pandas as pd
from bs4 import BeautifulSoup


RAW_DIR = Path("data/raw")
SILVER_DIR = Path("data/procesada/silver")


NORMALIZED_COLUMNS = [
    "external_id",
    "title",
    "company",
    "location",
    "job_type",
    "category",
    "description",
    "url",
    "source",
    "published_at",
    "raw_file",
    "processed_at",
]


IT_KEYWORDS = [
    "software",
    "developer",
    "desarrollador",
    "programador",
    "engineer",
    "ingeniero",
    "data",
    "datos",
    "analyst",
    "analytics",
    "business intelligence",
    "bi",
    "python",
    "sql",
    "java",
    "javascript",
    "typescript",
    "react",
    "node",
    "backend",
    "frontend",
    "fullstack",
    "devops",
    "cloud",
    "aws",
    "azure",
    "gcp",
    "docker",
    "kubernetes",
    "database",
    "postgresql",
    "mysql",
    "etl",
    "elt",
    "machine learning",
    "artificial intelligence",
    "cybersecurity",
    "qa",
    "quality assurance",
    "test automation",
    "scrum",
    "product owner",
    "product manager",
    "it",
    "information technology",
]


SKILL_PATTERNS = {
    "Python": [r"\bpython\b"],
    "SQL": [r"\bsql\b"],
    "PostgreSQL": [r"\bpostgresql\b", r"\bpostgres\b"],
    "MySQL": [r"\bmysql\b"],
    "BigQuery": [r"\bbigquery\b", r"\bbig query\b"],
    "AWS": [r"\baws\b", r"\bamazon web services\b"],
    "Azure": [r"\bazure\b"],
    "GCP": [r"\bgcp\b", r"\bgoogle cloud\b", r"\bgoogle cloud platform\b"],
    "Docker": [r"\bdocker\b"],
    "Kubernetes": [r"\bkubernetes\b", r"\bk8s\b"],
    "Spark": [r"\bspark\b", r"\bapache spark\b"],
    "PySpark": [r"\bpyspark\b"],
    "Airflow": [r"\bairflow\b", r"\bapache airflow\b"],
    "dbt": [r"\bdbt\b"],
    "Git": [r"\bgit\b"],
    "GitHub": [r"\bgithub\b"],
    "Linux": [r"\blinux\b"],
    "Pandas": [r"\bpandas\b"],
    "NumPy": [r"\bnumpy\b"],
    "Power BI": [r"\bpower bi\b", r"\bpowerbi\b"],
    "Tableau": [r"\btableau\b"],
    "Looker": [r"\blooker\b", r"\blooker studio\b"],
    "FastAPI": [r"\bfastapi\b"],
    "Flask": [r"\bflask\b"],
    "Django": [r"\bdjango\b"],
    "JavaScript": [r"\bjavascript\b", r"\bjs\b"],
    "TypeScript": [r"\btypescript\b", r"\bts\b"],
    "React": [r"\breact\b", r"\breactjs\b", r"\breact\.js\b"],
    "Node.js": [r"\bnode\.js\b", r"\bnodejs\b", r"\bnode\b"],
    "Java": [r"\bjava\b"],
    "Scala": [r"\bscala\b"],
    "ETL": [r"\betl\b"],
    "ELT": [r"\belt\b"],
    "Data Warehouse": [r"\bdata warehouse\b"],
    "Data Lake": [r"\bdata lake\b"],
    "Machine Learning": [r"\bmachine learning\b", r"\bml\b"],
    "API": [r"\bapi\b", r"\bapis\b"],
}


def is_missing_text(value) -> bool:
    if value is None:
        return True

    try:
        return bool(pd.isna(value))
    except (TypeError, ValueError):
        return False


def clean_html(text: str | None) -> str | None:
    if is_missing_text(text):
        return None

    text = str(text)

    if "<" in text and ">" in text:
        soup = BeautifulSoup(text, "html.parser")
        clean_text = soup.get_text(separator=" ", strip=True)
    else:
        clean_text = text

    clean_text = re.sub(r"\s+", " ", clean_text).strip()

    return clean_text if clean_text else None


def normalize_text(text: str | None) -> str | None:
    if is_missing_text(text):
        return None

    text = clean_html(text)

    if not text:
        return None

    return re.sub(r"\s+", " ", text).strip()


def text_or_empty(value) -> str:
    if is_missing_text(value):
        return ""

    return str(value)


def parse_datetime(value) -> str | None:
    if value is None or value == "":
        return None

    try:
        if isinstance(value, int):
            parsed = pd.to_datetime(value, unit="s", errors="coerce")
        else:
            parsed = pd.to_datetime(value, errors="coerce")

        if pd.isna(parsed):
            return None

        return parsed.isoformat()

    except Exception:
        return None


def generate_hash_id(value: str | None) -> str:
    if not value:
        value = f"missing-{datetime.now().timestamp()}"

    return hashlib.md5(value.encode("utf-8")).hexdigest()


def detect_source_from_filename(file_path: Path) -> str:
    filename = file_path.name.lower()

    if "remotive" in filename:
        return "remotive"

    if "arbeitnow" in filename:
        return "arbeitnow"

    if "we_work_remotely_rss" in filename or "wwr_rss" in filename:
        return "we_work_remotely_rss"

    if "we_work_remotely_scraper" in filename or "wwr_scraper" in filename:
        return "we_work_remotely_scraper"

    return "unknown"


def load_raw_json(file_path: Path) -> list[dict]:
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    if isinstance(data, list):
        return data

    if isinstance(data, dict):
        if "jobs" in data:
            return data["jobs"]

        if "data" in data:
            return data["data"]

    return []


def normalize_remotive_job(job: dict, raw_file: str) -> dict:
    url = job.get("url")

    return {
        "external_id": str(job.get("id") or generate_hash_id(url)),
        "title": normalize_text(job.get("title")),
        "company": normalize_text(job.get("company_name")),
        "location": normalize_text(job.get("candidate_required_location")),
        "job_type": normalize_text(job.get("job_type")),
        "category": normalize_text(job.get("category")),
        "description": normalize_text(job.get("description")),
        "url": normalize_text(url),
        "source": "remotive",
        "published_at": parse_datetime(job.get("publication_date")),
        "raw_file": raw_file,
        "processed_at": datetime.now().isoformat(),
    }


def normalize_arbeitnow_job(job: dict, raw_file: str) -> dict:
    url = job.get("url")
    tags = job.get("tags") or []
    job_types = job.get("job_types") or []

    category = ", ".join(tags) if isinstance(tags, list) else str(tags)
    job_type = ", ".join(job_types) if isinstance(job_types, list) else str(job_types)

    return {
        "external_id": str(job.get("slug") or generate_hash_id(url)),
        "title": normalize_text(job.get("title")),
        "company": normalize_text(job.get("company_name")),
        "location": normalize_text(job.get("location")),
        "job_type": normalize_text(job_type),
        "category": normalize_text(category),
        "description": normalize_text(job.get("description")),
        "url": normalize_text(url),
        "source": "arbeitnow",
        "published_at": parse_datetime(job.get("created_at")),
        "raw_file": raw_file,
        "processed_at": datetime.now().isoformat(),
    }


def normalize_wwr_job(job: dict, raw_file: str, source: str) -> dict:
    url = job.get("url") or job.get("link")

    return {
        "external_id": str(job.get("external_id") or job.get("id") or generate_hash_id(url)),
        "title": normalize_text(job.get("title")),
        "company": normalize_text(job.get("company")),
        "location": normalize_text(job.get("location") or "Remote"),
        "job_type": normalize_text(job.get("job_type")),
        "category": normalize_text(job.get("category")),
        "description": normalize_text(job.get("description") or job.get("summary")),
        "url": normalize_text(url),
        "source": source,
        "published_at": parse_datetime(job.get("published_at") or job.get("published")),
        "raw_file": raw_file,
        "processed_at": datetime.now().isoformat(),
    }


def normalize_job(job: dict, source: str, raw_file: str) -> dict:
    if source == "remotive":
        return normalize_remotive_job(job, raw_file)

    if source == "arbeitnow":
        return normalize_arbeitnow_job(job, raw_file)

    if source in {"we_work_remotely_rss", "we_work_remotely_scraper"}:
        return normalize_wwr_job(job, raw_file, source)

    url = job.get("url")

    return {
        "external_id": str(job.get("id") or job.get("external_id") or generate_hash_id(url)),
        "title": normalize_text(job.get("title")),
        "company": normalize_text(job.get("company") or job.get("company_name")),
        "location": normalize_text(job.get("location")),
        "job_type": normalize_text(job.get("job_type")),
        "category": normalize_text(job.get("category")),
        "description": normalize_text(job.get("description")),
        "url": normalize_text(url),
        "source": source,
        "published_at": parse_datetime(job.get("published_at")),
        "raw_file": raw_file,
        "processed_at": datetime.now().isoformat(),
    }


def normalize_bronze_files() -> pd.DataFrame:
    raw_files = sorted(RAW_DIR.glob("*.json"))

    if not raw_files:
        raise FileNotFoundError("No se encontraron archivos JSON en data/raw/.")

    normalized_jobs = []

    for file_path in raw_files:
        source = detect_source_from_filename(file_path)
        raw_jobs = load_raw_json(file_path)

        print(f"Procesando archivo: {file_path.name}")
        print(f"Fuente detectada: {source}")
        print(f"Registros encontrados: {len(raw_jobs)}")

        for job in raw_jobs:
            normalized_jobs.append(
                normalize_job(
                    job=job,
                    source=source,
                    raw_file=file_path.name,
                )
            )

    df = pd.DataFrame(normalized_jobs, columns=NORMALIZED_COLUMNS)

    df = df.dropna(subset=["title", "url"])
    df = df.drop_duplicates(subset=["source", "external_id"])
    df = df.drop_duplicates(subset=["url"])

    return df.reset_index(drop=True)


def build_search_text(row: pd.Series) -> str:
    values = [
        text_or_empty(row.get("title")),
        text_or_empty(row.get("company")),
        text_or_empty(row.get("location")),
        text_or_empty(row.get("job_type")),
        text_or_empty(row.get("category")),
        text_or_empty(row.get("description")),
    ]

    return " ".join(values).lower()


def is_it_related_job(row: pd.Series) -> bool:
    search_text = build_search_text(row)

    for keyword in IT_KEYWORDS:
        pattern = rf"\b{re.escape(keyword.lower())}\b"

        if re.search(pattern, search_text):
            return True

    return False


def filter_it_jobs(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["is_it_related"] = df.apply(is_it_related_job, axis=1)

    return df[df["is_it_related"]].reset_index(drop=True)


def extract_skills_from_text(text: str) -> list[str]:
    if not isinstance(text, str):
        return []

    found_skills = []

    for skill, patterns in SKILL_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text, flags=re.IGNORECASE):
                found_skills.append(skill)
                break

    return sorted(set(found_skills))


def add_skills_to_jobs(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    jobs_df = df.copy()
    all_job_skills = []
    skills_by_job = []

    for index, row in jobs_df.iterrows():
        search_text = build_search_text(row)
        skills = extract_skills_from_text(search_text)

        skills_by_job.append(", ".join(skills))

        for skill in skills:
            all_job_skills.append({
                "job_index": index,
                "external_id": row["external_id"],
                "source": row["source"],
                "url": row["url"],
                "skill_name": skill,
            })

    jobs_df["skills"] = skills_by_job
    jobs_df["total_skills_detected"] = jobs_df["skills"].apply(
        lambda value: 0 if value == "" else len(value.split(", "))
    )

    job_skills_df = pd.DataFrame(
        all_job_skills,
        columns=["job_index", "external_id", "source", "url", "skill_name"]
    )

    if not job_skills_df.empty:
        skills_catalog_df = (
            job_skills_df[["skill_name"]]
            .drop_duplicates()
            .sort_values("skill_name")
            .reset_index(drop=True)
        )
    else:
        skills_catalog_df = pd.DataFrame(columns=["skill_name"])

    return jobs_df, job_skills_df, skills_catalog_df


def save_silver_outputs(
    normalized_df: pd.DataFrame,
    it_jobs_df: pd.DataFrame,
    job_skills_df: pd.DataFrame,
    skills_catalog_df: pd.DataFrame,
) -> None:
    SILVER_DIR.mkdir(parents=True, exist_ok=True)

    normalized_df.to_csv(
        SILVER_DIR / "jobs_normalized.csv",
        index=False,
        encoding="utf-8"
    )

    it_jobs_df.to_csv(
        SILVER_DIR / "jobs_it.csv",
        index=False,
        encoding="utf-8"
    )

    job_skills_df.to_csv(
        SILVER_DIR / "job_skills.csv",
        index=False,
        encoding="utf-8"
    )

    skills_catalog_df.to_csv(
        SILVER_DIR / "skills_catalog.csv",
        index=False,
        encoding="utf-8"
    )


def run_silver_pipeline() -> None:


    normalized_df = normalize_bronze_files()
    print(f"Ofertas normalizadas: {len(normalized_df)}")

    it_jobs_df = filter_it_jobs(normalized_df)
    print(f"Ofertas clasificadas como TI: {len(it_jobs_df)}")

    it_jobs_with_skills_df, job_skills_df, skills_catalog_df = add_skills_to_jobs(it_jobs_df)

    print(f"Relaciones oferta-skill detectadas: {len(job_skills_df)}")
    print(f"Skills únicas detectadas: {len(skills_catalog_df)}")

    save_silver_outputs(
        normalized_df=normalized_df,
        it_jobs_df=it_jobs_with_skills_df,
        job_skills_df=job_skills_df,
        skills_catalog_df=skills_catalog_df,
    )


    print("Etapa SILVER finalizada")
    print("Archivos generados en data/procesada/silver/")
