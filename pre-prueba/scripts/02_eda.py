import pandas as pd
from pathlib import Path

def main():
    # Establecer la ruta del archivo
    path_data = Path(__file__).resolve().parent.parent
    csv_file = path_data / "archive" / "Amazon Sale Report.csv"
    
    print("--- INICIANDO EDA ---")
    df = pd.read_csv(csv_file, low_memory=False)
    
    # TRUCO DE SEGURIDAD: Limpiar espacios en blanco al inicio/final de los nombres de columnas
    # Esto evita errores como "Sales Channel " vs "Sales Channel"
    df.columns = df.columns.str.strip()
    
    print("\n--- 1. SHAPE DEL DATASET ---")
    print(f"Filas: {df.shape[0]}, Columnas: {df.shape[1]}")
    
    print("\n--- 2. TIPOS DE DATOS POR COLUMNA ---")
    # df.dtypes imprime los tipos y df.info() es útil tmb
    print(df.dtypes)
    
    print("\n--- 3. PORCENTAJE DE NULOS POR COLUMNA ---")
    porcentaje_nulos = (df.isnull().sum() / len(df)) * 100
    print(porcentaje_nulos.sort_values(ascending=False))
    
    print("\n--- 4. ESTADÍSTICAS DESCRIPTIVAS DE COLUMNAS CLAVE ---")
    # Asumimos Qty y Amount como numéricas
    print(df[['Qty', 'Amount']].describe())
    
    print("\n--- 5. ANÁLISIS E IDENTIFICACIÓN DE PROBLEMAS ---")
    print(f"Total de registros: {len(df)}")
    print(f"Order IDs únicos: {df['Order ID'].nunique()}")
    
    duplicados = df.duplicated().sum()
    print(f"Filas exactamente duplicadas: {duplicados}")
    
    # Revisando las fechas
    print("\nObservación columna Date:")
    print(df['Date'].head(3))
    
    # Valores extraños en Qty
    print("\nDistribución de Qty:")
    print(df['Qty'].value_counts())

    print("\nDistribución de Sales Channel:")
    print(df["Sales Channel"].value_counts())

if __name__ == '__main__':
    main()
