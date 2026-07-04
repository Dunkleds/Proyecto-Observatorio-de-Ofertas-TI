from datetime import datetime
from pathlib import Path
import json
import requests


ARBEITNOW_API_URL = "https://www.arbeitnow.com/api/job-board-api"


def fetch_arbeitnow_jobs(page: int = 1) -> list[dict]:
    """
    Extrae trabajos de la API pública de Arbeitnow.
    """
    params = {
        "page": page
    }

    response = requests.get(
        ARBEITNOW_API_URL,
        params=params,
        timeout=30,
        headers={"User-Agent": "observatorio-ofertas-ti/1.0"}
    )

    response.raise_for_status()

    data = response.json()
    jobs = data.get("data", [])

    return jobs


def fetch_multiple_pages(max_pages: int = 3) -> list[dict]:
    """
    Extrae trabajos de múltiples páginas.
    """
    all_jobs = []

    for page in range(1, max_pages + 1):
        jobs = fetch_arbeitnow_jobs(page=page)

        if not jobs:
            break

        all_jobs.extend(jobs)

    return all_jobs


def save_raw_jobs(jobs: list[dict], source: str) -> Path:
    """
    Guarda los trabajos extraídos en data/raw como JSON.
    """
    output_dir = Path("data/raw")
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"{source}_{timestamp}.json"

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(jobs, file, ensure_ascii=False, indent=2)

    return output_path


if __name__ == "__main__":
    jobs = fetch_multiple_pages(max_pages=3)
    output_path = save_raw_jobs(jobs, source="arbeitnow")

    print(f"Fuente: Arbeitnow")
    print(f"Trabajos extraídos: {len(jobs)}")
    print(f"Guardado en: {output_path}")