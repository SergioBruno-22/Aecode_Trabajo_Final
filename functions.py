import numpy as np
import matplotlib.pyplot as plt
import functions as f
from openpyxl import Workbook
from openpyxl.chart import LineChart, Reference
from io import BytesIO

def calcular_coeficiente_C(t: float, TP: float, TL: float) -> float:
    if t < TP:
        return 2.5
    elif t > TL:
        return 2.5 * TP / t
    else:
        return 2.5 * TP * TL / t**2

def calcular_factor_k(t: float) -> float:
    return 1.0 if t <= 0.5 else 0.75 + 0.5 * t

def calcular_gamma(X: np.ndarray, M: np.ndarray) -> float:
    return (X.T @ M @ np.ones(5)) / (X.T @ M @ X)

def calcular_aceleraciones(Sa: float, Gamma: float, X: np.ndarray) -> np.ndarray:
    return Sa * Gamma * X

def calcular_fuerzas(M: np.ndarray, U_hat: np.ndarray) -> np.ndarray:
    return M @ U_hat

def calcular_cortantes(F: np.ndarray) -> list:
    return [F[i:].sum() for i in range(5)]

def main_calculos(H, Z, S, TP, TL, U, CT, R0, m1, m5, X1, X2, X3):
    """Función principal de cálculos adaptada para Streamlit"""
    # Cálculos iniciales
    T = (5 * H) / CT
    R = 8.0  # Ia * Ip * R0
    
    # Matriz de masas
    M = np.diag([m1, m1, m1, m1, m5])
    
    # Factores de participación
    Gamma1 = calcular_gamma(X1, M)
    Gamma2 = calcular_gamma(X2, M)
    Gamma3 = calcular_gamma(X3, M)
    
    # Aceleraciones y fuerzas
    Cc = calcular_coeficiente_C(T, TP, TL)
    Cs = (Z * U * Cc * S) / R
    Sa = Cs * 9.81
    
    U_hat1 = calcular_aceleraciones(Sa, Gamma1, X1)
    U_hat2 = calcular_aceleraciones(Sa, Gamma2, X2)
    U_hat3 = calcular_aceleraciones(Sa, Gamma3, X3)
    
    F1 = calcular_fuerzas(M, U_hat1)
    F2 = calcular_fuerzas(M, U_hat2)
    F3 = calcular_fuerzas(M, U_hat3)
    
    # Cortantes
    V1 = calcular_cortantes(F1)
    V2 = calcular_cortantes(F2)
    V3 = calcular_cortantes(F3)
    
    # Combinaciones
    Vrisc = np.sqrt(np.array(V1)**2 + np.array(V2)**2 + np.array(V3)**2).tolist()
    Vsum_abs = (np.abs(V1) + np.abs(V2) + np.abs(V3)).tolist()
    Vrnc_h = (0.25 * np.array(Vsum_abs) + 0.75 * np.array(Vrisc)).tolist()
    Vreal = (np.array(Vrnc_h) * 0.75 * R).tolist()
    
    return {
        'F1': F1.tolist(),
        'V1': V1,
        'Vsum_abs': Vsum_abs,
        'Vrisc': Vrisc,
        'Vrnc_h': Vrnc_h,
        'Vreal': Vreal
    }

def generar_graficos_principales(F, V):
    """Genera los primeros dos gráficos"""
    pisos = [1, 2, 3, 4, 5]
    
    # Gráfico 1: Fuerzas
    fig1, ax1 = plt.subplots(figsize=(8, 4))
    ax1.bar(pisos, F, color='skyblue', edgecolor='black')
    ax1.set_title('Fuerzas Sísmicas por Piso (F)')
    ax1.set_xlabel('Piso')
    ax1.set_ylabel('Fuerza [ton]')
    ax1.grid(True, linestyle='--', alpha=0.6)
    
    # Gráfico 2: Cortantes
    fig2, ax2 = plt.subplots(figsize=(8, 4))
    ax2.bar(pisos, V, color='lightgreen', edgecolor='black')
    ax2.set_title('Cortante en la Base por Piso (V)')
    ax2.set_xlabel('Piso')
    ax2.set_ylabel('Cortante [ton]')
    ax2.grid(True, linestyle='--', alpha=0.6)
    
    return fig1, fig2

def generar_graficos_combinaciones(Vsum_abs, Vrisc, Vrnc_h, Vreal):
    """Genera el gráfico de combinaciones"""
    pisos = [1, 2, 3, 4, 5]
    width = 0.2
    
    fig, ax = plt.subplots(figsize=(10, 6))
    x = np.arange(len(pisos))
    
    ax.bar(x - 1.5*width, Vsum_abs, width, label='Vsum_abs', color='#1f77b4')
    ax.bar(x - 0.5*width, Vrisc, width, label='V_RISC', color='#ff7f0e')
    ax.bar(x + 0.5*width, Vrnc_h, width, label='V_RNC_H', color='#2ca02c')
    ax.bar(x + 1.5*width, Vreal, width, label='V_Real', color='#d62728')
    
    ax.set_title('Comparación de Métodos de Combinación')
    ax.set_xlabel('Piso')
    ax.set_ylabel('Cortante [ton]')
    ax.set_xticks(x)
    ax.set_xticklabels(pisos)
    ax.legend()
    ax.grid(True, linestyle='--', alpha=0.6)
    
    return fig

def generar_reporte_excel(Vreal):
    """Genera el reporte en Excel y devuelve un buffer para Streamlit"""
    wb = Workbook()
    ws = wb.active
    ws.title = "Resultados"
    
    # Encabezados
    ws['A1'] = 'Piso'
    ws['B1'] = 'V_Real (ton)'
    
    # Datos
    for i, valor in enumerate(Vreal, start=2):
        ws.cell(row=i, column=1, value=i-1)
        ws.cell(row=i, column=2, value=valor)
    
    # Gráfico
    chart = LineChart()
    data = Reference(ws, min_col=2, min_row=1, max_row=6)
    chart.add_data(data, titles_from_data=True)
    chart.title = "Cortante Real en la Base"
    chart.x_axis.title = "Piso"
    chart.y_axis.title = "Cortante (ton)"
    ws.add_chart(chart, "D2")
    
    # Guardar en buffer
    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    
    return buffer