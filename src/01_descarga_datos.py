import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

try:
    import ee
    import geemap
except ImportError:
    print("ERROR: earthengine-api y geemap no instalados.")
    print("Ejecute: pip install earthengine-api geemap")
    sys.exit(1)

from src.config import (
    EE_PROJECT, QUINDIO_BOUNDS, ANIOS, DATA_RAW,
    NUBES_MAX_PORCENTAJE, validar_configuracion,
)


def inicializar_earth_engine():
    if not EE_PROJECT:
        print("ERROR: Variable de entorno EE_PROJECT no definida.")
        print("Ejemplo PowerShell: $env:EE_PROJECT = 'mi-proyecto-123'")
        sys.exit(1)
    try:
        ee.Initialize(project=EE_PROJECT)
        print(f"Earth Engine inicializado: {EE_PROJECT}")
    except Exception as e:
        print(f"ERROR al inicializar Earth Engine: {e}")
        print("Ejecute: earthengine authenticate")
        sys.exit(1)


def obtener_zona_estudio():
    return ee.Geometry.Rectangle(QUINDIO_BOUNDS)


def obtener_limites_municipales(zona):
    try:
        colombia = ee.FeatureCollection("FAO/GAUL/2015/level2")
        quindio = colombia.filter(ee.Filter.eq("ADM1_NAME", "Quindio"))
        return quindio
    except Exception as e:
        print(f"Advertencia limites municipales: {e}")
        return None


def obtener_sentinel2(zona, anio):
    s2 = (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(zona)
        .filterDate(f"{anio}-01-01", f"{anio}-12-31")
        .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", NUBES_MAX_PORCENTAJE))
    )
    return s2


def obtener_dynamic_world(zona, anio):
    dw = (
        ee.ImageCollection("GOOGLE/DYNAMICWORLD/V1")
        .filterBounds(zona)
        .filterDate(f"{anio}-01-01", f"{anio}-12-31")
    )
    return dw


def obtener_composicion_s2(zona, anio):
    s2 = obtener_sentinel2(zona, anio)
    count = s2.size().getInfo()
    if count == 0:
        print(f"  ADVERTENCIA: Sin imagenes Sentinel-2 para {anio}")
        return None, 0
    median = s2.median().clip(zona)
    return median, count


def obtener_composicion_dw(zona, anio):
    dw = obtener_dynamic_world(zona, anio)
    count = dw.size().getInfo()
    if count == 0:
        print(f"  ADVERTENCIA: Sin datos Dynamic World para {anio}")
        return None, 0
    median = dw.median().clip(zona)
    return median, count


def descargar_serie_temporal(zona):
    DATA_RAW.mkdir(parents=True, exist_ok=True)
    serie = {}
    for anio in ANIOS:
        print(f"\nProcesando {anio}...")
        s2_img, s2_count = obtener_composicion_s2(zona, anio)
        dw_img, dw_count = obtener_composicion_dw(zona, anio)
        print(f"  Sentinel-2: {s2_count} imagenes")
        print(f"  Dynamic World: {dw_count} imagenes")
        if s2_img is not None and dw_img is not None:
            serie[anio] = {"s2": s2_img, "dw": dw_img, "s2_count": s2_count, "dw_count": dw_count}
        else:
            serie[anio] = None
    return serie


def exportar_como_asset(serie, zona):
    for anio, datos in serie.items():
        if datos is None:
            continue
        task = ee.batch.Export.image.toAsset(
            image=datos["s2"],
            description=f"s2_quindio_{anio}",
            assetId=f"users/{EE_PROJECT}/s2_quindio_{anio}",
            region=zona,
            scale=10,
            maxPixels=1e9,
        )
        task.start()
        print(f"  Exportando S2 {anio} como asset...")


def main():
    print("=" * 60)
    print("DESCARGA DE DATOS - QUINDIO, COLOMBIA")
    print("=" * 60)
    avisos = validar_configuracion()
    if avisos:
        for a in avisos:
            print(f"AVISO: {a}")
    inicializar_earth_engine()
    zona = obtener_zona_estudio()
    limites = obtener_limites_municipales(zona)
    if limites:
        n_mun = limites.size().getInfo()
        print(f"Municipios encontrados: {n_mun}")
    serie = descargar_serie_temporal(zona)
    print("\n" + "=" * 60)
    print("RESUMEN DE DESCARGA")
    print("=" * 60)
    for anio, datos in serie.items():
        if datos:
            print(f"  {anio}: OK")
        else:
            print(f"  {anio}: SIN DATOS")
    return serie, zona


if __name__ == "__main__":
    main()
