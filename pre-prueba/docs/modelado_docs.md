# Análisis de Columnas y Diseño del Modelo Estrella

A continuación, analizamos cada una de las columnas presentes en el archivo `Amazon Sale Report.csv` para decidir su utilidad en nuestro Data Warehouse (Modelo Estrella).

## 1. Columnas que DESCARTAMOS ❌
Estas columnas no aportan valor analítico o están redundantes/con errores graves:

*   `index`: Es solo el número de fila original del CSV. No sirve de nada en la base de datos (PostgreSQL generará sus propios IDs autoincrementales).
*   `currency`: Si todas las ventas (o casi todas) están en una sola moneda (ej. INR), es un dato redundante que solo ocupa espacio. Acordamos descartarla.
*   `Unnamed: 22`: Columna basura generada por comas sobrantes al final del CSV. Tiene 38% de valores nulos y tipos de datos mezclados. Fuera.
*   `fulfilled-by`: Tiene casi 70% de nulos. Nos aporta más consistencia la columna `Fulfilment` (que no tiene nulos).
*   `promotion-ids`: Tiene 38% de nulos y suelen ser cadenas de texto larguísimas y sucias ("Amazon PLCC Free-Financing..."). Es mejor descartarla para simplificar el modelo base, salvo que el negocio lo pida.

---

## 2. Columnas para la Tabla de Hechos (`fact_ventas`) 🎯
Aquí guardaremos las métricas transaccionales (números que vamos a sumar/promediar) y las llaves Foráneas que conectan con el resto de la estrella:

*   `Order ID`: Es vital. Es el identificador "natural" de la transacción, aunque recuerda que puede repetirse si un cliente compró 2 productos distintos en el mismo pedido.
*   `Qty`: (Numérico) Métrica clave. Cantidad de productos vendidos.
*   `Amount`: (Numérico) Métrica clave. Monto total pagado.
*   *(Llaves Foráneas)*: Aquí agregaremos columnas autogeneradas como `id_tiempo`, `id_producto`, `id_envio`, `id_cliente` que apuntan a las Dimensiones.

---

## 3. Columnas para las Dimensiones 🌟

### 📦 `dim_producto`
Describe QUÉ se vendió. Un mismo producto se venderá miles de veces, pero en esta tabla solo existirá una vez.
*   `SKU`: (Stock Keeping Unit). Será nuestra llave natural, el código de barras del almacén.
*   `Style`: El código de estilo o diseño del producto.
*   `Category`: Categoría general (ej. Top, Set, Kurta).
*   `Size`: Talla (ej. S, M, L, XL).
*   `ASIN`: El código estándar de identificación de Amazon. Es útil mantenerlo para cruzar con el inventario virtual.

### 🚚 `dim_envio` (o `dim_logistica`)
Describe CÓMO y DÓNDE se entregó el pedido. Podemos agrupar toda la geografía y el estatus del transportista.
*   `Status`: Estado general de la orden (Cancelado, Enviado, Entregado).
*   `Courier Status`: Estado detallado de la empresa transportista.
*   `Fulfilment`: Quién procesa el envío (Amazon o el Vendedor).
*   `Sales Channel`: El canal donde se vendió (Amazon.in, etc.).
*   `ship-service-level`: Nivel del servicio (Expedited, Standard).
*   `ship-city`: Ciudad de destino.
*   `ship-state`: Estado / Departamento de destino.
*   `ship-postal-code`: Código postal (Tratado como texto).
*   `ship-country`: País de destino.

### 👤 `dim_cliente`
Debido a la privacidad, Amazon no da el nombre del comprador masivo, pero sí nos da un detalle del tipo de cliente.
*   `B2B`: Es un Booleano. Nos indica si la venta fue a una empresa (Business to Business) o a un consumidor final cotidiano.

### 📅 `dim_tiempo`
No tomaremos "columnas" del CSV, sino que usaremos la columna `Date` original, la parsearemos en formato Fecha, y generaremos un registro en esta tabla con:
*   `fecha_completa`: El día exacto (ej: 2022-04-30).
*   `mes`: Ej: 4
*   `año`: Ej: 2022
*   `trimestre`: Ej: 2 (Ideal para KPIs).
*   `semana_del_año`: Útil para gráficos de tendencias continuas.
