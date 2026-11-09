import json
import os
from unittest import mock

import pytest

from src import extraccion, main

FIXTURE = os.path.join(os.path.dirname(__file__), "fixtures", "libro.html")


@pytest.fixture
def html():
    with open(FIXTURE, encoding="utf-8") as f:
        return f.read()


def test_extraer_con_bs4(html):
    datos = extraccion.extraer_con_bs4(html)
    assert datos["metodo"] == "BeautifulSoup"
    assert datos["titulo"] == "A Light in the Attic"
    assert datos["precio"] == "£51.77"
    assert datos["disponibilidad"].startswith("In stock")


def test_extraer_con_scrapy(html):
    datos = extraccion.extraer_con_scrapy(html)
    assert datos["metodo"] == "Scrapy (Selector Engine)"
    assert datos["titulo"] == "A Light in the Attic"
    assert datos["precio"] == "£51.77"
    assert datos["upc"] == "a897fe39b1053632"


def test_construir_resultado_y_guardar_json(html, tmp_path):
    bs4 = extraccion.extraer_con_bs4(html)
    scrapy = extraccion.extraer_con_scrapy(html)
    selenium = {"metodo": "Selenium", "titulo": bs4["titulo"], "precio": bs4["precio"]}

    resultado = extraccion.construir_resultado(bs4, selenium, scrapy)
    ruta = extraccion.guardar_json(resultado, str(tmp_path / "resultado_extraccion.json"))

    with open(ruta, encoding="utf-8") as f:
        guardado = json.load(f)
    assert guardado == resultado
    assert guardado["tecnologias_probadas"] == ["BeautifulSoup", "Selenium", "Scrapy"]
    assert [d["metodo"] for d in guardado["detalles_extraccion"]] == [
        "BeautifulSoup",
        "Selenium",
        "Scrapy (Selector Engine)",
    ]


def test_descargar_html_decodifica_utf8():
    respuesta = mock.Mock(content="£51.77".encode("utf-8"), encoding="ISO-8859-1")
    type(respuesta).text = mock.PropertyMock(side_effect=lambda: respuesta.content.decode(respuesta.encoding))
    with mock.patch.object(extraccion.requests, "get", return_value=respuesta):
        assert extraccion.descargar_html() == "£51.77"


def test_ejecutar_sin_drive(html, tmp_path):
    selenium = {"metodo": "Selenium", "titulo": "A Light in the Attic", "precio": "£51.77"}
    ruta = tmp_path / "salida.json"
    with mock.patch.object(extraccion, "descargar_html", return_value=html), mock.patch.object(
        extraccion, "extraer_con_selenium", return_value=selenium
    ):
        resultado = main.ejecutar(str(ruta), subir_a_drive=False)

    assert ruta.exists()
    assert resultado["articulo_analizado"] == "A Light in the Attic"
