import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ---------------------------
# Configuración de página
# ---------------------------
st.set_page_config(
    page_title="EDA Aleatorio Interactivo",
    page_icon="📊",
    layout="wide"
)

# ---------------------------
# Utilidades
# ---------------------------
def generar_df(n_cat: int, seed: int, min_v: int, max_v: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    df = pd.DataFrame({
        "Categoría": [f"C{i+1}" for i in range(n_cat)],
        "Valor_1": rng.integers(min_v, max_v + 1, n_cat),
        "Valor_2": rng.integers(min_v, max_v + 1, n_cat),
    })
    return df

def normalizar_cols(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    out = df.copy()
    for c in cols:
        total = out[c].sum()
        out[c] = (out[c] / total * 100) if total != 0 else 0
    return out

# ---------------------------
# Estado (session_state)
# ---------------------------
if "seed" not in st.session_state:
    st.session_state.seed = 42
if "df" not in st.session_state:
    st.session_state.df = generar_df(n_cat=6, seed=st.session_state.seed, min_v=10, max_v=100)

# ---------------------------
# Sidebar: Generación de datos
# ---------------------------
st.sidebar.header("⚙️ Generación de datos")
n_cat = st.sidebar.slider("Número de categorías", 3, 30, 8, step=1)
min_v = st.sidebar.number_input("Valor mínimo", value=10, min_value=0, step=1)
max_v = st.sidebar.number_input("Valor máximo", value=120, min_value=1, step=1)
if max_v <= min_v:
    st.sidebar.error("El valor máximo debe ser mayor que el mínimo.")

seed_input = st.sidebar.number_input("Semilla (reproducibilidad)", value=st.session_state.seed, min_value=0, step=1)

col_btn1, col_btn2 = st.sidebar.columns(2)
regen = col_btn1.button("🔁 Regenerar")
rand_seed = col_btn2.button("🎲 Semilla aleatoria")

if rand_seed:
    seed_input = int(np.random.randint(0, 1_000_000))
if regen or rand_seed:
    st.session_state.seed = seed_input
    st.session_state.df = generar_df(n_cat=n_cat, seed=seed_input, min_v=min_v, max_v=max_v)

# ---------------------------
# Sidebar: Opciones de visualización
# ---------------------------
st.sidebar.header("📊 Opciones de visualización")
cols_num = ["Valor_1", "Valor_2"]
serie_lineas = st.sidebar.multiselect("Series para líneas", options=cols_num, default=cols_num)
serie_barras = st.sidebar.selectbox("Serie para barras", options=cols_num, index=0)

ordenar_por = st.sidebar.selectbox(
    "Ordenar por",
    options=["Categoría"] + cols_num,
    index=0,
    help="Orden ascendente por la columna seleccionada"
)
asc = st.sidebar.toggle("Orden ascendente", value=True)
normalizar = st.sidebar.toggle("Mostrar en porcentaje (%)", value=False)

mostrar_tabla = st.sidebar.toggle("Mostrar tabla de datos", value=True)
descargar = st.sidebar.toggle("Habilitar descarga CSV", value=True)

# ---------------------------
# Datos (post-procesamiento)
# ---------------------------
df = st.session_state.df.copy()

# Orden
df = df.sort_values(by=ordenar_por, ascending=asc).reset_index(drop=True)

# Normalización opcional
df_plot = normalizar_cols(df, cols_num) if normalizar else df

# ---------------------------
# Encabezado
# ---------------------------
st.title("📊 EDA Interactivo con Streamlit + Plotly")
st.caption("Genera datos sintéticos, explóralos con estadísticas rápidas y visualízalos con **barras** y **líneas** configurables.")

# ---------------------------
# Estadísticas y tabla
# ---------------------------
with st.expander("📈 Estadísticas descriptivas", expanded=True):
    stats = df[cols_num].describe().T
    if normalizar:
        st.info("Estás viendo estadísticas de datos **normalizados (%)**.")
    st.dataframe(stats, use_container_width=True)

if mostrar_tabla:
    st.subheader("🔢 Datos")
    st.dataframe(df_plot, use_container_width=True)

# ---------------------------
# Gráficos (dos columnas)
# ---------------------------
left, right = st.columns(2, gap="large")

# Barras
with left:
    st.subheader("Barras")
    fig_bar = px.bar(
        df_plot,
        x="Categoría",
        y=serie_barras,
        text=serie_barras,
        labels={"Categoría": "Categoría", serie_barras: "Valor (%)" if normalizar else "Valor"},
        title=f"{'%' if normalizar else ''} {serie_barras} por Categoría"
    )
    fig_bar.update_traces(texttemplate="%{text:.1f}" if normalizar else "%{text}", textposition="outside")
    fig_bar.update_layout(xaxis_title="Categoría", yaxis_title="%" if normalizar else "Valor", uniformtext_minsize=10, uniformtext_mode="hide")
    st.plotly_chart(fig_bar, use_container_width=True, theme="streamlit")

# Líneas
with right:
    st.subheader("Líneas")
    if not serie_lineas:
        st.warning("Selecciona al menos una serie para el gráfico de líneas en el panel lateral.")
    else:
        df_long = df_plot.melt(id_vars="Categoría", value_vars=serie_lineas, var_name="Serie", value_name="Valor")
        fig_line = px.line(
            df_long,
            x="Categoría",
            y="Valor",
            color="Serie",
            markers=True,
            labels={"Categoría": "Categoría", "Valor": "Valor (%)" if normalizar else "Valor"},
            title=f"Serie(s) {'normalizadas (%)' if normalizar else ''}"
        )
        st.plotly_chart(fig_line, use_container_width=True, theme="streamlit")

# ---------------------------
# Descarga
# ---------------------------
if descargar:
    st.subheader("⬇️ Descargar datos")
    st.download_button(
        label="Descargar CSV",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="datos_aleatorios.csv",
        mime="text/csv",
        use_container_width=True
    )

# ---------------------------
# Notas
# ---------------------------
with st.expander("ℹ️ Notas", expanded=False):
    st.markdown(
        """
- **Normalizar (%)** convierte cada columna numérica en porcentaje del total de su columna.
- **Ordenar por** permite reordenar dinámicamente la tabla y los gráficos.
- **Regenerar** usa la semilla indicada; **Semilla aleatoria** crea una nueva semilla al vuelo.
- Puedes elegir una o dos series para líneas, y una serie para barras.
        """
    )
