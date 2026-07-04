from extraccion.remotive_api import fetch_remotive_jobs, save_raw_jobs as save_remotive_jobs
from extraccion.arbeitnow_api import fetch_multiple_pages, save_raw_jobs as save_arbeitnow_jobs
from extraccion.wwr_rss import fetch_wwr_rss_jobs, save_raw_jobs as save_wwr_rss_jobs
from extraccion.wwr_scraper import fetch_wwr_programming_jobs, save_raw_jobs as save_wwr_scraper_jobs


def run_extraction_pipeline() -> None:

    print("Iniciando pipeline de extracción...")

    print("Extrayendo jobs de Remotive...")
    remotive_jobs = fetch_remotive_jobs(search="data engineer")
    remotive_path = save_remotive_jobs(remotive_jobs, source="remotive")
    print(f"Jobs de Remotive: {len(remotive_jobs)} | File: {remotive_path}")

    print("Extrayendo jobs de Arbeitnow...")
    arbeitnow_jobs = fetch_multiple_pages(max_pages=3)
    arbeitnow_path = save_arbeitnow_jobs(arbeitnow_jobs, source="arbeitnow")
    print(f"Jobs de Arbeitnow: {len(arbeitnow_jobs)} | File: {arbeitnow_path}")

    print("Extrayendo jobs de We Work Remotely RSS...")
    wwr_rss_jobs = fetch_wwr_rss_jobs()
    wwr_rss_path = save_wwr_rss_jobs(wwr_rss_jobs, source="we_work_remotely_rss")
    print(f"Jobs de We Work Remotely RSS: {len(wwr_rss_jobs)} | File: {wwr_rss_path}")

    print("Extrayendo jobs de We Work Remotely scraper...")
    wwr_scraper_jobs = fetch_wwr_programming_jobs()
    wwr_scraper_path = save_wwr_scraper_jobs(
        wwr_scraper_jobs,
        source="we_work_remotely_scraper"
    )
    print(f"Jobs de We Work Remotely scraper: {len(wwr_scraper_jobs)} | File: {wwr_scraper_path}")

    total_jobs = (
        len(remotive_jobs)
        + len(arbeitnow_jobs)
        + len(wwr_rss_jobs)
        + len(wwr_scraper_jobs)
    )

    print("Pipeline de extracción completado.")
    print(f"Total de jobs extraídos: {total_jobs}")


if __name__ == "__main__":
    run_extraction_pipeline()