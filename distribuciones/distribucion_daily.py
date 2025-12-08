import pandas as pd
import numpy as np
import scipy.stats as st
import matplotlib.pyplot as plt
import seaborn as sns

FILE_NAME = 'PV_Elec_Gas3.csv'

print(f"--- ANALIZANDO PRODUCCIÓN SOLAR (WEIBULL - ESCALA DE GRISES) ---")

try:
    df = pd.read_csv(FILE_NAME)
    
    # Procesamos fechas y desacumulamos
    df['Fecha'] = pd.to_datetime(df.iloc[:, 0], dayfirst=True, errors='coerce')
    df = df.dropna(subset=['Fecha']).sort_values('Fecha')
    df['Solar_Diaria'] = df.iloc[:, 1].diff() # Restar acumulado anterior
    
    # Filtro básico de valores anómalos
    df = df[df['Solar_Diaria'] > 0.1]
    
    # 2. Limpieza de Outliers (IQR Global)
    Q1 = df['Solar_Diaria'].quantile(0.25)
    Q3 = df['Solar_Diaria'].quantile(0.75)
    IQR = Q3 - Q1
    data_clean = df[(df['Solar_Diaria'] >= (Q1 - 1.5*IQR)) & (df['Solar_Diaria'] <= (Q3 + 1.5*IQR))].copy()
    
    # Separamos en esatciones
    data_clean['Mes'] = data_clean['Fecha'].dt.month
    mes_pico = data_clean.groupby('Mes')['Solar_Diaria'].mean().idxmax()
    
    if mes_pico in [5, 6, 7, 8]:
        meses_verano = [6, 7, 8]
        meses_invierno = [12, 1, 2]
    else:
        meses_verano = [12, 1, 2]
        meses_invierno = [6, 7, 8]
        
    # Separar Datasets
    df_verano = data_clean[data_clean['Mes'].isin(meses_verano)]['Solar_Diaria']
    df_invierno = data_clean[data_clean['Mes'].isin(meses_invierno)]['Solar_Diaria']
    
    # Ajustamos con Weibull
    dist = st.weibull_min
    
    params_ver = dist.fit(df_verano)
    params_inv = dist.fit(df_invierno)
    
    # Gráficos
    plt.figure(figsize=(12, 5))
    sns.set_style("whitegrid") # Fondo blanco limpio
    
    x_plot = np.linspace(0, max(data_clean['Solar_Diaria']), 1000)
    
    # Invierno
    plt.subplot(1, 2, 1)
    sns.histplot(df_invierno, stat="density", color="gray", alpha=0.4, label="Datos Reales", element="step")
    # Línea Sólida
    plt.plot(x_plot, dist.pdf(x_plot, *params_inv), color='black', linestyle='-', lw=2.5, label='Ajuste Weibull')
    plt.title("INVIERNO (Producción Solar)")
    plt.xlabel("Producción diaria (kWh)")
    plt.ylabel("Densidad")
    plt.legend()
    
    # Verano
    plt.subplot(1, 2, 2)
    sns.histplot(df_verano, stat="density", color="gray", alpha=0.4, label="Datos Reales", element="step")
    # Línea Sólida 
    plt.plot(x_plot, dist.pdf(x_plot, *params_ver), color='black', linestyle='-', lw=2.5, label='Ajuste Weibull')
    plt.title("VERANO (Producción Solar)")
    plt.xlabel("Producción diaria (kWh)")
    plt.ylabel("Densidad")
    plt.legend()
    
    plt.tight_layout()
    plt.show()

    print("\n" + "="*50)
    print("📋 COPIA ESTOS DATOS (Shape, Location, Scale):")
    print(f"SOLAR_PARAMS_INVIERNO = {params_inv}")
    print(f"SOLAR_PARAMS_VERANO   = {params_ver}")
    print("="*50)

except Exception as e:
    print(f"Error: {e}")
