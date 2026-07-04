from extract.remotive_api import (
    fetch_remotive_jobs,
    save_raw_jobs as save_remotive_jobs,
)

from extract.arbeitnow_api import (
    fetch_arbeitnow_jobs,
    save_raw_jobs as save_arbeitnow_jobs,
)

from extract.wwr_rss import (
    fetch_wwr_rss_jobs,
    save_raw_jobs as save_wwr_rss_jobs,
)

from extract.wwr_scraper import (
    fetch_wwr_programming_jobs,
    save_raw_jobs as save_wwr_scraper_jobs,
)


def run_bronze_extraction_pipeline() -> None:
    """
    Ejecuta la etapa bronze del pipeline.

    Objetivo de la etapa bronze:
    - Extraer datos crudos desde todas las fuentes disponibles.
    - No aplicar filtros de negocio.
    - No limpiar ni transformar datos.
    - Guardar archivos JSON en data/raw/.
    """

    print("Iniciando etapa de extracción")


    total_jobs = 0

    # --------------------------------------------------
    # Remotive API
    # --------------------------------------------------
    try:
        print("\n[1/4] Extrayendo ofertas desde Remotive API...")

        remotive_jobs = fetch_remotive_jobs()
        remotive_path = save_remotive_jobs(
            remotive_jobs,
            source="remotive_all"
        )

        print(f"Remotive - ofertas extraídas: {len(remotive_jobs)}")
        print(f"Archivo generado: {remotive_path}")

        total_jobs += len(remotive_jobs)

    except Exception as error:
        print(f"Error extrayendo datos desde Remotive: {error}")

    # --------------------------------------------------
    # Arbeitnow API
    # --------------------------------------------------
    try:
        print("\n[2/4] Extrayendo ofertas desde Arbeitnow API...")

        arbeitnow_jobs = fetch_arbeitnow_jobs(
            max_pages=20,
            delay_seconds=1.0
        )

        arbeitnow_path = save_arbeitnow_jobs(
            arbeitnow_jobs,
            source="arbeitnow_all"
        )

        print(f"Arbeitnow - ofertas extraídas: {len(arbeitnow_jobs)}")
        print(f"Archivo generado: {arbeitnow_path}")

        total_jobs += len(arbeitnow_jobs)

    except Exception as error:
        print(f"Error extrayendo datos desde Arbeitnow: {error}")

    # --------------------------------------------------
    # We Work Remotely RSS
    # --------------------------------------------------
    try:
        print("\n[3/4] Extrayendo ofertas desde We Work Remotely RSS...")

        wwr_rss_jobs = fetch_wwr_rss_jobs()
        wwr_rss_path = save_wwr_rss_jobs(
            wwr_rss_jobs,
            source="we_work_remotely_rss_all"
        )

        print(f"We Work Remotely RSS - ofertas extraídas: {len(wwr_rss_jobs)}")
        print(f"Archivo generado: {wwr_rss_path}")

        total_jobs += len(wwr_rss_jobs)

    except Exception as error:
        print(f"Error extrayendo datos desde We Work Remotely RSS: {error}")

    # --------------------------------------------------
    # We Work Remotely Scraper
    # --------------------------------------------------
    try:
        print("\n[4/4] Extrayendo ofertas desde We Work Remotely Scraper...")

        wwr_scraper_jobs = fetch_wwr_programming_jobs()
        wwr_scraper_path = save_wwr_scraper_jobs(
            wwr_scraper_jobs,
            source="we_work_remotely_scraper_all"
        )

        print(f"We Work Remotely Scraper - ofertas extraídas: {len(wwr_scraper_jobs)}")
        print(f"Archivo generado: {wwr_scraper_path}")

        total_jobs += len(wwr_scraper_jobs)

    except Exception as error:
        print(f"Error extrayendo datos desde We Work Remotely Scraper: {error}")

    print("\n==========================================")
    print("Etapa BRONZE finalizada")
    print(f"Total de ofertas crudas extraídas: {total_jobs}")
    print("Archivos guardados en: data/raw/")
    print("==========================================")


if __name__ == "__main__":
    run_bronze_extraction_pipeline()