from datetime import datetime
from pathlib import Path
import requests
import json

Remotive_API_URL = "https://remotive.com/api/remote-jobs"

def fetch_remotive_jobs(search: str | None = None,
                        category: str | None = None,
                        limit: int | None = None) -> list[dict]:
    """ 
    Extraemos los trabajos de la API de Remotive.io según el término de búsqueda proporcionado.
    """
    params = {}

    if search:
        params["search"] = search

    if category:
        params["category"] = category

    if limit:
        params["limit"] = limit

    response = requests.get(Remotive_API_URL,
                            params=params,
                            timeout=30, 
                            headers={"User-Agent": "observatorio-ofertas-ti/1.0"}
                            )
    response.raise_for_status()  # Lanza una excepción si la respuesta no es exitosa
    data = response.json()
    jobs = data.get("jobs", [])
    return jobs

def save_jobs_to_json(jobs: list[dict], source: str) -> Path:
    """
    Guardamos los trabajos extraidos en un archivo JSON en la carpeta data/raw.
    """
    output_dir = Path("data/raw")
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"{source}_{timestamp}.json"

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(jobs, file, ensure_ascii=False, indent=2)
    return output_file

if __name__ == "__main__":
    jobs = fetch_remotive_jobs(search="data", category=None, limit=200)
    output_path = save_jobs_to_json(jobs, source="remotive")
    print(f"La fuente de datos Remotive.io ha sido extraida y guardada en: {output_path}\n")
    print(f"Se han extraido {len(jobs)} ofertas de trabajo.\n")