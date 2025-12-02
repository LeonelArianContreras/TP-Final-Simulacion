import pandas as pd
import numpy as np
import scipy.stats as st
import matplotlib.pyplot as plt

# ==============================================================================
# 1. CONFIGURACIÓN: PARÁMETROS REALES (Copiados de tu consola)
# ==============================================================================

# --- CONSUMO (Dataset D202.csv) ---
# Invierno: ~18.5 kWh/día (Calefacción?) | Verano: ~9.2 kWh/día
CONSUMO_PARAMS_INVIERNO = (6.468657320847244, -2.771614471746993, 3.2919875899109767)
CONSUMO_PARAMS_VERANO   = (2.60736791363958, 3.3705618589665227, 2.229800106915757)

# --- SOLAR (Dataset PV_Elec_Gas3.csv) ---
# Invierno: ~3.3 kWh/día | Verano: ~18 kWh/día
SOLAR_PARAMS_INVIERNO = (1.6678779297865651, 0.16070725078743087, 1.8871140604934582)
SOLAR_PARAMS_VERANO   = (514.066769648103, -130.75223807209858, 0.2898945029981943)

# Archivo para leer la "forma" de la curva horaria (D202.csv)
FILE_PERFIL = 'D202.csv'

# ==============================================================================
# 2. FUNCIONES AUXILIARES
# ==============================================================================

def obtener_perfil_horario(archivo):
    """
    Lee el CSV para aprender a qué hora consume más la casa.
    Intenta leer formato D202 (START TIME) y si falla usa genérico.
    """
    try:
        df = pd.read_csv(archivo)
        
        # Caso 1: Formato D202 con columna 'START TIME' (ej: 0:15)
        if 'START TIME' in df.columns:
            # Convertimos "0:15" a hora numérica
            df['Hour'] = pd.to_datetime(df['START TIME'], format='%H:%M', errors='coerce').dt.hour
            perfil = df.groupby('Hour')['USAGE'].mean().values
            
        # Caso 2: Formato anterior con columna 'Time' o 'Date'
        else:
            df.columns = [c.strip() for c in df.columns] # Limpiar espacios
            if 'Time' in df.columns:
                df['Hour'] = pd.to_datetime(df['Time'], format='%H:%M', errors='coerce').dt.hour
            elif 'Date' in df.columns:
                df['Hour'] = pd.to_datetime(df['Date']).dt.hour
            perfil = df.groupby('Hour')['Energy Consumption (kWh)'].mean().values

        # Relleno y Normalización
        if len(perfil) < 24: 
            perfil = np.resize(perfil, 24)
        
        # Evitar división por cero
        suma = np.sum(perfil)
        if suma == 0: return np.array([1/24]*24)
        
        return perfil / suma

    except Exception as e:
        print(f"Advertencia: No se pudo leer perfil horario ({e}). Usando perfil genérico.")
        # Perfil genérico residencial (Pico nocturno)
        p = np.array([0.2, 0.2, 0.2, 0.2, 0.3, 0.8, 1.2, 1.0, 0.8, 0.6, 0.5, 0.5, 
                      0.6, 0.7, 0.8, 0.9, 1.2, 1.8, 2.5, 2.8, 2.5, 2.0, 1.0, 0.5])
        return p / np.sum(p)

def simular_escenario(dias, params_solar, params_consumo, perfil_consumo_pct):
    # Configuración Batería (Tesla Powerwall 2)
    CAPACIDAD_BATERIA = 13.5 # kWh
    bateria = 6.5            # Empezamos ~50%
    
    historia_bateria = []
    historia_solar = []
    historia_consumo = []
    
    for _ in range(dias):
        # 1. Generar TOTALES DEL DÍA (Aleatorios Gamma)
        sol_total = max(0, st.gamma.rvs(*params_solar))
        consumo_total = max(0, st.gamma.rvs(*params_consumo))
        
        # 2. Curvas Horarias
        horas = np.arange(24)
        
        # Solar (Campana Gauss a las 13hs)
        curva_solar = np.exp(-((horas - 13)**2) / (2 * 2.5**2))
        if np.sum(curva_solar) > 0:
            curva_solar = (curva_solar / np.sum(curva_solar)) * sol_total
            
        # Consumo (Perfil * Total) + Ruido leve
        ruido = np.random.normal(1, 0.1, 24)
        curva_consumo = perfil_consumo_pct * consumo_total * ruido
        curva_consumo = np.maximum(0, curva_consumo)
        
        # 3. Balance Hora a Hora
        for h in range(24):
            prod = curva_solar[h]
            cons = curva_consumo[h]
            balance = prod - cons
            
            if balance > 0:
                # Sobra -> Cargar
                bateria = min(CAPACIDAD_BATERIA, bateria + balance)
            else:
                # Falta -> Descargar
                bateria = max(0.0, bateria + balance)
                
            historia_solar.append(prod)
            historia_consumo.append(cons)
            historia_bateria.append(bateria)
            
    return historia_solar, historia_consumo, historia_bateria

# ==============================================================================
# 3. EJECUCIÓN
# ==============================================================================

print("--- INICIANDO SIMULACIÓN COMPARATIVA FINAL ---")
DIAS = 15
perfil_pct = obtener_perfil_horario(FILE_PERFIL)

# Escenario INVIERNO
sol_inv, cons_inv, bat_inv = simular_escenario(DIAS, SOLAR_PARAMS_INVIERNO, CONSUMO_PARAMS_INVIERNO, perfil_pct)

# Escenario VERANO
sol_ver, cons_ver, bat_ver = simular_escenario(DIAS, SOLAR_PARAMS_VERANO, CONSUMO_PARAMS_VERANO, perfil_pct)

# --- GRÁFICOS ---
horas = np.arange(len(bat_inv))
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True, sharey=False) # sharey=False para ver detalle en cada uno

# PLOT INVIERNO
ax1.set_title(f"❄️ INVIERNO: Déficit Energético (Consumo Alto vs Solar Bajo)", fontsize=14, color='navy', fontweight='bold')
# Eje Izquierdo (Potencia)
ax1.plot(horas, sol_inv, color='orange', label='Generación Solar', lw=1.5)
ax1.plot(horas, cons_inv, color='blue', alpha=0.7, label='Consumo Casa', lw=1.5)
ax1.set_ylabel("Potencia (kW)")
ax1.grid(alpha=0.3)
# Eje Derecho (Batería)
ax1_bis = ax1.twinx()
ax1_bis.fill_between(horas, bat_inv, color='green', alpha=0.1)
ax1_bis.plot(horas, bat_inv, color='green', lw=2, label='Batería (kWh)')
ax1_bis.set_ylim(0, 14.5)
ax1_bis.axhline(13.5, color='red', ls='--', alpha=0.5, label='Max Batería')
ax1_bis.set_ylabel("Batería (kWh)", color='green')
# Leyenda unificada
lines, labels = ax1.get_legend_handles_labels()
lines2, labels2 = ax1_bis.get_legend_handles_labels()
ax1.legend(lines + lines2, labels + labels2, loc='upper left')


# PLOT VERANO
ax2.set_title(f"☀️ VERANO: Superávit Energético (Consumo Bajo vs Solar Alto)", fontsize=14, color='darkred', fontweight='bold')
# Eje Izquierdo (Potencia)
ax2.plot(horas, sol_ver, color='orange', label='Generación Solar', lw=1.5)
ax2.plot(horas, cons_ver, color='blue', alpha=0.7, label='Consumo Casa', lw=1.5)
ax2.set_ylabel("Potencia (kW)")
ax2.grid(alpha=0.3)
# Eje Derecho (Batería)
ax2_bis = ax2.twinx()
ax2_bis.fill_between(horas, bat_ver, color='green', alpha=0.1)
ax2_bis.plot(horas, bat_ver, color='green', lw=2, label='Batería (kWh)')
ax2_bis.set_ylim(0, 14.5)
ax2_bis.axhline(13.5, color='red', ls='--', alpha=0.5)
ax2_bis.set_ylabel("Batería (kWh)", color='green')
ax2.set_xlabel("Horas Simuladas (0 a 360)")
# Leyenda unificada
lines, labels = ax2.get_legend_handles_labels()
lines2, labels2 = ax2_bis.get_legend_handles_labels()
ax2.legend(lines + lines2, labels + labels2, loc='upper left')

plt.tight_layout()
plt.show()

print("¡Simulación Finalizada!")
print("Nota: En Invierno verás la batería agotarse frecuentemente (línea verde en 0).")
print("Nota: En Verano verás la batería llena frecuentemente (línea verde en 13.5).")