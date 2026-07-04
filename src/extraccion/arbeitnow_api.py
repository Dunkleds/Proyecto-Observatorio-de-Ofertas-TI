from datetime import datetime
from pathlib import Path
import json
import time
import requests


ARBEITNOW_API_URL = "https://www.arbeitnow.com/api/job-board-api"


def fetch_arbeitnow_page(page: int = 1) -> list[dict]:
    """
    Extrae trabajos de una página específica de la API de Arbeitnow.
    """
    params = {
        "page": page
    }

    response = requests.get(
        ARBEITNOW_API_URL,
        params=params,
        timeout=30,
        headers={"User-Agent": "observatorio-ofertas-ti/1.0 academic project"},
    )

    response.raise_for_status()

    data = response.json()
    jobs = data.get("data", [])

    return jobs


def fetch_arbeitnow_jobs(max_pages: int = 20, delay_seconds: float = 1.0) -> list[dict]:
    """
    Extrae trabajos de múltiples páginas de la API de Arbeitnow.

    """
    all_jobs = []

    for page in range(1, max_pages + 1):
        print(f"Obteniendo la página de Arbeitnow {page}...")

        jobs = fetch_arbeitnow_page(page=page)

        if not jobs:
            print("No hay más trabajos disponibles.")
            break

        all_jobs.extend(jobs)

        print(f"Pagina {page}: {len(jobs)} trabajos descargados")
        print(f"Total de trabajos acumulados: {len(all_jobs)}")

        time.sleep(delay_seconds)

    return all_jobs


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
    jobs = fetch_arbeitnow_jobs(max_pages=20, delay_seconds=1.0)
    output_path = save_raw_jobs(jobs, source="arbeitnow_all")

    print("Source: Arbeitnow")
    print(f"Raw jobs extracted: {len(jobs)}")
    print(f"Saved to: {output_path}")