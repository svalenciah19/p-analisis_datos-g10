"""Guarda una copia histórica del resultado en Azure Blob Storage usando identidad administrada."""

import os
from datetime import datetime, timezone

CONTENEDOR_POR_DEFECTO = "extracciones"


def nombre_historico(nombre: str, ahora: datetime | None = None) -> str:
    ahora = ahora or datetime.now(timezone.utc)
    base, ext = os.path.splitext(nombre)
    return f"{ahora:%Y/%m/%d}/{base}_{ahora:%Y%m%dT%H%M%SZ}{ext}"


def crear_cliente_desde_entorno():
    from azure.identity import DefaultAzureCredential
    from azure.storage.blob import BlobServiceClient

    # En Container Apps, AZURE_CLIENT_ID selecciona la identidad administrada asignada por el usuario
    credencial = DefaultAzureCredential(managed_identity_client_id=os.environ.get("AZURE_CLIENT_ID"))
    return BlobServiceClient(account_url=os.environ["AZURE_STORAGE_ACCOUNT_URL"], credential=credencial)


def subir_historico(cliente, ruta_local: str, contenedor: str = CONTENEDOR_POR_DEFECTO, ahora: datetime | None = None) -> str:
    from azure.storage.blob import ContentSettings

    nombre_blob = nombre_historico(os.path.basename(ruta_local), ahora)
    with open(ruta_local, "rb") as datos:
        cliente.get_blob_client(container=contenedor, blob=nombre_blob).upload_blob(
            datos, overwrite=True, content_settings=ContentSettings(content_type="application/json")
        )
    print(f"Copia histórica guardada en Blob Storage: {contenedor}/{nombre_blob}")
    return nombre_blob
