import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np

from src.config import (
    ANIOS, INDICES_S2, CLASES_DYNAMIC_WORLD, TILE_SIZE,
    DATA_PROCESSED, CRS_CALCULO,
)


def calcular_indices_s2(imagen):
    ndvi = imagen.normalizedDifference(["B8", "B4"]).rename("NDVI")
    ndbi = imagen.normalizedDifference(["B11", "B8"]).rename("NDBI")
    ndwi = imagen.normalizedDifference(["B3", "B8"]).rename("NDWI")
    evi = (
        imagen.expression(
            "2.5 * ((NIR - RED) / (NIR + 6 * RED - 7.5 * BLUE + 1))",
            {
                "NIR": imagen.select("B8"),
                "RED": imagen.select("B4"),
                "BLUE": imagen.select("B2"),
            },
        )
        .rename("EVI")
    )
    return imagen.addBands([ndvi, ndbi, ndwi, evi])


def obtener_bandas_clase_dw(imagen_dw):
    bandas = [f"label_{i}" for i in range(len(CLASES_DYNAMIC_WORLD))]
    nombres_disponibles = imagen_dw.bandNames().getInfo()
    clases_validas = []
    bandas_validas = []
    for i, (clase, banda) in enumerate(zip(CLASES_DYNAMIC_WORLD, bandas)):
        if banda in nombres_disponibles:
            clases_validas.append(clase)
            bandas_validas.append(banda)
    return bandas_validas, clases_validas


def clasificar_cobertura_dw(imagen_dw):
    bandas, clases = obtener_bandas_clase_dw(imagen_dw)
    if not bandas:
        return None, []
    imagen_clasificada = imagen_dw.select(bandas).argmax().rename("clase_dw")
    return imagen_clasificada, clases


def obtener_probabilidades_dw(imagen_dw):
    bandas, clases = obtener_bandas_clase_dw(imagen_dw)
    probabilidades = {}
    for clase, banda in zip(clases, bandas):
        probabilidades[clase] = imagen_dw.select(banda)
    return probabilidades


def generar_tiles(tamano=TILE_SIZE):
    tiles = []
    half = tamano // 2
    for i in range(-half, half):
        for j in range(-half, half):
            tiles.append((i * tamano, j * tamano, tamano, tamano))
    return tiles


def normalizar_imagen_s2(imagen_np):
    imagen_np = np.clip(imagen_np, 0, 10000)
    imagen_np = imagen_np / 10000.0
    return np.clip(imagen_np, 0, 1)


def preparar_array_prithvi(imagen_s2, bandas):
    arrays = []
    for banda in bandas:
        arr = np.array(imagen_s2.select(banda).getInfo() if hasattr(imagen_s2, 'getInfo') else imagen_s2[banda])
        arr = np.nan_to_num(arr, nan=0.0, posinf=0.0, neginf=0.0)
        arrays.append(arr)
    return np.stack(arrays, axis=-1)


def procesar_serie_preprocesamiento(serie_temporal):
    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    serie_procesada = {}
    for anio, datos in serie_temporal.items():
        if datos is None:
            continue
        s2_con_indices = calcular_indices_s2(datos["s2"])
        dw_clases, clases = clasificar_cobertura_dw(datos["dw"])
        dw_probs = obtener_probabilidades_dw(datos["dw"])
        serie_procesada[anio] = {
            "s2_indice": s2_con_indices,
            "dw_clasificacion": dw_clases,
            "dw_probabilidades": dw_probs,
            "clases_dw": clases,
        }
    return serie_procesada


def main():
    print("=" * 60)
    print("PREPROCESAMIENTO - QUINDIO")
    print("=" * 60)
    print(f"Anios: {ANIOS[0]}-{ANIOS[-1]}")
    print(f"Indices: {INDICES_S2}")
    print(f"Tamano de tile: {TILE_SIZE}")
    print(f"CRS: {CRS_CALCULO}")
    from src.config import ANIOS as _ANIOS
    for anio in _ANIOS:
        print(f"  {anio}: listo para procesar")
    return True


if __name__ == "__main__":
    main()
