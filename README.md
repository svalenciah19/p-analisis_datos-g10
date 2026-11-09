# p-analisis_datos-g10
Repositorio Remoto colaborativo para Evidencia de aprendizaje 2 . Optimizando la productividad en el mundo del software

## Estructura

| Ruta | Descripción |
|------|-------------|
| `p-analisis_datos-g10.ipynb` | Notebook original (Google Colab) |
| `src/extraccion.py` | Extracción con BeautifulSoup, Selenium y Scrapy |
| `src/drive.py` | Borra `resultado_extraccion.json` en Google Drive y sube el nuevo |
| `src/main.py` | Punto de entrada (`python -m src.main [--drive]`) |
| `tests/` | Pruebas automatizadas (pytest, sin conexión a internet) |
| `.github/workflows/ci-cd.yml` | Pipeline CI/CD de GitHub Actions |
| `scripts/obtener_token_drive.py` | Script único para obtener el token de Google Drive |

## Ejecución local

```bash
pip install -r requirements-dev.txt
pytest                      # pruebas
python -m src.main          # genera resultado_extraccion.json (requiere Google Chrome)
```

## CI/CD con GitHub Actions

- **CI (`pruebas`)**: se ejecuta en cada push y pull request a `main`.
- **CD (`extraccion-y-despliegue`)**: si las pruebas pasan (en push a `main` o ejecución manual), extrae los datos,
  **elimina** `resultado_extraccion.json` de la carpeta de Drive y **sube uno nuevo**. El JSON también queda como artefacto del run.
- Ejecución manual: pestaña **Actions → CI/CD - Extraccion de datos → Run workflow**.

### Configuración de Google Drive (una sola vez)

1. En [Google Cloud Console](https://console.cloud.google.com/) crea un proyecto y habilita **Google Drive API**.
2. **Google Auth Platform → Público (pantalla de consentimiento)**: tipo *Externo*, agrega tu correo como usuario de prueba y luego
   pulsa **Publicar app** (en modo *Prueba* el token caduca a los 7 días).
3. **Clientes → Crear cliente → App de escritorio**. Descarga el JSON y guárdalo como `scripts/client_secret.json` (está en `.gitignore`).
4. En tu equipo:
   ```bash
   pip install google-auth-oauthlib
   python scripts/obtener_token_drive.py
   ```
   Inicia sesión con la cuenta dueña del Drive; el script imprime `GDRIVE_CLIENT_ID`, `GDRIVE_CLIENT_SECRET` y `GDRIVE_REFRESH_TOKEN`.
5. Abre la carpeta `MyDrive/p-analisis_datos-g10` en Drive; el ID es la última parte de la URL
   (`https://drive.google.com/drive/folders/1jCOvwHmQdIbrbsYr1WNNl2mjjXn7hlBi`).
6. En GitHub: **Settings → Environments → New environment** llamado `test`, y agrega ahí los secrets
   `GDRIVE_CLIENT_ID`, `GDRIVE_CLIENT_SECRET`, `GDRIVE_REFRESH_TOKEN` y `GDRIVE_FOLDER_ID`.
