"""Reemplaza un archivo en una carpeta de Google Drive: borra las versiones anteriores y sube la nueva."""

import os

SCOPES = ["https://www.googleapis.com/auth/drive"]


def crear_servicio_desde_entorno():
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build

    creds = Credentials(
        token=None,
        refresh_token=os.environ["GDRIVE_REFRESH_TOKEN"],
        client_id=os.environ["GDRIVE_CLIENT_ID"],
        client_secret=os.environ["GDRIVE_CLIENT_SECRET"],
        token_uri="https://oauth2.googleapis.com/token",
        scopes=SCOPES,
    )
    return build("drive", "v3", credentials=creds, cache_discovery=False)


def buscar_archivos(servicio, nombre: str, carpeta_id: str) -> list:
    nombre_escapado = nombre.replace("\\", "\\\\").replace("'", "\\'")
    query = f"name = '{nombre_escapado}' and '{carpeta_id}' in parents and trashed = false"
    respuesta = servicio.files().list(q=query, fields="files(id, name)", spaces="drive").execute()
    return respuesta.get("files", [])


def reemplazar_archivo(servicio, ruta_local: str, carpeta_id: str, nombre: str | None = None) -> str:
    from googleapiclient.http import MediaFileUpload

    nombre = nombre or os.path.basename(ruta_local)

    for archivo in buscar_archivos(servicio, nombre, carpeta_id):
        servicio.files().delete(fileId=archivo["id"]).execute()
        print(f"Archivo anterior eliminado de Drive: {archivo['name']} ({archivo['id']})")

    media = MediaFileUpload(ruta_local, mimetype="application/json")
    nuevo = (
        servicio.files()
        .create(body={"name": nombre, "parents": [carpeta_id]}, media_body=media, fields="id")
        .execute()
    )
    print(f"Nuevo archivo subido a Drive: {nombre} ({nuevo['id']})")
    return nuevo["id"]
