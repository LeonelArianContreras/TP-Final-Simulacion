# Hogares Sostenibles: Modelo de Simulación Energética

Un hogar inteligente busca implementar una solución de autoabastecimiento energético mediante la instalación de un sistema 
de paneles solares. El sistema se compone de paneles con una potencia total **PPS** y una batería con una capacidad de almacenamiento **CB**.


El objetivo principal es satisfacer la demanda eléctrica del hogar, la cual está determinada por una función de densidad
de probabilidad (f.d.p.) y es influenciada por la cantidad de electrodomésticos (**QE**). La producción de energía del panel también sigue una f.d.p..



### Lógica del Sistema
La simulación opera bajo la siguiente lógica diaria:

1.  **Balance Energético:** La energía generada (**PE**) cubre el consumo instantáneo (**CE**).
2.  **Excedente:** Si `PE > CE`, el sobrante se almacena en la batería (**E**) hasta su capacidad máxima (**CB**).
3.  **Déficit:** Si `PE < CE`, se usa la batería.
4.  **Red Eléctrica:** Si `PE + E < CE`, la energía faltante se compra a la red.
5.  **Modo Ahorro:**
    * Si la batería cae por debajo del punto crítico (**PMA**), se activa el modo ahorro.
    * En este modo, el **50% del consumo** se abastece forzosamente desde la red para proteger la batería.
6.  **Mantenimiento:**
    * Si la cantidad de veces que se activa el modo ahorro llega a un límite (**LMA**), se llama al técnico.
    * El técnico demora una cantidad de días variable (f.d.p.) para realizar el mantenimiento y evitar la degradación permanente de la batería.

### Variables estocásticas y de entorno:

* **Estaciones:**
    * *Verano:* Amanece 6:00 AM, anochece 8:00 PM.
    * *Invierno:* Amanece 8:00 AM, anochece 6:00 PM.
* **Climatología:** Existe una probabilidad diaria del **26,6%** de día nublado, disminuyendo drásticamente la generación.
* **Modo Ahorro:** Para preservar la vida útil de la batería, el sistema activa un "modo ahorro". 
Si el **nivel** de la **batería cae** por debajo de un **punto crítico (PMA)**, como anteriormente se mencionó, 
el 50% de toda la demanda eléctrica restante de ese día se abastecerá forzosamente desde la red eléctrica, independientemente de la generación solar.


### Metodología
* **Tipo de Simulación:** Avance del tiempo a intervalos constantes.
* **Delta T:** $\Delta t = 1$ día.


---

## Objetivo de la Simulación

Determinar la **configuración óptima** de las variables de control (`PPS`, `CB`, `PMA`) para lograr:

*  **Maximizar:** Porcentaje de ahorro de energía (PAEE).
*  **Minimizar:** Gasto mensual (GPMEE) y llamadas al técnico (PRT).
*  **Asegurar:** Baja frecuencia de modo ahorro (PMMA) y nivel saludable de batería (NPEB).

---

## Métricas de Evaluación

| Métrica | Descripción |
| :--- | :--- |
| **PAEE** | Porcentaje de ahorro de energía eléctrica (vs. escenario sin paneles). |
| **GPMEE** | Gasto promedio mensual de energía eléctrica ($/mes). |
| **PMMA** | Promedio mensual de activaciones del modo ahorro. |
| **NPEB** | Nivel promedio de energía en la batería (kWh). |
| **PRT** | Promedio de revisiones técnicas por mes. |

---

## Análisis Técnico

### Clasificación de Variables

| Tipo Variable | Variable | Descripción |
| :--- | :--- | :--- |
| **DATOS** | **PE** | Producción diaria de energía alterna (kWh). |
| | **CE** | Consumo de Energía diario (kWh). |
| | **DT** | Demora del técnico de baterías. |
| **CONTROL** | **PPS** | Potencia total de los paneles solares. |
| | **QE** | Cantidad de electrodomésticos. |
| | **CB** | Capacidad de la batería. |
| | **PMA** | Punto de activación del modo de ahorro. |
| | **LCB** | Límite de ciclos de batería (antes de llamar al técnico). |
| **ESTADO** | **E** | Cantidad de Energía en Batería actual (kWh). |
| **RESULTADO** | **PAEE** | Porcentaje de ahorro de energía eléctrica. |
| | **PSMEE** | Porcentaje uso mensual de energía eléctrica. |
| | **PMMA** | Promedio mensual de veces que se usó el modo ahorro. |
| | **NPEB** | Nivel promedio de energía en la batería. |
| | **PRT** | Promedio de revisiones técnicas por mes. |

### Clasificación de Eventos

| Tipo Evento | Evento |
| :--- | :--- |
| **PROPIO** | Generación de energía |
| | Uso de energía convencional |
| | Uso de energía en modo ahorro |
| **Comprometidos ΔT anteriores** | Llegada del técnico de baterías |
| **Comprometidos ΔT futuro** | Llamada al técnico de baterías |

### TEF (Tabla de Eventos Futuros)

| Variable | Descripción |
| :--- | :--- |
| **FRT** | Fecha de Revisión Técnica |