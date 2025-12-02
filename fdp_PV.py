import pandas as pd
import numpy as np
import scipy.stats as st
import matplotlib.pyplot as plt

# 1. Cargar y Preprocesar (Igual que antes)
df = pd.read_csv('PV_Elec_Gas3.csv')
df.columns = ['Fecha', 'Solar_Acumulada', 'Elec_Diaria', 'Gas_Diario']
df['Fecha'] = pd.to_datetime(df['Fecha'], dayfirst=True)
df = df.sort_values('Fecha')

df['Solar_Diaria'] = df['Solar_Acumulada'].diff()

# Limpiar datos
data = df['Solar_Diaria'].dropna()
data = data[data > 0.1] # Filtramos días de producción muy baja/error

# 2. Definir las distribuciones candidatas 
distribuciones = [        
    st.gamma,       
    st.weibull_min
]

best_dist = None
best_params = {}
best_sse = np.inf

# Configuración del gráfico
plt.figure(figsize=(12, 6))
y, x, _ = plt.hist(data, bins=50, density=True, alpha=0.5, color='gray', label='Datos Reales')
x_plot = np.linspace(min(data), max(data), 1000)

# 3. Bucle de Ajuste (Fitting Loop)
print("Resultados del Ajuste (SSE: Menor es Mejor):")
print("-" * 50)

for dist in distribuciones:
    try:
        # Ajustar la distribución a los datos
        params = dist.fit(data)
        
        # Calcular el error cuadrático (SSE)
        x_mid = (x[:-1] + x[1:]) / 2
        pdf_at_bins = dist.pdf(x_mid, *params)
        sse = np.sum((y - pdf_at_bins)**2)
        
        print(f"{dist.name.ljust(15)}: Error (SSE) = {sse:.5f} | Params: {params[:3]}...")
        print(f"\n--- Distribución {dist.name} ---")
        print(f"Shape (k/alpha): {params[0]}")
        print(f"Loc: {params[1]}")
        print(f"Scale: {params[2]}")
        print(f"Tupla completa para copiar: {params}")
        
        # Graficar
        plt.plot(x_plot, dist.pdf(x_plot, *params), lw=2, label=f'{dist.name}')

        # Guardar el ganador
        if sse < best_sse:
            best_sse = sse
            best_dist = dist
            best_params = params
             
    except Exception as e:
        # Algunos ajustes fallan, especialmente con data sesgada.
        print(f"Error al ajustar {dist.name}: {e}")

# 4. Mostrar Ganador
print("-" * 50)
print(f"🏆 LA MEJOR DISTRIBUCIÓN ES: {best_dist.name.upper()} (SSE: {best_sse:.5f})")
print(f"📋 PARÁMETROS PARA TU SIMULADOR: {best_params}")
print("\n¡Usa estos parámetros para generar números aleatorios en tu simulación!")

plt.title(f'Ajuste de Distribuciones a Producción Solar (Ganadora: {best_dist.name.upper()})')
plt.legend(loc='upper right')
plt.grid(alpha=0.3)
plt.show()