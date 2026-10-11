import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import json
import numpy as np
import pandas as pd
import rasterio
from rasterio.transform import from_bounds

from src.config import (
    ANIOS, CLASES_PRITHVI, CLASES_DYNAMIC_WORLD, OUTPUTS,
    QUINDIO_BOUNDS, CRS_WEB, CRS_CALCULO,
)


def exportar_csv(datos, nombre_archivo, subdir=""):
    ruta_dir = OUTPUTS / subdir if subdir else OUTPUTS
    ruta_dir.mkdir(parents=True, exist_ok=True)
    ruta = ruta_dir / nombre_archivo
    if isinstance(datos, pd.DataFrame):
        datos.to_csv(ruta, index=False)
    else:
        pd.DataFrame(datos).to_csv(ruta, index=False)
    print(f"CSV exportado: {ruta}")
    return ruta


def exportar_geojson(datos, nombre_archivo, subdir=""):
    ruta_dir = OUTPUTS / subdir if subdir else OUTPUTS
    ruta_dir.mkdir(parents=True, exist_ok=True)
    ruta = ruta_dir / nombre_archivo
    if hasattr(dados, "to_file"):
        datos.to_file(ruta, driver="GeoJSON")
    print(f"GeoJSON exportado: {ruta}")
    return ruta


def exportar_geotiff(array_2d, nombre_archivo, subdir="", crs=CRS_CALCULO):
    ruta_dir = OUTPUTS / subdir if subdir else OUTPUTS
    ruta_dir.mkdir(parents=True, exist_ok=True)
    ruta = ruta_dir / nombre_archivo
    lon_min, lat_min, lon_max, lat_max = QUINDIO_BOUNDS
    transform = from_bounds(lon_min, lat_min, lon_max, lat_max, array_2d.shape[1], array_2d.shape[0])
    with rasterio.open(
        ruta, "w",
        driver="GTiff",
        height=array_2d.shape[0],
        width=array_2d.shape[1],
        count=1,
        dtype=str(array_2d.dtype),
        crs=crs,
        transform=transform,
    ) as dst:
        dst.write(array_2d, 1)
    print(f"GeoTIFF exportado: {ruta}")
    return ruta


def exportar_json(datos, nombre_archivo, subdir=""):
    ruta_dir = OUTPUTS / subdir if subdir else OUTPUTS
    ruta_dir.mkdir(parents=True, exist_ok=True)
    ruta = ruta_dir / nombre_archivo
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2, default=str)
    print(f"JSON exportado: {ruta}")
    return ruta


def exportar_serie_temporal(serie_temporal, subdir="series_temporales"):
    filas = []
    for anio in sorted(serie_temporal.keys()):
        datos = serie_temporal[anio]
        if datos is None:
            continue
        fila = {"anio": anio}
        if "probabilidades" in datos:
            for clase, valor in datos["probabilidades"].items():
                fila[clase] = valor
        filas.append(fila)
    df = pd.DataFrame(filas)
    return exportar_csv(df, "serie_cobertura_quindio.csv", subdir)


def exportar_matriz_transicion(matriz_df, nombre="matriz_transicion.csv", subdir="metricas"):
    return exportar_csv(matriz_df, nombre, subdir)


def exportar_metricas(metricas, subdir="metricas"):
    return exportar_json(metricas, "metricas_validacion.json", subdir)


def exportar_mapa_html(mapa, nombre_archivo="mapa_cobertura.html"):
    ruta = OUTPUTS / nombre_archivo
    if hasattr(mapa, "to_html"):
        mapa.to_html(filename=str(ruta))
    elif hasattr(mapa, "save"):
        mapa.save(str(ruta))
    print(f"Mapa HTML exportado: {ruta}")
    return ruta


def main():
    print("=" * 60)
    print("EXPORTACION DE RESULTADOS - QUINDIO")
    print("=" * 60)
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    print(f"Anios: {ANIOS[0]}-{ANIOS[-1]}")
    print(f"Clases: {len(CLASES_PRITHVI)}")
    print(f"CRS: {CRS_CALCULO}")
    print("Modulo de exportacion listo.")


if __name__ == "__main__":
    main()
