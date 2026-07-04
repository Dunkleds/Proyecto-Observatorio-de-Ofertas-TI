from datetime import datetime
from pathlib import Path
import json
import time
import requests
from bs4 import BeautifulSoup


WWR_PROGRAMMING_URL = "https://weworkremotely.com/categories/remote-programming-jobs"


def fetch_html(url: str) -> str:
    """
    Descarga el contenido HTML de una página pública de ofertas de trabajo.
    """
    headers = {
        "User-Agent": "observatorio-ofertas-ti/1.0 (academic portfolio project)"
    }

    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()

    return response.text


def parse_wwr_jobs(html: str) -> list[dict]:
    """
    Parsea las tarjetas de trabajo de la página de categoría de We Work Remotely.

    """
    soup = BeautifulSoup(html, "html.parser")

    jobs = []

    job_sections = soup.select("section.jobs li.feature, section.jobs li:not(.view-all)")

    for item in job_sections:
        link_tag = item.select_one("a[href*='/remote-jobs/']")

        if not link_tag:
            continue

        spans = item.select("span.company, span.title, span.region")

        company = spans[0].get_text(strip=True) if len(spans) > 0 else None
        title = spans[1].get_text(strip=True) if len(spans) > 1 else None
        region = spans[2].get_text(strip=True) if len(spans) > 2 else "Remote"

        relative_url = link_tag.get("href")
        url = f"https://weworkremotely.com{relative_url}" if relative_url else None

        if not title or not url:
            continue

        jobs.append({
            "external_id": url,
            "title": title,
            "company": company,
            "location": region,
            "job_type": None,
            "category": "Programming",
            "description": None,
            "url": url,
            "published_at": None,
            "source": "we_work_remotely_scraper",
        })

    return jobs


def fetch_wwr_programming_jobs() -> list[dict]:
    """
    Extrae trabajos de la categoría de programación de We Work Remotely mediante scraping HTML.
    """
    html = fetch_html(WWR_PROGRAMMING_URL)

    time.sleep(1)

    jobs = parse_wwr_jobs(html)

    return jobs


def save_raw_jobs(jobs: list[dict], source: str) -> Path:
    """
    Guarda los trabajos extraidos en data/raw como JSON.
    """
    output_dir = Path("data/raw")
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"{source}_{timestamp}.json"

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(jobs, file, ensure_ascii=False, indent=2)

    return output_path


if __name__ == "__main__":
    jobs = fetch_wwr_programming_jobs()
    output_path = save_raw_jobs(jobs, source="we_work_remotely_scraper")

    print(f"Fuente: We Work Remotely HTML scraper")
    print(f"Trabajos extraidos: {len(jobs)}")
    print(f"Guardado en: {output_path}")