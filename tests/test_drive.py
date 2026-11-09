from unittest import mock

from src import drive


def _servicio_falso(archivos_existentes):
    servicio = mock.MagicMock()
    files = servicio.files.return_value
    files.list.return_value.execute.return_value = {"files": archivos_existentes}
    files.create.return_value.execute.return_value = {"id": "nuevo-id"}
    return servicio, files


def test_reemplazar_borra_anteriores_y_sube_nuevo(tmp_path):
    archivo = tmp_path / "resultado_extraccion.json"
    archivo.write_text("{}", encoding="utf-8")
    servicio, files = _servicio_falso(
        [{"id": "viejo-1", "name": "resultado_extraccion.json"}, {"id": "viejo-2", "name": "resultado_extraccion.json"}]
    )

    with mock.patch("googleapiclient.http.MediaFileUpload") as media:
        nuevo_id = drive.reemplazar_archivo(servicio, str(archivo), "carpeta-123")

    assert nuevo_id == "nuevo-id"
    assert [c.kwargs["fileId"] for c in files.delete.call_args_list] == ["viejo-1", "viejo-2"]
    query = files.list.call_args.kwargs["q"]
    assert "name = 'resultado_extraccion.json'" in query
    assert "'carpeta-123' in parents" in query
    body = files.create.call_args.kwargs["body"]
    assert body == {"name": "resultado_extraccion.json", "parents": ["carpeta-123"]}
    media.assert_called_once()


def test_reemplazar_sin_archivo_previo_solo_sube(tmp_path):
    archivo = tmp_path / "resultado_extraccion.json"
    archivo.write_text("{}", encoding="utf-8")
    servicio, files = _servicio_falso([])

    with mock.patch("googleapiclient.http.MediaFileUpload"):
        drive.reemplazar_archivo(servicio, str(archivo), "carpeta-123")

    files.delete.assert_not_called()
    files.create.assert_called_once()
