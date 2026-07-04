from datetime import datetime
from pathlib import Path
import json
import requests


REMOTIVE_API_URL = "https://remotive.com/api/remote-jobs"


def fetch_remotive_jobs(
    limit: int | None = None,
    search: str | None = None,
    category: str | None = None,
) -> list[dict]:
    """
    Extrae trabajos remotos activos de la API pública de Remotive.

    """
    params = {}

    if limit is not None:
        params["limit"] = limit

    if search is not None:
        params["search"] = search

    if category is not None:
        params["category"] = category

    response = requests.get(
        REMOTIVE_API_URL,
        params=params,
        timeout=30,
        headers={"User-Agent": "observatorio-ofertas-ti/1.0 academic project"},
    )

    response.raise_for_status()

    data = response.json()
    jobs = data.get("jobs", [])

    print(f"Cuenta de trabajos: {data.get('job-count')}")
    print(f"Trabajos de Remotive descargados: {len(jobs)}")

    return jobs


def save_raw_jobs(jobs: list[dict], source: str) -> Path:
    """
    Guarda los trabajos en bruto en data/raw como JSON.
    """
    output_dir = Path("data/raw")
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"{source}_{timestamp}.json"

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(jobs, file, ensure_ascii=False, indent=2)

    return output_path


if __name__ == "__main__":
    jobs = fetch_remotive_jobs()
    output_path = save_raw_jobs(jobs, source="remotive_all")

    print("Fuente: Remotive")
    print(f"Trabajos en bruto extraídos: {len(jobs)}")
    print(f"Guardado en: {output_path}")