# Proyecto Final - AECODE - Python Aplicado a Ingenieria Civil

import streamlit as st
import numpy as np
import functions as f
import matplotlib.pyplot as plt
from io import BytesIO

# Configuración de la página
st.set_page_config(page_title="Análisis Sísmico", layout="wide")
st.title("📊 Análisis Sísmico de Edificios")

# Sidebar para parámetros de entrada
with st.sidebar:
    st.header("⚙️ Parámetros de Entrada")
    g = 9.81
    H = st.number_input("Altura total (m)", value=3.0, step=0.1)
    Z = st.number_input("Factor de zona", value=0.45, step=0.05)
    S = st.number_input("Factor de suelo", value=1.0, step=0.1)
    TP = st.number_input("Período TP (s)", value=0.4, step=0.05)
    TL = st.number_input("Período TL (s)", value=2.5, step=0.1)
    U = st.number_input("Factor de uso", value=1.0, step=0.1)
    CT = st.number_input("Coeficiente CT", value=35.0, step=1.0)
    R0 = st.number_input("Factor R0", value=8, step=1)
    m1 = st.number_input("Masa pisos 1-4 (ton)", value=31.80, step=0.1)
    m5 = st.number_input("Masa piso 5 (ton)", value=27.50, step=0.1)

# Vectores modales predefinidos (podrían hacerse editables)
X1 = np.array([0.03112, 0.05959, 0.08302, 0.09940, 0.10834])
X2 = np.array([-0.08102, -0.10493, -0.05484, 0.03358, 0.10609])
X3 = np.array([0.10415, 0.03021, -0.09525, -0.05769, 0.09176])

# Procesamiento principal
if st.button("🔄 Calcular y Graficar"):
    with st.spinner("Realizando cálculos..."):
        # Ejecutar cálculos
        resultados = f.main_calculos(H, Z, S, TP, TL, U, CT, R0, m1, m5, X1, X2, X3)
        
        # Mostrar resultados
        st.subheader("📈 Resultados Gráficos")
        
        # Gráficos en pestañas
        tab1, tab2 = st.tabs(["Fuerzas y Cortantes", "Combinaciones de Cortantes"])
        
        with tab1:
            fig1, fig2 = f.generar_graficos_principales(
                resultados['F1'], 
                resultados['V1']
            )
            st.pyplot(fig1)
            st.pyplot(fig2)
        
        with tab2:
            fig3 = f.generar_graficos_combinaciones(
                resultados['Vsum_abs'],
                resultados['Vrisc'],
                resultados['Vrnc_h'],
                resultados['Vreal']
            )
            st.pyplot(fig3)
        
        # Reporte Excel
        st.subheader("📊 Reporte de Resultados")
        excel_buffer = f.generar_reporte_excel(resultados['Vreal'])
        st.download_button(
            label="📥 Descargar Reporte Excel",
            data=excel_buffer,
            file_name="Reporte_Sismico.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        # Mostrar valores numéricos
        with st.expander("🔍 Ver valores numéricos"):
            st.write("**Fuerzas Modales (F1):**", resultados['F1'])
            st.write("**Cortante Base (V1):**", resultados['V1'])
            st.write("**V_RISC:**", resultados['Vrisc'])
            st.write("**V_Real:**", resultados['Vreal'])