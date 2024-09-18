import pandas as pd

def listar_hojas(archivo):
    """
    Lista todas las hojas disponibles en el archivo Excel.
    """
    hojas = pd.ExcelFile(archivo, engine='openpyxl').sheet_names
    print("Hojas disponibles en el archivo:")

    for idx, hoja in enumerate(hojas):
        print(f"{idx + 1}. {hoja}")
    
    print()
    return hojas

def seleccionar_hoja(hojas):
    """
    Permite al usuario seleccionar una hoja entre las disponibles.
    """
    while True:
        try:
            seleccion = int(input("Selecciona el número de la hoja que deseas procesar: "))
            print()
            if 1 <= seleccion <= len(hojas):
                return hojas[seleccion - 1]
            else:
                print("Por favor, selecciona un número válido.")
        except ValueError:
            print("Entrada no válida. Introduce un número.")

def validar_columnas(df):
    """
    Verifica que el DataFrame de entrada contenga las columnas necesarias.
    """
    columnas_requeridas = {'IDAccidente', 'LATITUD', 'LONGITUD'}
    columnas_actuales = set(df.columns)
    
    if not columnas_requeridas.issubset(columnas_actuales):
        columnas_faltantes = columnas_requeridas - columnas_actuales
        raise ValueError(f"El archivo de entrada debe contener las siguientes columnas: {', '.join(columnas_faltantes)}")

def validar_coordenadas(latitud, longitud, contador_conversiones):
    """
    Valida y corrige las coordenadas de latitud y longitud.
    - La latitud debe estar entre 19 y 22.
    - La longitud debe estar entre -102 y -99, y siempre negativa.
    """
    # Verificar si la longitud es positiva y corregirla
    if longitud > 0:
        longitud = -longitud
        contador_conversiones += 1

    # Verificar si la latitud está fuera del rango esperado
    if not (19 <= latitud <= 22):
        print(f"**************************************************************")
        print(f"* Advertencia: Latitud fuera del rango esperado: {latitud}")
        print(f"**************************************************************")

    # Verificar si la longitud está fuera del rango esperado
    if not (-102 <= longitud <= -99):
        print(f"**************************************************************")
        print(f"* Advertencia: Longitud fuera del rango esperado: {longitud}")
        print(f"**************************************************************")

    return latitud, longitud, contador_conversiones

def corregir_coordenadas(df):
    """
    Aplica la validación y corrección de coordenadas a un DataFrame de accidentes.
    """
    contador_conversiones = 0
    latitudes_longitudes = []

    for _, row in df.iterrows():
        lat, lon, contador_conversiones = validar_coordenadas(row['LATITUD'], row['LONGITUD'], contador_conversiones)
        latitudes_longitudes.append((lat, lon))

    df['LATITUD'], df['LONGITUD'] = zip(*latitudes_longitudes)

    if contador_conversiones > 0:
        print(f"Se realizaron {contador_conversiones} conversiones de longitud positiva a negativa.")

    return df
