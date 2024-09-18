import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from utils import corregir_coordenadas, listar_hojas, seleccionar_hoja
import argparse

def obtener_columnas_requeridas(df):
    """
    Verifica si el DataFrame tiene las columnas requeridas.
    Si no las tiene, muestra una lista de columnas para que el usuario elija.
    """
    columnas_requeridas = ['IDEvento', 'LATITUD', 'LONGITUD']
    
    for col in columnas_requeridas:
        if col not in df.columns:
            print("Columnas disponibles:")
            for idx, column in enumerate(df.columns):
                print(f"{idx + 1}. {column}")

            print(f"No se encontró la columna '{col}'.")
            seleccion = int(input(f"Selecciona el número de la columna que deseas usar para '{col}': ")) - 1
            columnas_requeridas[columnas_requeridas.index(col)] = df.columns[seleccion]

    return columnas_requeridas

def main(entrada_file, salida_file):
    # Listar las hojas disponibles
    hojas = listar_hojas(entrada_file)
    
    # Permitir al usuario seleccionar la hoja a procesar
    hoja_seleccionada = seleccionar_hoja(hojas)

    # Cargar los datos y validarlos
    accidentes_data = pd.read_excel(entrada_file, sheet_name=hoja_seleccionada, engine='openpyxl')
    
    # Verificar las columnas requeridas
    columnas_requeridas = obtener_columnas_requeridas(accidentes_data)

    # Renombrar las columnas para garantizar que el resto del proceso funcione correctamente
    accidentes_data = accidentes_data.rename(columns={
        columnas_requeridas[0]: 'IDEvento',
        columnas_requeridas[1]: 'LATITUD',
        columnas_requeridas[2]: 'LONGITUD'
    })

    # Validar y corregir las coordenadas
    accidentes_data = corregir_coordenadas(accidentes_data)

    # Polígonos de los tramos carreteros
    tramos_gdf = gpd.read_file('./buffersQRO/map.shp')

    # Convertir las columnas de latitud y longitud en geometría Point y crear un GeoDataFrame
    accidentes_data['geometry'] = accidentes_data.apply(lambda row: Point(row['LONGITUD'], row['LATITUD']), axis=1)
    accidentes_gdf = gpd.GeoDataFrame(accidentes_data, geometry='geometry')

    # Asegurarse de que ambos GeoDataFrames tengan el mismo sistema de coordenadas (CRS)
    accidentes_gdf.set_crs(tramos_gdf.crs, inplace=True)

    # Realizar una unión espacial para asociar cada accidente con su tramo carretero correspondiente
    accidentes_tramos_gdf = gpd.sjoin(
        accidentes_gdf, tramos_gdf[['geometry', 'SECCION']], 
        how='left', 
        predicate='within'
    )

    # Seleccionar solo las columnas relevantes
    accidentes_tramos_data = accidentes_tramos_gdf[[
        'IDEvento', 
        'LATITUD', 
        'LONGITUD', 
        'SECCION'
    ]]

    # Guardar los resultados en un archivo Excel
    accidentes_tramos_data.to_excel(salida_file, index=False)
    print(f"Los resultados se han guardado en {salida_file} \n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Procesa datos de accidentes y tramos carreteros, corrige coordenadas, remapea nombres de tramos y agrega IDs de tramos C5i.',
        epilog='Ejemplo de uso: python main.py accidentes.xlsx resultados.xlsx'
    )
    parser.add_argument(
        'entrada_file', 
        type=str, 
        help='Nombre del archivo de entrada con los datos de accidentes en formato Excel.'
    )
    parser.add_argument(
        'salida_file', 
        type=str, 
        help='Nombre del archivo de salida para guardar los resultados en formato Excel.'
    )

    args = parser.parse_args()
    main(args.entrada_file, args.salida_file)
