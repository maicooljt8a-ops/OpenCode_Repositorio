import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.config import ANIOS, CLASES_PRITHVI, CLASES_DYNAMIC_WORLD, OUTPUTS


PALETA_CLASES = {
    "water": "#419BDF",
    "trees": "#397D49",
    "grass": "#88B053",
    "crops": "#7A87C6",
    "shrubland": "#E49635",
    "shrub_and_scrub": "#E49635",
    "built": "#C4281B",
    "bare": "#A59B8F",
    "snow_and_ice": "#B39FE1",
    "snow": "#B39FE1",
    "flooded_vegetation": "#5B8C5A",
}


def graficar_serie_temporales(serie_df, ruta_salida):
    fig, ax = plt.subplots(figsize=(12, 6))
    for col in serie_df.columns:
        if col != "anio":
            ax.plot(serie_df["anio"], serie_df[col], marker="o", label=col)
    ax.set_xlabel("Anio")
    ax.set_ylabel("Probabilidad / Fraccion")
    ax.set_title("Evolucion de Cobertura - Quindio")
    ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(ruta_salida, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Grafica guardada: {ruta_salida}")


def graficar_matriz_transicion(matriz_df, ruta_salida):
    fig, ax = plt.subplots(figsize=(10, 8))
    im = ax.imshow(matriz_df.values, cmap="YlOrRd", aspect="auto")
    ax.set_xticks(range(len(matriz_df.columns)))
    ax.set_yticks(range(len(matriz_df.index)))
    ax.set_xticklabels(matriz_df.columns, rotation=45, ha="right")
    ax.set_yticklabels(matriz_df.index)
    ax.set_xlabel("Hacia")
    ax.set_ylabel("Desde")
    ax.set_title("Matriz de Transicion de Coberturas")
    for i in range(len(matriz_df.index)):
        for j in range(len(matriz_df.columns)):
            ax.text(j, i, f"{matriz_df.iloc[i, j]:,}", ha="center", va="center", fontsize=7)
    plt.colorbar(im, ax=ax, label="Pixeles")
    plt.tight_layout()
    plt.savefig(ruta_salida, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Matriz guardada: {ruta_salida}")


def graficar_distribucion_clases(dist_df, ruta_salida):
    fig, ax = plt.subplots(figsize=(12, 6))
    x = np.arange(len(dist_df))
    width = 0.8 / len(dist_df.columns[1:])
    for i, col in enumerate(dist_df.columns[1:]):
        ax.bar(x + i * width, dist_df[col], width, label=col)
    ax.set_xlabel("Clase")
    ax.set_ylabel("Fraccion")
    ax.set_title("Distribucion de Cobertura por Anio")
    ax.set_xticks(x)
    ax.set_xticklabels(dist_df[dist_df.columns[0]], rotation=45, ha="right")
    ax.legend()
    plt.tight_layout()
    plt.savefig(ruta_salida, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Distribucion guardada: {ruta_salida}")


def generar_mapa_cambios(cambios_df, ruta_salida):
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(cambios_df["anio_fin"], cambios_df["porcentaje_cambio"], color="steelblue")
    ax.set_xlabel("Anio")
    ax.set_ylabel("Porcentaje de cambio")
    set_title = "Tasa de Cambio de Cobertura - Quindio"
    ax.set_title(set_title)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(ruta_salida, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Mapa de cambios guardado: {ruta_salida}")


def main():
    print("=" * 60)
    print("VISUALIZACION - QUINDIO")
    print("=" * 60)
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    print(f"Clases: {len(CLASES_PRITHVI)} clases Prithvi, {len(CLASES_DYNAMIC_WORLD)} Dynamic World")
    print("Modulo de visualizacion listo.")


if __name__ == "__main__":
    main()
