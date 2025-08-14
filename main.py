import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- Título de la app ---
st.title("📊 Análisis Exploratorio de Datos Aleatorios")

# --- Generar datos aleatorios ---
np.random.seed(42)
data = pd.DataFrame({
    "Categoría": [f"C{i}" for i in range(1, 6)],
    "Valor_1": np.random.randint(10, 100, 5),
    "Valor_2": np.random.randint(50, 150, 5)
})

st.subheader("Datos generados")
st.dataframe(data)

# --- Análisis básico ---
st.subheader("Estadísticas descriptivas")
st.write(data.describe())

# --- Visualización 1: Barras ---
st.subheader("Gráfico de Barras")
fig_bar, ax_bar = plt.subplots()
ax_bar.bar(data["Categoría"], data["Valor_1"], color="skyblue")
ax_bar.set_xlabel("Categoría")
ax_bar.set_ylabel("Valor 1")
ax_bar.set_title("Barras de Valor_1 por Categoría")
st.pyplot(fig_bar)

# --- Visualización 2: Líneas ---
st.subheader("Gráfico de Líneas")
fig_line, ax_line = plt.subplots()
ax_line.plot(data["Categoría"], data["Valor_1"], marker="o", label="Valor_1")
ax_line.plot(data["Categoría"], data["Valor_2"], marker="o", label="Valor_2")
ax_line.set_xlabel("Categoría")
ax_line.set_ylabel("Valores")
ax_line.set_title("Líneas de Valor_1 y Valor_2")
ax_line.legend()
st.pyplot(fig_line)
