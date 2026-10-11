import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_RAW = BASE_DIR / "data" / "raw"
DATA_PROCESSED = BASE_DIR / "data" / "processed"
OUTPUTS = BASE_DIR / "outputs"
WEB_DIR = BASE_DIR / "web"

EE_PROJECT = os.environ.get("EE_PROJECT", "")

CRS_CALCULO = "EPSG:9377"
CRS_WEB = "EPSG:4326"

QUINDIO_BOUNDS = [-75.75, 4.15, -75.35, 4.65]

ANIOS = list(range(2018, 2026))

MUNICIPIOS_QUINDIO = [
    "Armenia", "Buenavista", "Calarca", "Circasia", "Cordoba",
    "Filandia", "Genova", "La Tebaida", "Montenegro", "Pijao",
    "Quimbaya", "Salento",
]

CLASES_DYNAMIC_WORLD = [
    "water", "trees", "grass", "flooded_vegetation", "crops",
    "shrub_and_scrub", "built", "bare", "snow_and_ice",
]

CLASES_PRITHVI = [
    "water", "trees", "grass", "crops", "shrubland",
    "built", "bare", "snow",
]

UMBRAL_CAMBIO = 0.15

TILE_SIZE = 256
BATCH_SIZE = 8
NUM_WORKERS = 4
NUBES_MAX_PORCENTAJE = 20

INDICES_S2 = ["NDVI", "NDBI", "NDWI", "EVI"]


def rectangulo_zona():
    return QUINDIO_BOUNDS


def validar_configuracion():
    avisos = []
    if not EE_PROJECT:
        avisos.append("Variable de entorno EE_PROJECT no definida.")
    if QUINDIO_BOUNDS[0] >= QUINDIO_BOUNDS[2] or QUINDIO_BOUNDS[1] >= QUINDIO_BOUNDS[3]:
        avisos.append("Rectangulo de zona no valido.")
    if len(ANIOS) < 2:
        avisos.append("Se necesitan al menos dos anos.")
    return avisos


if __name__ == "__main__":
    print("=== Configuracion del proyecto - Quindio ===")
    print(f"Raiz: {BASE_DIR}")
    print(f"Proyecto EE: {EE_PROJECT or '(no definido)'}")
    print(f"Zona: {rectangulo_zona()}")
    print(f"Anios: {ANIOS[0]}-{ANIOS[-1]}")
    print(f"Municipios: {len(MUNICIPIOS_QUINDIO)}")
    avisos = validar_configuracion()
    for a in avisos:
        print(f"  - {a}")
