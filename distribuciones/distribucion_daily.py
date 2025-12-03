import pandas as pd
import numpy as np
import scipy.stats as st
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# --- CONFIGURACIÓN ---
FILE_NAME = 'PV_Elec_Gas3.csv'
SCRIPT_DIR = Path(__file__).resolve().parent
FILE_PATH = SCRIPT_DIR / FILE_NAME

print(f"--- ANALIZANDO PRODUCCIÓN SOLAR: {FILE_PATH} ---")

try:
    df = pd.read_csv(FILE_NAME)
    
    # 1. Procesar Fechas y Des-acumular
    df['Fecha'] = pd.to_datetime(df.iloc[:, 0], dayfirst=True, errors='coerce')
    df = df.dropna(subset=['Fecha']).sort_values('Fecha')
    df['Solar_Diaria'] = df.iloc[:, 1].diff() # Restar acumulado anterior
    
    # Filtro básico de errores (negativos o cero absoluto)
    df = df[df['Solar_Diaria'] > 0.1]
    
    # 2. Limpieza de Outliers (IQR Global)
    Q1 = df['Solar_Diaria'].quantile(0.25)
    Q3 = df['Solar_Diaria'].quantile(0.75)
    IQR = Q3 - Q1
    data_clean = df[(df['Solar_Diaria'] >= (Q1 - 1.5*IQR)) & (df['Solar_Diaria'] <= (Q3 + 1.5*IQR))].copy()
    
    # 3. Detectar Estaciones
    data_clean['Mes'] = data_clean['Fecha'].dt.month
    mes_pico = data_clean.groupby('Mes')['Solar_Diaria'].mean().idxmax()
    
    if mes_pico in [5, 6, 7, 8]:
        print("-> Hemisferio: NORTE")
        meses_verano = [6, 7, 8]
        meses_invierno = [12, 1, 2]
    else:
        print("-> Hemisferio: SUR")
        meses_verano = [12, 1, 2]
        meses_invierno = [6, 7, 8]
        
    # Separar Datasets
    df_verano = data_clean[data_clean['Mes'].isin(meses_verano)]['Solar_Diaria']
    df_invierno = data_clean[data_clean['Mes'].isin(meses_invierno)]['Solar_Diaria']
    
    # 4. Ajuste Gamma (Separado)
    dist = st.gamma
    params_ver = dist.fit(df_verano)
    params_inv = dist.fit(df_invierno)

    # --- GRAFICOS MEJORADOS ---
    sns.set(style='whitegrid')
    fig, axes = plt.subplots(1, 2, figsize=(16, 6), sharey=False)

    # Usar percentiles para definir el rango X y evitar outliers extremos
    combined = np.concatenate([df_verano.values, df_invierno.values])
    x_max = max(np.percentile(combined, 99.5), 1.0)
    x_plot = np.linspace(0, x_max * 1.05, 1000)

    # Plot comparado de histogramas y PDFs
    ax = axes[0]
    sns.histplot(df_invierno, bins=30, stat='density', color='steelblue', alpha=0.45, label='Invierno (datos)', ax=ax)
    sns.histplot(df_verano, bins=30, stat='density', color='tomato', alpha=0.35, label='Verano (datos)', ax=ax)
    ax.plot(x_plot, dist.pdf(x_plot, *params_inv), color='navy', lw=2.5, label='Invierno (Gamma fit)')
    ax.plot(x_plot, dist.pdf(x_plot, *params_ver), color='darkred', lw=2.5, label='Verano (Gamma fit)')

    # Estadísticos: media, mediana y banda P10-P90
    def annotate_stats(axis, data, color, tag):
        if len(data) == 0:
            return
        mean = np.mean(data)
        median = np.median(data)
        p10, p90 = np.percentile(data, [10, 90])
        axis.axvline(mean, color=color, linestyle='--', lw=1.6, label=f'{tag} Media {mean:.1f} kWh')
        axis.axvline(median, color=color, linestyle=':', lw=1.4, label=f'{tag} Mediana {median:.1f} kWh')
        axis.axvspan(p10, p90, color=color, alpha=0.08)

    annotate_stats(ax, df_invierno.values, 'navy', 'Invierno')
    annotate_stats(ax, df_verano.values, 'darkred', 'Verano')

    ax.set_xlim(0, x_max * 1.05)
    ax.set_xlabel('Producción diaria (kWh)')
    ax.set_ylabel('Densidad')
    ax.set_title('Producción Solar: Invierno vs Verano (sin outliers)')
    ax.legend(fontsize=9, loc='upper right')

    # Eje derecho: CDF comparativa
    ax2 = axes[1]
    sorted_inv = np.sort(df_invierno.values)
    sorted_ver = np.sort(df_verano.values)
    if len(sorted_inv) > 0:
        cdf_inv = np.arange(1, len(sorted_inv) + 1) / len(sorted_inv)
        ax2.plot(sorted_inv, cdf_inv, color='navy', lw=2, label='Invierno ECDF')
    if len(sorted_ver) > 0:
        cdf_ver = np.arange(1, len(sorted_ver) + 1) / len(sorted_ver)
        ax2.plot(sorted_ver, cdf_ver, color='darkred', lw=2, label='Verano ECDF')

    ax2.set_xlim(0, x_max * 1.05)
    ax2.set_ylim(0, 1)
    ax2.set_xlabel('Producción diaria (kWh)')
    ax2.set_ylabel('CDF')
    ax2.set_title('ECDF: Distribución Acumulada')
    ax2.grid(alpha=0.2)
    ax2.legend(fontsize=9)

    # Texto resumen con parámetros para copiar en simulaciones
    summary = f"Invierno params: {params_inv}\nVerano params: {params_ver}"
    fig.text(0.5, 0.01, summary, ha='center', va='bottom', fontsize=9, bbox=dict(facecolor='white', alpha=0.6))

    plt.tight_layout(rect=[0, 0.03, 1, 0.97])
    plt.show()

    print("\n" + "="*50)
    print("📋 COPIA ESTOS DATOS PARA EL ARCHIVO 'simulaciones.py':")
    print(f"SOLAR_PARAMS_INVIERNO = {params_inv}")
    print(f"SOLAR_PARAMS_VERANO   = {params_ver}")
    print("="*50)

except Exception as e:
    print(f"Error: {e}")