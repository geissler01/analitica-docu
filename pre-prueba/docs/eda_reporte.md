# Reporte de Calidad de Datos (EDA)

## Resumen de Problemas Encontrados

1. **Problema 1: Valores ilógicos (cero) en cantidades**
   - **Columna:** `Qty`
   - **Descripción:** Se encontraron 12,807 registros donde la cantidad vendida (`Qty`) es exactamente 0.
   - **Impacto potencial:** Afectará críticamente el cálculo del `ticket_promedio` (ya que Amount / 0 generaría errores numéricos o nulos) y reduce la integridad de los datos, ya que una transacción de venta con cantidad cero carece de sentido operativo.

2. **Problema 2: Nulos en métrica clave de ingresos**
   - **Columna:** `Amount` (y secundariamente `currency`)
   - **Descripción:** Faltan datos monetarios en aproximadamente el 6.04% de los registros (alrededor de 7,795 transacciones).
   - **Impacto potencial:** Subestimación de las ventas totales y de ingresos por categoría si no se reportan o imputan correctamente. Además, genera inconsistencias si `Qty` es mayor a 0 pero el `Amount` es nulo o 0.

3. **Problema 3: Columnas innecesarias o basura**
   - **Columna:** `Unnamed: 22` y `fulfilled-by`
   - **Descripción:** Existe una columna sin nombre (`Unnamed: 22`) con 38% de valores nulos y tipos mixtos (`object`). Por otra parte, `fulfilled-by` tiene 69% de nulos.
   - **Impacto potencial:** Genera ruido en el diseño de las dimensiones de nuestro Esquema Estrella, incrementa el tiempo de procesamiento y el peso de BD sin aportar valor analítico aparente. 

4. **Problema 4: Order IDs repetidos (Cardinalidad)**
   - **Columna:** `Order ID`
   - **Descripción:** Hay 128,975 registros totales pero solo 120,378 `Order ID` únicos.
   - **Impacto potencial:** No es estrictamente un "error", pero indica que un mismo `Order ID` puede agrupar varios `SKU`. Esto nos alerta para la fase de Carga (Ejercicio 4 y 6), donde debemos manejar el ETL de manera que evite insertar llaves primarias duplicadas si intentamos usar `Order ID` como PK única en una transacción general.

## Tipos de Datos Incorrectos

**¿Qué columnas tienen el tipo de dato incorrecto y por qué es crítico para el análisis?**

*   **`Date`:** Actualmente el importador de CSV lo interpreta como `str` (texto como "04-30-22"). **Impacto crítico:** Es imposible realizar analítica de series temporales (ej. ventas agrupadas por mes, comparaciones año a año, extraer "semana del año") sin convertir estas strings a un objeto `datetime` formal.
*   **`ship-postal-code`:** Actualmente está interpretado como `float64` (decimales). **Impacto crítico:** Los códigos postales son identificadores categóricos, no valores numéricos. Convertirlos a float implica agregar ".0" al final y perder "ceros" a la izquierda en caso de que existan códigos postales que los tengan. Deben ser tratados como cadenas de texto (`str`).
