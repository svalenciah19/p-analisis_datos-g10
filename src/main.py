"""Punto de entrada: extrae los datos, genera resultado_extraccion.json y opcionalmente lo publica en Drive.

Uso:
    python -m src.main              # solo extrae y guarda el JSON local
    python -m src.main --drive      # además reemplaza el archivo en Google Drive
    python -m src.main --blob       # además guarda una copia histórica en Azure Blob Storage
"""

import argparse
import os

from src import extraccion

NOMBRE_ARCHIVO = "resultado_extraccion.json"


def ejecutar(ruta_salida: str = NOMBRE_ARCHIVO, subir_a_drive: bool = False, subir_a_blob: bool = False) -> dict:
    html = extraccion.descargar_html()
    datos_bs4 = extraccion.extraer_con_bs4(html)
    print("Extracción exitosa con BeautifulSoup:", datos_bs4)

    datos_selenium = extraccion.extraer_con_selenium()
    print("Extracción exitosa con Selenium:", datos_selenium)

    datos_scrapy = extraccion.extraer_con_scrapy(html)
    print("Extracción exitosa con Scrapy:", datos_scrapy)

    resultado = extraccion.construir_resultado(datos_bs4, datos_selenium, datos_scrapy)
    extraccion.guardar_json(resultado, ruta_salida)
    print(f"Archivo JSON generado: {ruta_salida}")

    if subir_a_drive:
        from src import drive

        servicio = drive.crear_servicio_desde_entorno()
        drive.reemplazar_archivo(servicio, ruta_salida, os.environ["GDRIVE_FOLDER_ID"], NOMBRE_ARCHIVO)

    if subir_a_blob:
        from src import blob

        cliente = blob.crear_cliente_desde_entorno()
        blob.subir_historico(cliente, ruta_salida, os.environ.get("AZURE_STORAGE_CONTAINER", blob.CONTENEDOR_POR_DEFECTO))

    return resultado


def main():
    parser = argparse.ArgumentParser(description="Extracción de datos de books.toscrape.com")
    parser.add_argument("--salida", default=NOMBRE_ARCHIVO, help="Ruta del JSON de salida")
    parser.add_argument("--drive", action="store_true", help="Reemplazar el archivo en Google Drive")
    parser.add_argument("--blob", action="store_true", help="Guardar copia histórica en Azure Blob Storage")
    args = parser.parse_args()
    ejecutar(args.salida, args.drive, args.blob)


if __name__ == "__main__":
    main()
