import pandas as pd
import numpy as np
import scipy.stats as st
import matplotlib.pyplot as plt

# --- CONFIGURACIÓN ---
FILE_NAME = 'PV_Elec_Gas3.csv'

print(f"--- ANALIZANDO PRODUCCIÓN SOLAR: {FILE_NAME} ---")

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
    
    # Graficar comparativa
    plt.figure(figsize=(12, 5))
    x_plot = np.linspace(0, max(data_clean['Solar_Diaria']), 1000)
    
    plt.plot(x_plot, dist.pdf(x_plot, *params_inv), 'b-', lw=2, label='Invierno Ajustado')
    plt.plot(x_plot, dist.pdf(x_plot, *params_ver), 'r-', lw=2, label='Verano Ajustado')
    plt.hist(df_invierno, density=True, alpha=0.3, color='blue')
    plt.hist(df_verano, density=True, alpha=0.3, color='red')
    plt.title("Comparativa Solar: Invierno vs Verano (Sin Outliers)")
    plt.legend()
    plt.show()

    print("\n" + "="*50)
    print("📋 COPIA ESTOS DATOS PARA EL ARCHIVO 'simulaciones.py':")
    print(f"SOLAR_PARAMS_INVIERNO = {params_inv}")
    print(f"SOLAR_PARAMS_VERANO   = {params_ver}")
    print("="*50)

except Exception as e:
    print(f"Error: {e}")