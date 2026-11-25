from datetime import datetime, timezone
from unittest import mock

from src import blob


def test_nombre_historico_incluye_fecha_y_hora():
    ahora = datetime(2026, 11, 24, 12, 0, 5, tzinfo=timezone.utc)
    assert blob.nombre_historico("resultado_extraccion.json", ahora) == (
        "2026/11/24/resultado_extraccion_20261124T120005Z.json"
    )


def test_subir_historico_sube_al_contenedor(tmp_path):
    archivo = tmp_path / "resultado_extraccion.json"
    archivo.write_text("{}", encoding="utf-8")
    cliente = mock.MagicMock()
    ahora = datetime(2026, 11, 24, 12, 0, 5, tzinfo=timezone.utc)

    nombre = blob.subir_historico(cliente, str(archivo), "extracciones", ahora)

    cliente.get_blob_client.assert_called_once_with(container="extracciones", blob=nombre)
    cliente.get_blob_client.return_value.upload_blob.assert_called_once()
