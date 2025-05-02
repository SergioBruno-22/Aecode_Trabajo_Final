# Proyecto Final - AECODE - Python Aplicado a Ingenieria Civil

import streamlit as st
import numpy as np
import functions as f
from io import BytesIO

st.set_page_config(page_title="Análisis Sísmico Dinámico", layout="wide")
st.title("🏗️ Análisis Sísmico con Parámetros Dinámicos")

# Sidebar para parámetros editables
with st.sidebar:
    st.header("🔧 Parámetros de Configuración")
    
    # Parámetros principales
    n_pisos = st.number_input("Número de Pisos", 1, 10, 5)
    n_modos = st.number_input("Número de Modos", 1, 5, 3)
    
    # Factores de cálculo
    st.subheader("Factores de Cálculo")
    Ia = st.number_input("Factor Ia", 0.5, 2.0, 1.0)
    Ip = st.number_input("Factor Ip", 0.5, 2.0, 1.0)
    CT = st.number_input("Coeficiente CT", 10.0, 100.0, 35.0)
    R0 = st.number_input("Factor R0", 1, 10, 8)
    
    # Masas por piso
    st.subheader("Configuración de Masas")
    masa_base = st.number_input("Masa Base (ton)", 20.0, 50.0, 31.8)
    masa_ultimo = st.number_input("Masa Último Piso (ton)", 20.0, 50.0, 27.5)
    masas = [masa_base]*(n_pisos-1) + [masa_ultimo]
    
    # Vectores modales
    st.subheader("Vectores Modales")
    modos = {}
    for i in range(n_modos):
        modo = st.text_area(f"Modo {i+1} (valores separados por comas)", 
                          value=", ".join([f"{0.1*(j+1):.4f}" for j in range(n_pisos)]))
        try:
            modos[f"Modo{i+1}"] = np.array([float(x.strip()) for x in modo.split(',')])
        except:
            st.error("Formato incorrecto en los vectores modales")

# Parámetros fijos
H = st.sidebar.number_input("Altura Total (m)", 3.0, 50.0, 10.0)
Z = st.sidebar.number_input("Factor de Zona", 0.1, 1.0, 0.45)
S = st.sidebar.number_input("Factor de Suelo", 0.5, 2.0, 1.0)
TP = st.sidebar.number_input("Período TP (s)", 0.1, 1.0, 0.4)
TL = st.sidebar.number_input("Período TL (s)", 1.0, 5.0, 2.5)
U = st.sidebar.number_input("Factor de Uso", 0.5, 2.0, 1.0)

if st.button("🚀 Ejecutar Análisis"):
    try:
        with st.spinner("Realizando cálculo sísmico..."):
            resultados = f.main_calculos(
                n_pisos, H, Z, S, TP, TL, U, CT, R0, masas, modos, Ia, Ip
            )
            
            st.success("Análisis completado correctamente!")
            
            # Visualización de resultados
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Fuerzas Sísmicas")
                fig1 = f.generar_graficos_principales(resultados['F1'], resultados['V1'], n_pisos)
                st.pyplot(fig1)
                
            with col2:
                st.subheader("Comparación de Cortantes")
                fig2 = f.generar_graficos_combinaciones(resultados, n_pisos)
                st.pyplot(fig2)
            
            # Reporte Excel
            excel_buffer = f.generar_reporte_excel(resultados['Vreal'], n_pisos)
            st.download_button(
                label="📥 Descargar Reporte Completo",
                data=excel_buffer,
                file_name="analisis_sismico.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
    except Exception as e:
        st.error(f"Error en el cálculo: {str(e)}")
