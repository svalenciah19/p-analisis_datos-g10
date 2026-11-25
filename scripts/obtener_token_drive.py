"""Ejecutar UNA sola vez en tu computador para obtener el refresh token de Google Drive.

1. Descarga el JSON del cliente OAuth (tipo "App de escritorio") y guárdalo como client_secret.json
   en esta misma carpeta (NO lo subas a GitHub; ya está en .gitignore).
2. pip install google-auth-oauthlib
3. Opciones:
   python scripts/obtener_token_drive.py                       # imprime los valores (para secrets de GitHub)
   python scripts/obtener_token_drive.py --keyvault <nombre>   # los guarda en Azure Key Vault sin mostrarlos
                                         [--folder-id <id>]     # (requiere 'az login')
"""

import argparse
import os
import shutil
import subprocess

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/drive"]
RUTA_CLIENTE = os.path.join(os.path.dirname(__file__), "client_secret.json")


def guardar_en_keyvault(vault: str, nombre: str, valor: str) -> None:
    az = shutil.which("az") or shutil.which("az.cmd")
    if not az:
        raise SystemExit("No se encontró Azure CLI ('az'). Instálala y ejecuta 'az login'.")
    # El valor se pasa por argumento al proceso hijo y nunca se imprime
    subprocess.run(
        [az, "keyvault", "secret", "set", "--vault-name", vault, "--name", nombre, "--value", valor, "--output", "none"],
        check=True,
    )
    print(f"Secreto '{nombre}' guardado en Key Vault '{vault}'.")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--keyvault", help="Nombre del Key Vault donde guardar las credenciales")
    parser.add_argument("--folder-id", help="ID de la carpeta de Google Drive (se guarda como gdrive-folder-id)")
    args = parser.parse_args()

    flow = InstalledAppFlow.from_client_secrets_file(RUTA_CLIENTE, SCOPES)
    creds = flow.run_local_server(port=0, access_type="offline", prompt="consent")
    if not creds.refresh_token:
        raise SystemExit("Google no devolvió refresh token. Revoca el acceso de la app en tu cuenta y vuelve a intentar.")

    if args.keyvault:
        guardar_en_keyvault(args.keyvault, "gdrive-client-id", creds.client_id)
        guardar_en_keyvault(args.keyvault, "gdrive-client-secret", creds.client_secret)
        guardar_en_keyvault(args.keyvault, "gdrive-refresh-token", creds.refresh_token)
        if args.folder_id:
            guardar_en_keyvault(args.keyvault, "gdrive-folder-id", args.folder_id)
        return

    print("\nAgrega estos valores como secrets en GitHub (Settings > Secrets and variables > Actions):\n")
    print(f"GDRIVE_CLIENT_ID      = {creds.client_id}")
    print(f"GDRIVE_CLIENT_SECRET  = {creds.client_secret}")
    print(f"GDRIVE_REFRESH_TOKEN  = {creds.refresh_token}")


if __name__ == "__main__":
    main()
