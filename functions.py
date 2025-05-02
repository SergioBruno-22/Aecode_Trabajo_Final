import numpy as np
import matplotlib.pyplot as plt
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

def calcular_gamma(X: np.ndarray, M: np.ndarray) -> float:
    n = X.shape[0]
    return (X.T @ M @ np.ones(n)) / (X.T @ M @ X)

def calcular_aceleraciones(Sa: float, Gamma: float, X: np.ndarray) -> np.ndarray:
    return Sa * Gamma * X

def calcular_fuerzas(M: np.ndarray, U_hat: np.ndarray) -> np.ndarray:
    return M @ U_hat

def calcular_cortantes(F: np.ndarray) -> list:
    return [F[i:].sum() for i in range(len(F))]

def main_calculos(n_pisos, H, Z, S, TP, TL, U, CT, R0, masas, modos, Ia, Ip):
    """Función principal de cálculos con parámetros dinámicos"""
    # Validación de inputs
    if len(masas) != n_pisos or any(len(m) != n_pisos for m in modos.values()):
        raise ValueError("Los vectores deben tener longitud igual al número de pisos")
    
    # Cálculo de parámetros dinámicos
    T = (5 * H) / CT
    R = Ia * Ip * R0
    
    # Matriz de masas diagonal
    M = np.diag(masas)
    
    # Factores de participación para cada modo
    Gammas = {}
    U_hats = {}
    Fs = {}
    
    for modo, X in modos.items():
        Gammas[modo] = calcular_gamma(X, M)
        U_hats[modo] = calcular_aceleraciones((Z * U * calcular_coeficiente_C(T, TP, TL) * S) / R * 9.81, 
                                            Gammas[modo], X)
        Fs[modo] = calcular_fuerzas(M, U_hats[modo])
    
    # Cortantes para cada modo
    Vs = {modo: calcular_cortantes(F) for modo, F in Fs.items()}
    
    # Combinación de resultados
    Vrisc = np.sqrt(sum(np.array(V)**2 for V in Vs.values())).tolist()
    Vsum_abs = (sum(np.abs(V) for V in Vs.values())).tolist()
    Vrnc_h = (0.25 * np.array(Vsum_abs) + 0.75 * np.array(Vrisc)).tolist()
    Vreal = (np.array(Vrnc_h) * 0.75 * R).tolist()
    
    return {
        'F1': Fs.get('Modo1', []).tolist(),
        'V1': Vs.get('Modo1', []),
        'Vsum_abs': Vsum_abs,
        'Vrisc': Vrisc,
        'Vrnc_h': Vrnc_h,
        'Vreal': Vreal,
        'modos': list(modos.keys())
    }

def generar_graficos_principales(F, V, n_pisos):
    """Genera los primeros dos gráficos con parámetros dinámicos"""
    pisos = list(range(1, n_pisos+1))
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Gráfico de fuerzas
    ax1.bar(pisos, F, color='#1f77b4', edgecolor='black')
    ax1.set_title('Distribución de Fuerzas Sísmicas', fontsize=14)
    ax1.set_xlabel('Piso', fontsize=12)
    ax1.set_ylabel('Fuerza (ton)', fontsize=12)
    ax1.grid(True, linestyle='--', alpha=0.6)
    
    # Gráfico de cortantes
    ax2.bar(pisos, V, color='#2ca02c', edgecolor='black')
    ax2.set_title('Cortantes por Nivel', fontsize=14)
    ax2.set_xlabel('Piso', fontsize=12)
    ax2.set_ylabel('Cortante (ton)', fontsize=12)
    ax2.grid(True, linestyle='--', alpha=0.6)
    
    plt.tight_layout()
    return fig

def generar_graficos_combinaciones(resultados, n_pisos):
    """Genera gráfico comparativo de combinaciones"""
    pisos = list(range(1, n_pisos+1))
    width = 0.2
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    for i, (key, values) in enumerate({
        'Vsum_abs': resultados['Vsum_abs'],
        'V_RISC': resultados['Vrisc'],
        'V_RNC': resultados['Vrnc_h'],
        'V_Real': resultados['Vreal']
    }.items()):
        ax.bar([p + i*width for p in range(n_pisos)], values, width, label=key)
    
    ax.set_title('Comparación de Métodos de Combinación', fontsize=14)
    ax.set_xlabel('Piso', fontsize=12)
    ax.set_ylabel('Cortante (ton)', fontsize=12)
    ax.set_xticks([p + 1.5*width for p in range(n_pisos)])
    ax.set_xticklabels(pisos)
    ax.legend()
    ax.grid(True, linestyle='--', alpha=0.6)
    
    return fig

def generar_reporte_excel(Vreal, n_pisos):
    """Genera reporte Excel con parámetros dinámicos"""
    wb = Workbook()
    ws = wb.active
    ws.title = "Resultados"
    
    # Cabecera
    ws.append(['Piso', 'Cortante Real (ton)'])
    
    # Datos
    for piso, valor in enumerate(Vreal, start=1):
        ws.append([piso, valor])
    
    # Gráfico
    chart = LineChart()
    data = Reference(ws, min_col=2, min_row=1, max_row=n_pisos+1)
    chart.add_data(data, titles_from_data=True)
    chart.title = "Distribución de Cortantes Reales"
    chart.x_axis.title = "Piso"
    chart.y_axis.title = "Cortante (ton)"
    ws.add_chart(chart, "D2")
    
    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer
