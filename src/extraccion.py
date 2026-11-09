"""Extracción de datos con BeautifulSoup, Selenium y Scrapy (misma lógica del notebook)."""

import json
import time

import requests
from bs4 import BeautifulSoup
from scrapy.selector import Selector

URL = "http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"
HEADERS = {"User-Agent": "Mozilla/5.0"}


def descargar_html(url: str = URL, timeout: int = 30) -> str:
    response = requests.get(url, headers=HEADERS, timeout=timeout)
    response.raise_for_status()
    # El servidor no declara charset y requests asumiría ISO-8859-1 (el "£" saldría como "Â£")
    response.encoding = "utf-8"
    return response.text


def extraer_con_bs4(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    return {
        "metodo": "BeautifulSoup",
        "titulo": soup.find("h1").text,
        "precio": soup.find("p", class_="price_color").text,
        "disponibilidad": soup.find("p", class_="instock availability").text.strip(),
    }


def extraer_con_scrapy(html: str) -> dict:
    sel = Selector(text=html)
    return {
        "metodo": "Scrapy (Selector Engine)",
        "titulo": sel.css("h1::text").get(),
        "precio": sel.css("p.price_color::text").get(),
        "upc": sel.css("table.table-striped tr:nth-child(1) td::text").get(),
    }


def extraer_con_selenium(url: str = URL) -> dict:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By

    chrome_options = Options()
    for arg in ("--headless=new", "--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"):
        chrome_options.add_argument(arg)

    driver = webdriver.Chrome(options=chrome_options)
    try:
        driver.get(url)
        time.sleep(2)
        return {
            "metodo": "Selenium",
            "titulo": driver.find_element(By.TAG_NAME, "h1").text,
            "precio": driver.find_element(By.CSS_SELECTOR, "p.price_color").text,
        }
    finally:
        driver.quit()


def construir_resultado(datos_bs4: dict, datos_selenium: dict, datos_scrapy: dict) -> dict:
    return {
        "proyecto": "Analisis y Extraccion de Datos",
        "articulo_analizado": datos_bs4["titulo"],
        "precio": datos_bs4["precio"],
        "disponibilidad": datos_bs4["disponibilidad"],
        "tecnologias_probadas": ["BeautifulSoup", "Selenium", "Scrapy"],
        "detalles_extraccion": [datos_bs4, datos_selenium, datos_scrapy],
    }


def guardar_json(datos: dict, ruta: str) -> str:
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=4)
    return ruta
