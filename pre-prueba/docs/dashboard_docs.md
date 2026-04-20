# Dashboard Ejecutivo: Decisiones de Visualización

## Justificación de los Gráficos Elegidos

1. **KPI Cards (Revenue, Órdenes, Ticket Promedio):** Se eligieron tarjetas para las métricas principales porque ofrecen una lectura inmediata y sin distracciones del estado actual del negocio. Es lo primero que el directivo ve al abrir el reporte.
2. **Gráfico de Áreas (Tendencia Mensual):** Permite visualizar la evolución temporal de las ventas. Se eligió el formato de área en lugar de línea para enfatizar el volumen de ventas acumulado y su estacionalidad.
3. **Gráfico de Barras Horizontales (Categorías):** Es la mejor opción para comparar dimensiones con nombres largos. Facilita la identificación rápida de la categoría líder sin obligar al usuario a inclinar la cabeza.
4. **Slicer de Tiempo:** Se incluyó un filtro interactivo por Mes/Año para permitir al usuario "viajar" por los datos y analizar periodos específicos.

## Buenas Prácticas Aplicadas

1. **Consistencia de Colores:** Se asignó un color único a cada categoría principal. Este color se mantiene constante tanto en el gráfico de barras como en cualquier otro visual donde aparezca la categoría, reduciendo la carga cognitiva del usuario.
2. **Jerarquía Visual:** Aplicamos la regla de lectura en "Z". Las métricas críticas (KPIs) están en la esquina superior izquierda, seguidas por las tendencias temporales y finalmente los detalles granulares de categorías y estados.
3. **Eliminación de Ruido (Data-Ink Ratio):** Se eliminaron líneas de cuadrícula innecesarias, bordes pesados y leyendas redundantes. El objetivo es que cada píxel de color en la pantalla represente información valiosa.
