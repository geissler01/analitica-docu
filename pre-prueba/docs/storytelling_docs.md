# Storytelling con Datos: Informe Estratégico RetailCo Q2 2022

## 1. Contexto del Análisis
Este análisis se centra en la salud financiera y operativa de RetailCo durante el primer semestre de 2022. El objetivo es identificar por qué el ticket promedio está superando las expectativas y cómo podemos sostener el crecimiento ante una evidente desaceleración al cierre de junio.

## 2. Hallazgos Principales (Descriptivo)
*   **Dominio de Categorías (Regla 80/20)**: Hemos hallado una concentración masiva del negocio. Solo dos categorías, Set y kurta, generan el 92% de los $78.5M totales. Específicamente, el producto 'Set' actúa como nuestro "Premium Driver" con un precio promedio de $746, mientras que 'kurta' funciona como nuestro producto de volumen.
*   **Eficiencia en Captura de Valor**: El ticket promedio de $597.72 (+37% sobre el objetivo) demuestra que la estrategia de precios es efectiva en los nichos actuales.
*   **Fugas de Datos**: Durante el proceso ETL descubrimos que un 5% de la data (6,413 registros) presentaba inconsistencias en envíos, lo que indica un área de mejora en la captura de información del cliente.

## 3. Diagnóstico de Causas (¿A qué se debe?)
*   **Ciclo de Festividades**: El pico de ventas en Abril está directamente relacionado con el calendario cultural en India. La caída posterior en Mayo y Junio es una corrección estacional clásica tras el periodo de compras intensas.
*   **Geografía del Revenue**: La concentración en estados como Maharashtra y Karnataka responde a que son núcleos económicos (Hubs Tecnológicos) con mayor poder adquisitivo, lo que explica por qué el ticket promedio real es mucho más alto que el conservador objetivo de $435.

## 4. Recomendaciones Estratégicas
*   **Acción Inmediata (Marketing)**: Lanzar una campaña de "Flash Sales" en la categoría 'Set' durante el mes de Julio para mitigar la tendencia a la baja observada post-abril.
*   **Acción Operativa (Inventario)**: Reasignar el 70% del presupuesto de compras exclusivamente a las Top 2 categorías, eliminando la sobreacumulación de stock en categorías de bajo movimiento como 'Dupatta' o 'Bottom'.
*   **Gobernanza de Datos**: Modificar la validación de la App de ventas para asegurar que los campos de ciudad y estado sean obligatorios, eliminando así la incertidumbre en los informes de logística.

---

**¿Qué tipo de pregunta de negocio estás respondiendo?**
- Respondemos preguntas Descriptivas (¿Qué vendimos?), Diagnósticas (¿Por qué el éxito en Tier-1 y el pico de Abril?) y Prescriptivas (¿Qué acciones de marketing y stock debemos tomar ahora?).

**¿Cómo guiaste al lector hacia la conclusión?**
- Usamos la técnica de "Pirámide Invertida": Primero sorprendemos con el éxito de los $78M y el ticket promedio, luego bajamos al detalle de qué categorías lo lograron, alertamos sobre la caída estacional y cerramos con un plan de acción concreto para el próximo trimestre.
