import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
import pandas as pd

from src.config import ANIOS, UMBRAL_CAMBIO, CLASES_PRITHVI, CLASES_DYNAMIC_WORLD


def calcular_matriz_transicion(clasificacion_t1, clasificacion_t2, clases):
    n = len(clases)
    matriz = np.zeros((n, n), dtype=np.int64)
    clase_a_idx = {c: i for i, c in enumerate(clases)}
    flat_t1 = clasificacion_t1.flatten()
    flat_t2 = clasificacion_t2.flatten()
    for v1, v2 in zip(flat_t1, flat_t2):
        idx1 = int(v1) if 0 <= int(v1) < n else -1
        idx2 = int(v2) if 0 <= int(v2) < n else -1
        if idx1 >= 0 and idx2 >= 0:
            matriz[idx1, idx2] += 1
    return matriz


def comparar_clasificaciones_por_anios(clasificaciones):
    cambios = []
    anios = sorted(clasificaciones.keys())
    for i in range(1, len(anios)):
        t1 = anios[i - 1]
        t2 = anios[i]
        if clasificaciones[t1] is None or clasificaciones[t2] is None:
            continue
        pred1 = clasificaciones[t1]["prediccion"]
        pred2 = clasificaciones[t2]["prediccion"]
        if pred1.shape != pred2.shape:
            continue
        cambio = pred2 - pred1
        cambio_mask = cambio != 0
        n_cambios = int(np.sum(cambio_mask))
        n_total = cambio.size
        cambios.append({
            "anio_inicio": t1,
            "anio_fin": t2,
            "pixeles_cambiados": n_cambios,
            "pixeles_totales": n_total,
            "porcentaje_cambio": 100 * n_cambios / n_total if n_total > 0 else 0,
        })
    return pd.DataFrame(cambios)


def detectar_cambios_significativos(probabilidades_t1, probabilidades_t2, umbral=UMBRAL_CAMBIO):
    cambios = {}
    for clase in probabilidades_t1:
        if clase not in probabilidades_t2:
            continue
        diff = probabilidades_t2[clase] - probabilidades_t1[clase]
        cambios[clase] = {
            "diferencia_max": float(np.max(np.abs(diff))),
            "diferencia_media": float(np.mean(np.abs(diff))),
            "cambio_significativo": bool(np.any(np.abs(diff) >= umbral)),
        }
    return cambios


def matriz_transicion_dataframe(matriz, clases):
    df = pd.DataFrame(matriz, index=clases, columns=clases)
    df.index.name = "desde"
    df.columns.name = "hacia"
    return df


def calcular_tasas_cambio(matriz, clases):
    tasas = []
    n = len(clases)
    total = matriz.sum()
    for i in range(n):
        for j in range(n):
            if i != j and matriz[i, j] > 0:
                tasas.append({
                    "desde": clases[i],
                    "hacia": clases[j],
                    "pixeles": int(matriz[i, j]),
                    "porcentaje": 100 * matriz[i, j] / total if total > 0 else 0,
                })
    return pd.DataFrame(tasas)


def main():
    print("=" * 60)
    print("DETECCION DE CAMBIOS - QUINDIO")
    print("=" * 60)
    print(f"Anios: {ANIOS[0]}-{ANIOS[-1]}")
    print(f"Umbral de cambio: {UMBRAL_CAMBIO}")
    print(f"Clases: {CLASES_PRITHVI}")
    print("Listo para analizar cuando se disponga de clasificaciones.")


if __name__ == "__main__":
    main()
