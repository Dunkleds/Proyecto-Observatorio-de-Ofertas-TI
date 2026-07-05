from pathlib import Path

import pandas as pd
import streamlit as st


BASE_DIR = Path(__file__).resolve().parents[1]
GOLD_DIR = BASE_DIR / "data" / "procesada" / "gold"


st.set_page_config(
    page_title="Observatorio de Ofertas TI",
    page_icon="📊",
    layout="wide",
)


def read_gold_csv(filename: str) -> pd.DataFrame:
    file_path = GOLD_DIR / filename

    if not file_path.exists():
        st.error(
            f"No se encontró el archivo {file_path}. "
            "Ejecuta primero la gold layer con: python src/main_gold.py"
        )
        st.stop()

    return pd.read_csv(file_path)


@st.cache_data
def load_data() -> dict[str, pd.DataFrame]:
    return {
        "resumen": read_gold_csv("vw_resumen_general.csv"),
        "fuentes": read_gold_csv("vw_ofertas_por_fuente.csv"),
        "skills": read_gold_csv("vw_top_skills.csv"),
        "empresas": read_gold_csv("vw_top_empresas.csv"),
        "meses": read_gold_csv("vw_ofertas_por_mes.csv"),
        "skills_fuente": read_gold_csv("vw_skills_por_fuente.csv"),
        "data_engineering": read_gold_csv("vw_demanda_data_engineering.csv"),
    }


def show_metric_cards(resumen_df: pd.DataFrame) -> None:
    resumen = resumen_df.iloc[0]

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("Ofertas TI", int(resumen.get("total_ofertas_ti", 0)))
    col2.metric("Empresas", int(resumen.get("total_empresas", 0)))
    col3.metric("Fuentes", int(resumen.get("total_fuentes", 0)))
    col4.metric("Ubicaciones", int(resumen.get("total_ubicaciones", 0)))
    col5.metric("Skills detectadas", int(resumen.get("total_skills_detectadas", 0)))


def show_bar_chart(
    df: pd.DataFrame,
    index_col: str,
    value_col: str,
    title: str,
    top_n: int | None = None,
) -> None:
    chart_df = df.copy()

    if top_n:
        chart_df = chart_df.head(top_n)

    chart_df = chart_df[[index_col, value_col]].set_index(index_col)

    st.subheader(title)
    st.bar_chart(chart_df)


def show_line_chart_by_month(df: pd.DataFrame) -> None:
    if df.empty:
        st.info("No hay datos mensuales disponibles.")
        return

    chart_df = df.copy()
    chart_df["mes"] = pd.to_datetime(chart_df["mes"], errors="coerce")
    chart_df = chart_df.dropna(subset=["mes"])
    chart_df = chart_df.sort_values("mes")
    chart_df = chart_df.set_index("mes")

    st.subheader("Evolución mensual de ofertas")
    st.line_chart(chart_df[["total_ofertas"]])


def main() -> None:
    st.title("📊 Observatorio de Ofertas TI")
    st.caption(
        "Dashboard generado a partir de la gold layer del pipeline "
        "bronze → silver → gold."
    )

    data = load_data()

    resumen_df = data["resumen"]
    fuentes_df = data["fuentes"]
    skills_df = data["skills"]
    empresas_df = data["empresas"]
    meses_df = data["meses"]
    skills_fuente_df = data["skills_fuente"]
    data_engineering_df = data["data_engineering"]

    st.sidebar.header("Configuración")
    top_n = st.sidebar.slider(
        "Cantidad de elementos en rankings",
        min_value=5,
        max_value=30,
        value=10,
        step=5,
    )

    st.sidebar.markdown("---")
    st.sidebar.write("Fuente de datos:")
    st.sidebar.code("data/procesada/gold/")

    show_metric_cards(resumen_df)

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        show_bar_chart(
            df=fuentes_df,
            index_col="source",
            value_col="total_ofertas",
            title="Ofertas por fuente",
        )

    with col2:
        show_bar_chart(
            df=skills_df,
            index_col="skill_name",
            value_col="total_menciones",
            title=f"Top {top_n} skills más solicitadas",
            top_n=top_n,
        )

    st.markdown("---")

    col3, col4 = st.columns(2)

    with col3:
        show_bar_chart(
            df=empresas_df,
            index_col="company",
            value_col="total_ofertas",
            title=f"Top {top_n} empresas con más ofertas",
            top_n=top_n,
        )

    with col4:
        show_bar_chart(
            df=data_engineering_df,
            index_col="skill_name",
            value_col="total_menciones",
            title="Demanda de skills Data Engineering",
        )

    st.markdown("---")

    show_line_chart_by_month(meses_df)

    st.markdown("---")

    st.subheader("Skills por fuente")

    if skills_fuente_df.empty:
        st.info("No hay datos de skills por fuente.")
    else:
        selected_source = st.selectbox(
            "Selecciona una fuente",
            sorted(skills_fuente_df["source"].dropna().unique()),
        )

        filtered_skills = (
            skills_fuente_df[skills_fuente_df["source"] == selected_source]
            .sort_values("total_menciones", ascending=False)
            .head(top_n)
        )

        show_bar_chart(
            df=filtered_skills,
            index_col="skill_name",
            value_col="total_menciones",
            title=f"Top skills en {selected_source}",
        )

    st.markdown("---")

    with st.expander("Ver tablas gold"):
        st.write("Resumen general")
        st.dataframe(resumen_df)

        st.write("Top skills")
        st.dataframe(skills_df.head(top_n))

        st.write("Top empresas")
        st.dataframe(empresas_df.head(top_n))

        st.write("Demanda Data Engineering")
        st.dataframe(data_engineering_df)


if __name__ == "__main__":
    main()