# Hogares Sostenibles: Modelo de Simulación Energética

Un hogar inteligente busca implementar una solución de autoabastecimiento energético mediante la instalación de un sistema de paneles solares. Se sabe que la instalación permite una potencia máxima de 5 kWp.

El sistema se compone de **CPS** paneles solares (máximo 10 unidades, 0,5 kWp c/u) y una batería con una capacidad de almacenamiento **CB**.

El objetivo principal es satisfacer la demanda eléctrica del hogar (**CE**), la cual está determinada por una función de densidad de probabilidad (f.d.p.) y es influenciada por la cantidad de electrodomésticos (**QE**). La producción de energía del panel (**PE**) también sigue una f.d.p.

### Lógica del Sistema
La simulación opera bajo la siguiente lógica diaria:

1.  **Balance Energético:** La energía generada (**PE**) se utiliza para satisfacer el consumo instantáneo (**CE**).
2.  **Excedente:** Si `PE > CE`, el excedente se almacena en la batería (**E**) hasta alcanzar su capacidad máxima (**CB**).
3.  **Déficit:** Si `PE < CE`, se utiliza la energía almacenada en la batería para cubrir el déficit.
4.  **Red Eléctrica:** Si `PE + E < CE` (generación y batería insuficientes), la energía faltante se compra a la red eléctrica.
5.  **Modo Ahorro:**
    * Si el nivel de la batería cae por debajo de un punto crítico (**PMA**), se activa el modo ahorro.
    * En este estado, el **50% del consumo** se abastece forzosamente desde la red eléctrica, independientemente de la generación solar, para proteger la batería.
6.  **Mantenimiento (Revisión Técnica):**
    * Se compara la capacidad de energía de una batería nueva vs. la usada.
    * Si la diferencia es menor a un umbral (**UCBR**), se considera llamar al técnico para instalar un dispositivo nuevo.
    * El técnico tiene una demora (**DTR**) en días para realizar la intervención.

### Variables estocásticas y de entorno:

* **Estaciones:** La producción se ve afectada por la estación:
    * *Verano:* Amanece 6:00 AM, anochece 8:00 PM.
    * *Invierno:* Amanece 8:00 AM, anochece 6:00 PM.
* **Climatología:** Existe una probabilidad diaria del **26,6%** de que el día esté nublado, disminuyendo drásticamente la energía generada.

### Metodología
* **Tipo de Simulación:** Avance del tiempo a intervalos constantes.
* **Delta T:** $\Delta t = 1$ día.

---

## Objetivo de la Simulación

Diseñar y ejecutar un modelo para determinar la **configuración óptima** de las variables de control, con el fin de:

* **Maximizar:** El autoabastecimiento energético (PSMEE).
* **Minimizar:** El porcentaje de energía de red usada (PRE) y las revisiones técnicas (PRT).
* **Monitorizar:** La frecuencia del modo ahorro (PMMA) y el nivel de batería (NPEB).

---

## Métricas de Evaluación (Resultados)

| Métrica | Nombre Completo | Descripción |
| :--- | :--- | :--- |
| **PRE** | Porcentaje de Red Eléctrica | Fracción de la demanda total no cubierta por el sistema, requiriendo importación externa. |
| **PERG** | Promedio de Energía Renovable Generada | Potencia bruta total que los paneles fueron capaces de producir (potencial máximo). |
| **PSMEE** | Promedio de uso mensual de energía renovable | Energía solar realmente aprovechada por el hogar (consumo directo o almacenamiento). |
| **PMMA** | Promedio mensual de modo ahorro | Frecuencia con la que el sistema entró en estado crítico (Batería < PMA). |
| **NPEB** | Nivel promedio de energía en batería | Promedio del estado de carga registrado. Indica sobredimensionamiento o riesgo de desabastecimiento. |
| **PRT** | Promedio de revisiones técnicas | Frecuencia media de intervenciones por caída de capacidad efectiva bajo el umbral UCBR. |

---

## Análisis Técnico

### Clasificación de Variables

| Tipo Variable | Variable | Descripción |
| :--- | :--- | :--- |
| **DATOS** | **PE** | Producción diaria de energía alterna (kWh) en verano/invierno. |
| | **CE** | Consumo de Energía diario (kWh). |
| | **DTR** | Demora del técnico de baterías en días. |
| **CONTROL** | **CPS** | Cantidad de paneles solares. |
| | **CB** | Capacidad de la batería (kWs). |
| | **PMA** | Punto de modo de ahorro (%). |
| | **UCBR** | Umbral de Capacidad de Batería para Revisión (kWs). |
| **ESTADO** | **E** | Cantidad de Energía en Batería (%). |
| **RESULTADO** | **PRE** | Porcentaje de energía de Red Eléctrica usada mensualmente. |
| | **PSMEE** | Promedio de uso mensual de energía eléctrica renovable generada. |
| | **PMMA** | Promedio mensual de veces que se usó el modo ahorro. |
| | **NPEB** | Nivel promedio de energía en la batería. |
| | **PRT** | Promedio de revisiones técnicas por mes. |
| | **PERG** | Promedio de Energía Renovable Generada. |

### Clasificación de Eventos

| Tipo Evento | Evento |
| :--- | :--- |
| **PROPIO** | Generación energía |
| | Uso de energía convencional |
| | Uso de energía en modo ahorro |
| **Comprometidos ΔT anteriores** | Llegada del técnico de baterías |
| **Comprometidos ΔT futuro** | Llamada al técnico de baterías |

### TEF (Tabla de Eventos Futuros)

| Variable | Descripción |
| :--- | :--- |
| **FRT** | Fecha de Revisión Técnica |
