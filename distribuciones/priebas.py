import pandas as pd

# --- CONFIGURACIÓN ---
FILE_NAME = 'smart_home_energy_consumption_large.csv'
OUTPUT_NAME = 'dias_con_un_solo_electrodomestico.csv'

print(f"--- ANALIZANDO DÍAS MONOTEMÁTICOS (1 Solo Aparato) ---")

try:
    # 1. Cargar datos
    df = pd.read_csv(FILE_NAME)
    df.columns = [c.strip() for c in df.columns]
    df['Date'] = pd.to_datetime(df['Date'])

    # 2. AGRUPAR POR DÍA Y CASA -> CONTAR APARATOS
    # Esto nos dice: "El día X, la Casa Y prendió Z aparatos"
    conteo_diario = df.groupby(['Home ID', 'Date']).size().reset_index(name='Cantidad_Aparatos')

    # 3. FILTRAR: Queremos días donde Cantidad_Aparatos == 1
    dias_solitarios = conteo_diario[conteo_diario['Cantidad_Aparatos'] == 1]

    # 4. CONTAR: ¿Cuántos de esos días tuvo cada casa?
    resultado_por_casa = dias_solitarios.groupby('Home ID').size().reset_index(name='Dias_con_1_Solo_Uso')
    
    # Ordenamos para ver quiénes son los más "ahorradores" o minimalistas
    resultado_por_casa = resultado_por_casa.sort_values('Dias_con_1_Solo_Uso', ascending=False)

    # --- MOSTRAR RESULTADOS ---
    print("\nTop 10 Casas con más días de un solo uso:")
    print("-" * 50)
    print(resultado_por_casa.head(10))
    print("-" * 50)

    # Estadística opcional interesante:
    total_dias_analizados = len(conteo_diario)
    total_dias_1_uso = len(dias_solitarios)
    porcentaje = (total_dias_1_uso / total_dias_analizados) * 100
    print(f"\nDe un total de {total_dias_analizados} días-casa registrados en todo el dataset,")
    print(f"en {total_dias_1_uso} ocasiones ({porcentaje:.2f}%) se prendió solo una cosa.")

    # Guardar
    resultado_por_casa.to_csv(OUTPUT_NAME, index=False)
    print(f"\nTabla completa guardada en: {OUTPUT_NAME}")

except Exception as e:
    print(f"Error: {e}")