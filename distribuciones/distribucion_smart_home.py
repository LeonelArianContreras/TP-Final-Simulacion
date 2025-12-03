import pandas as pd
import numpy as np
import scipy.stats as st
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# --- CONFIGURACIÓN ---
FILE_NAME = 'D202.csv'

# Resolver ruta del CSV relativa a este archivo, así el script funciona
# tanto si se ejecuta desde la carpeta `distribuciones` como desde el root.
SCRIPT_DIR = Path(__file__).resolve().parent
FILE_PATH = SCRIPT_DIR / FILE_NAME

print(f"--- PROCESANDO CONSUMO ENERGÉTICO: {FILE_PATH} ---")

try:
    # 1. Cargar el CSV
    df = pd.read_csv(FILE_PATH)
    
    # 2. Convertir la columna DATE a formato fecha real
    # Asumimos formato MM/DD/YYYY según tu snippet (ej: 10/22/2016)
    df['DATE_OBJ'] = pd.to_datetime(df['DATE'])
    
    # 3. AGRUPACIÓN CLAVE: Pasar de 15 min -> 1 DÍA
    # Sumamos todo el 'USAGE' de cada día
    daily_df = df.groupby('DATE_OBJ')['USAGE'].sum().reset_index()
    
    # Filtro básico para limpiar días con errores (consumo 0 o negativo)
    daily_df = daily_df[daily_df['USAGE'] > 0.1]
    
    # 4. Detectar Estaciones (Hemisferio Norte)
    daily_df['Month'] = daily_df['DATE_OBJ'].dt.month
    
    meses_invierno = [12, 1, 2] # Dic, Ene, Feb
    meses_verano = [6, 7, 8]    # Jun, Jul, Ago
    
    data_invierno = daily_df[daily_df['Month'].isin(meses_invierno)]['USAGE']
    data_verano = daily_df[daily_df['Month'].isin(meses_verano)]['USAGE']
    
    print(f"-> Días de Invierno analizados: {len(data_invierno)}")
    print(f"-> Días de Verano analizados:   {len(data_verano)}")
    print(f"-> Consumo Promedio Invierno:   {data_invierno.mean():.2f} kWh/día")
    print(f"-> Consumo Promedio Verano:     {data_verano.mean():.2f} kWh/día")
    
    # 5. Ajustar Distribuciones Gamma
    dist = st.gamma
    params_inv = dist.fit(data_invierno)
    params_ver = dist.fit(data_verano)
    
    # --- GRÁFICOS (mejorados) ---
    sns.set(style='whitegrid')
    plt.rcParams.update({'font.size': 11})
    fig, axes = plt.subplots(1, 2, figsize=(16, 7), sharey=False)

    # Definir eje X común usando percentiles para evitar outliers extremos
    combined = np.concatenate([data_invierno.values, data_verano.values])
    x_max = max(np.percentile(combined, 99.5), 1.0)
    x_plot = np.linspace(0, x_max * 1.05, 1000)

    def enhance_plot(ax, data, params, color, title):
        if len(data) == 0:
            ax.text(0.5, 0.5, 'No hay datos suficientes', ha='center')
            return

        # Histograma (densidad) y curva teórica
        sns.histplot(data, bins=30, stat='density', color=color, alpha=0.45, ax=ax)
        ax.plot(x_plot, dist.pdf(x_plot, *params), color=color, lw=3, label='Ajuste Gamma')

        # Estadísticos: media, mediana y percentiles
        mean = np.mean(data)
        median = np.median(data)
        p10, p90 = np.percentile(data, [10, 90])
        ax.axvline(mean, color='k', linestyle='--', lw=1.8, label=f'Media {mean:.1f} kWh')
        ax.axvline(median, color='k', linestyle=':', lw=1.6, label=f'Mediana {median:.1f} kWh')
        ax.axvspan(p10, p90, color=color, alpha=0.12)

        # Eje secundario: CDF empírica
        ax2 = ax.twinx()
        sorted_x = np.sort(data)
        cdf = np.arange(1, len(sorted_x) + 1) / len(sorted_x)
        ax2.plot(sorted_x, cdf, color='gray', lw=1.6, alpha=0.9, label='ECDF')
        ax2.set_ylim(0, 1)
        ax2.set_ylabel('CDF', fontsize=10)

        # Labels y estética
        ax.set_xlim(0, x_max * 1.05)
        ax.set_xlabel('Consumo Diario (kWh)')
        ax.set_title(title)
        ax.grid(alpha=0.25)

        # Caja de texto con resumen
        info = f'N={len(data)}\nMedia={mean:.2f} kWh\nMediana={median:.2f} kWh\nP10-P90={p10:.1f}-{p90:.1f} kWh'
        ax.text(0.98, 0.95, info, transform=ax.transAxes, ha='right', va='top', bbox=dict(facecolor='white', alpha=0.7), fontsize=9)

        # Leyenda compacta
        handles, labels = ax.get_legend_handles_labels()
        handles2, labels2 = ax2.get_legend_handles_labels()
        ax.legend(handles + handles2, labels + labels2, loc='upper right', fontsize=9)

    enhance_plot(axes[0], data_invierno.values, params_inv, 'skyblue', f'❄️ INVIERNO (Prom: {data_invierno.mean():.1f} kWh)')
    enhance_plot(axes[1], data_verano.values, params_ver, 'orange', f'☀️ VERANO (Prom: {data_verano.mean():.1f} kWh)')

    plt.tight_layout()
    plt.show()
    
    # 6. RESULTADOS PARA COPIAR
    print("\n" + "="*60)
    print("📋 COPIA ESTOS DATOS PARA TU ARCHIVO 'simulaciones.py':")
    print(f"CONSUMO_PARAMS_INVIERNO = {params_inv}")
    print(f"CONSUMO_PARAMS_VERANO   = {params_ver}")
    print("="*60)

except Exception as e:
    print(f"Error: {e}")