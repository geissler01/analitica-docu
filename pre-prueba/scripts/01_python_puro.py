import csv
from pathlib import Path
from collections import defaultdict

def main():
    # 1. Rutas de los archivos usando pathlib
    path_data = Path(__file__).resolve().parent.parent
    csv_file = path_data / "archive" / "Amazon Sale Report.csv"
    output_file = path_data / "outputs" / "ordenes_filtradas.csv"
    
    print("--- INICIANDO LECTURA CON PYTHON PURO ---")
    
    # 2. Leer el CSV usando solo el módulo csv (sin Pandas)
    datos = []
    try:
        with open(csv_file, mode='r', encoding='utf-8') as f:
            lector = csv.DictReader(f)
            for fila in lector:
                datos.append(fila)
        print(f"Total registros cargados en memoria: {len(datos)}")
    except Exception as e:
        print(f"Error al leer el archivo: {e}")
        return

    # 3. Calcula el total de ventas (Amount) usando comprensión de listas
    fallos = 0
    
    def parsear_monto(valor):
        """Función auxiliar para intentar convertir a float y manejar las excepciones"""
        nonlocal fallos # permite modificar la variable de afuera en lugar de crear una nueva aqui
        try:
            # Si el valor está vacío o nulo, reportarlo como fallo de formato 
            # (Aunque estrictamente un string vacío levanta error en float() de todas formas)
            return float(valor)
        except (ValueError, TypeError):
            # Incrementamos el contador si levanta excepción (es no-numérico o está en blanco)
            fallos += 1
            return 0.0

    # Comprensión de lista aplicando la extracción segura
    montos = [parsear_monto(fila.get('Amount')) for fila in datos] # recorre cada fila y aplica la funcion parsear_monto, extrae el valor de la columna 'Amount' y lo convierte a float
    total_ventas = sum(montos) # suma todos los valores de la lista montos
    
    print(f"\n--- CÁLCULO DE VENTAS TOTALES ---")
    print(f"Total de ventas (Amount): ${total_ventas:,.2f}")
    print(f"Registros que fallaron al parsear por no ser numéricos (incluye nulos): {fallos}")
    
    # 4. Filtrar los 5 SKUs con mayor cantidad vendida (Qty)
    # Evitamos loops lentos anidados utilizando un diccionario para sumar eficientemente
    sku_qty = defaultdict(int)
    for fila in datos:
        try:
            qty = int(fila.get('Qty', 0))
        except ValueError:
            qty = 0
        sku_qty[fila.get('SKU')] += qty
        
    # Ordenar el diccionario por valores (cantidades) y extraer los top 5 sin un framework
    top_5_skus_ordenados = sorted(sku_qty.items(), key=lambda x: x[1], reverse=True)[:5]
    print("\n Top 5 SKUs ordenados:")
    print(top_5_skus_ordenados)
    
    # Creamos un Set con los nombres de los SKU para una búsqueda súper rápida en tiempo O(1)
    skus_top = {sku for sku, qty in top_5_skus_ordenados}
    print("\n Set (conjunto) con los nombres de los SKU:")
    print(skus_top)
    
    print(f"\n--- TOP 5 PRODUCTOS MÁS VENDIDOS ---")
    for sku, qty in top_5_skus_ordenados:
        print(f"SKU: {sku} | Vendidos: {qty}")
        
    # 5. Escribir el nuevo archivo limitando columnas
    print(f"\n--- EXPORTANDO ARCHIVO FILTRADO ---")
    # Filtramos rápidamente usando list comprehension y la estructura de Set
    registros_filtrados = [fila for fila in datos if fila.get('SKU') in skus_top]
    
    columnas_salida = ['Order ID', 'SKU', 'Amount', 'Qty']
    
    try:
        with open(output_file, mode='w', encoding='utf-8', newline='') as f:
            escritor = csv.DictWriter(f, fieldnames=columnas_salida)
            escritor.writeheader()
            
            for fila in registros_filtrados:
                # Construimos un nuevo diccionario solo con las 4 columnas requeridas
                fila_reducida = {columna: fila.get(columna) for columna in columnas_salida}
                escritor.writerow(fila_reducida)
                
        print(f"¡Exportación exitosa! Se han guardado {len(registros_filtrados)} registros en: {output_file}")
    except Exception as e:
        print(f"Error escribiendo el archivo: {e}")

if __name__ == '__main__':
    main()
