"""Ejecutar UNA sola vez en tu computador para obtener el refresh token de Google Drive.

1. Descarga el JSON del cliente OAuth (tipo "App de escritorio") y guárdalo como client_secret.json
   en esta misma carpeta (NO lo subas a GitHub; ya está en .gitignore).
2. pip install google-auth-oauthlib
3. python scripts/obtener_token_drive.py
4. Copia los valores impresos a los secrets del repositorio en GitHub.
"""

import os

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/drive"]
RUTA_CLIENTE = os.path.join(os.path.dirname(__file__), "client_secret.json")

flow = InstalledAppFlow.from_client_secrets_file(RUTA_CLIENTE, SCOPES)
creds = flow.run_local_server(port=0, access_type="offline", prompt="consent")

print("\nAgrega estos valores como secrets en GitHub (Settings > Secrets and variables > Actions):\n")
print(f"GDRIVE_CLIENT_ID      = {creds.client_id}")
print(f"GDRIVE_CLIENT_SECRET  = {creds.client_secret}")
print(f"GDRIVE_REFRESH_TOKEN  = {creds.refresh_token}")
