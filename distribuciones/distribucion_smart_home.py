import pandas as pd
import numpy as np
import scipy.stats as st
import matplotlib.pyplot as plt
import seaborn as sns

# --- CONFIGURACIÓN ---
FILE_NAME = 'D202.csv'

print(f"--- PROCESANDO CONSUMO ENERGÉTICO: {FILE_NAME} ---")

try:
    # 1. Cargar el CSV
    df = pd.read_csv(FILE_NAME)
    
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
    
    # --- GRÁFICOS ---
    plt.figure(figsize=(14, 6))
    
    # Definir eje X común para que sean comparables
    max_val = max(daily_df['USAGE'].max(), 1.0)
    x_plot = np.linspace(0, max_val, 1000)
    
    # Plot Invierno
    plt.subplot(1, 2, 1)
    sns.histplot(data_invierno, stat="density", color="skyblue", alpha=0.6, label="Datos Reales")
    plt.plot(x_plot, dist.pdf(x_plot, *params_inv), 'b-', lw=3, label="Ajuste Gamma")
    plt.title(f"❄️ INVIERNO (Promedio: {data_invierno.mean():.1f} kWh)")
    plt.xlabel("Consumo Diario (kWh)")
    plt.legend()
    plt.grid(alpha=0.3)
    
    # Plot Verano
    plt.subplot(1, 2, 2)
    sns.histplot(data_verano, stat="density", color="orange", alpha=0.6, label="Datos Reales")
    plt.plot(x_plot, dist.pdf(x_plot, *params_ver), 'r-', lw=3, label="Ajuste Gamma")
    plt.title(f"☀️ VERANO (Promedio: {data_verano.mean():.1f} kWh)")
    plt.xlabel("Consumo Diario (kWh)")
    plt.legend()
    plt.grid(alpha=0.3)
    
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