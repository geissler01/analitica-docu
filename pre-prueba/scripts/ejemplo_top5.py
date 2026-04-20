from collections import defaultdict

def main():
    # 1. Tus 10 datos de prueba (Simulan el archivo de Excel / CSV)
    # Algunos tienen errores a propósito para simular la realidad (ej: Qty vacío '')
    datos = [
        {'Order ID': '001', 'SKU': 'Manzanas', 'Qty': '5'},
        {'Order ID': '002', 'SKU': 'Peras',    'Qty': '2'},
        {'Order ID': '003', 'SKU': 'Manzanas', 'Qty': '10'},
        {'Order ID': '004', 'SKU': 'Uvas',     'Qty': '6'},
        {'Order ID': '005', 'SKU': 'Mangos',   'Qty': '3'},
        {'Order ID': '006', 'SKU': 'Fresas',   'Qty': ''},    # <-- Error simulado (vacío)
        {'Order ID': '007', 'SKU': 'Peras',    'Qty': '8'},
        {'Order ID': '008', 'SKU': 'Manzanas', 'Qty': '5'},
        {'Order ID': '009', 'SKU': 'Uvas',     'Qty': '1'},
        {'Order ID': '010', 'SKU': 'Limon',    'Qty': '1'}
    ]

    print("--- 1. SUMANDO CANTIDADES (El diccionario especial) ---")
    
    # Creamos el diccionario que inicia automáticamente los conteos en 0
    sku_qty = defaultdict(int)
    print(sku_qty)
    
    for fila in datos:
        try:
            # Intentamos convertir la cantidad a número entero
            qty = int(fila.get('Qty', 0))
        except ValueError:
            # Si falla (como en la fila 006 de las Fresas), asumimos que vendió 0
            qty = 0
            
        # Al diccionario le decimos: "Encuentra este SKU y súmale la cantidad vendida"
        sku_qty[fila.get('SKU')] += qty
        print(sku_qty)
        
    # Veamos cómo quedó el diccionario "crudo":
    print("Diccionario sku_qty:", dict(sku_qty))
    print()

    print("--- 2. ORDENANDO Y SACANDO EL TOP 3 (Elegí Top 3 para el ejemplo) ---")
    # sorted() ordenará el diccionario basándose en la cantidad (x[1]) de mayor a menor
    top_3_skus_ordenados = sorted(sku_qty.items(), key=lambda x: x[1], reverse=True)[:3]
    
    for sku, qty in top_3_skus_ordenados:
        print(f"-> Producto: {sku} | Total Vendidos: {qty}")
    print()

    print("--- 3. CREANDO EL SET (El conjunto superrápido) ---")
    # De la lista anterior (que tiene el producto y cantidad), extraemos SOLAMENTE el nombre del producto
    skus_top = {sku for sku, qty in top_3_skus_ordenados}
    print("Nombres puros para búsquedas rápidas:", skus_top)
    print()

    print("--- 4. FILTRANDO LA BASE DE DATOS ORIGINAL ---")
    # Recorremos la lista "datos" original de 10 filas usando comprensión de listas.
    # Si la fruta está entre las Top 3 ganadoras (nuestro Set), la guardamos; de lo contrario, la ignoramos.
    registros_filtrados = [fila for fila in datos if fila.get('SKU') in skus_top]
    
    # Vamos a imprimir el resultado final para ver qué filas sobrevivieron al filtro
    print("Filas que sobrevivieron (Solo Manzanas, Peras y Uvas):")
    for fila in registros_filtrados:
        print(fila)

if __name__ == '__main__':
    main()
