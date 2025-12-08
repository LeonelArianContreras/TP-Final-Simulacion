import pandas as pd
import numpy as np
import scipy.stats as st
import matplotlib.pyplot as plt
import seaborn as sns

FILE_NAME = 'D202.csv'

print(f"--- PROCESANDO CONSUMO ENERGÉTICO (ESCALA DE GRISES) ---")

try:
    # Cargamos y procesamos
    df = pd.read_csv(FILE_NAME)
    df['DATE_OBJ'] = pd.to_datetime(df['DATE'])
    
    # Agrupamos por día
    daily_df = df.groupby('DATE_OBJ')['USAGE'].sum().reset_index()
    daily_df = daily_df[daily_df['USAGE'] > 0.1] # Filtro de ceros
    
    # Separamos estaciones
    daily_df['Month'] = daily_df['DATE_OBJ'].dt.month
    
    meses_invierno = [12, 1, 2]
    meses_verano = [6, 7, 8]
    
    data_invierno = daily_df[daily_df['Month'].isin(meses_invierno)]['USAGE']
    data_verano = daily_df[daily_df['Month'].isin(meses_verano)]['USAGE']
    
    # Ajustamos con Weibull
    params_inv_weibull = st.weibull_min.fit(data_invierno)
    params_ver_weibull = st.weibull_min.fit(data_verano)
    
    # Gráficos para el paper
    plt.figure(figsize=(14, 6))
    
    # Los ponemos en byn
    sns.set_style("whitegrid") 
    
    max_val = max(daily_df['USAGE'].max(), 1.0)
    x_plot = np.linspace(0, max_val, 1000)
    
    # Plot de invierno
    plt.subplot(1, 2, 1)
    
    # Histograma en gris claro
    sns.histplot(data_invierno, stat="density", color="gray", alpha=0.4, label="Datos Reales", element="step")
    
    # Línea Weibull en Negro 
    plt.plot(x_plot, st.weibull_min.pdf(x_plot, *params_inv_weibull), 
             color='black', linestyle='-', lw=2.5, label="Ajuste Weibull")
             
    plt.title(f"INVIERNO (Ajuste Weibull)")
    plt.xlabel("Consumo Diario (kWh)")
    plt.ylabel("Densidad")
    plt.legend()
    
    # Plot 2 verano
    plt.subplot(1, 2, 2)
    
    # Histograma en gris claro
    sns.histplot(data_verano, stat="density", color="gray", alpha=0.4, label="Datos Reales", element="step")
    
    # Línea Weibull en Negro 
    plt.plot(x_plot, st.weibull_min.pdf(x_plot, *params_ver_weibull), 
             color='black', linestyle='-', lw=2.5, label="Ajuste Weibull")
             
    plt.title(f"VERANO (Ajuste Weibull)")
    plt.xlabel("Consumo Diario (kWh)")
    plt.ylabel("Densidad")
    plt.legend()
    
    plt.tight_layout()
    plt.show()
    
    # Imprimimos resultados
    print("\n" + "="*60)
    print("📋 DATOS PARA TU SIMULACIÓN (Weibull):")
    print("-" * 20)
    print("INVIERNO (Shape, Location, Scale):")
    print(f"   {params_inv_weibull}")
    print("-" * 20)
    print("VERANO (Shape, Location, Scale):")
    print(f"   {params_ver_weibull}")
    print("="*60)

except Exception as e:
    print(f"Error: {e}")
