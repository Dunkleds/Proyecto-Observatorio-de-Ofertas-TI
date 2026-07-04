from datetime import datetime
from pathlib import Path
import json
import feedparser


WWR_RSS_URL = "https://weworkremotely.com/remote-jobs.rss"


def fetch_wwr_rss_jobs() -> list[dict]:
    """
    Extrae trabajos de la fuente RSS de We Work Remotely.

    """
    feed = feedparser.parse(WWR_RSS_URL)

    jobs = []

    for entry in feed.entries:
        job = {
            "external_id": entry.get("id"),
            "title": entry.get("title"),
            "company": None,
            "location": "Remote",
            "job_type": None,
            "category": None,
            "description": entry.get("summary"),
            "url": entry.get("link"),
            "published_at": entry.get("published"),
            "source": "we_work_remotely_rss",
        }

        jobs.append(job)

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
    jobs = fetch_wwr_rss_jobs()
    output_path = save_raw_jobs(jobs, source="we_work_remotely_rss_all")

    print("Fuente: We Work Remotely RSS")
    print(f"Trabajos en bruto extraídos: {len(jobs)}")
    print(f"Guardado en: {output_path}")