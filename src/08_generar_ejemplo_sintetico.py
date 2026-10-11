import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import ListedColormap
import numpy as np
import pandas as pd

import importlib.util
_config_path = Path(__file__).resolve().parent / "00_config.py"
_spec = importlib.util.spec_from_file_location("config_00", _config_path)
config_00 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(config_00)
ANIOS = config_00.ANIOS
CLASES_PRITHVI = config_00.CLASES_PRITHVI
QUINDIO_BOUNDS = config_00.QUINDIO_BOUNDS

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "outputs" / "ejemplo_sintetico"

COLORES_CLASES = {
    "water": "#419BDF",
    "trees": "#397D49",
    "grass": "#88B053",
    "crops": "#7A87C6",
    "shrubland": "#E49635",
    "built": "#C4281B",
    "bare": "#A59B8F",
    "snow": "#B39FE1",
}

ETIQUETA_SINTETICO = "DATOS SINTETICOS - NO REPRESENTA COBERTURA REAL"
RESOLUCION = 100


def generar_cobertura_sintetica(anio, rng):
    n = RESOLUCION
    x = np.linspace(0, 1, n)
    y = np.linspace(0, 1, n)
    xx, yy = np.meshgrid(x, y)
    elev = np.sin(3 * xx) * np.cos(2 * yy) + 0.5 * np.sin(5 * xx + anio * 0.3)
    patron = rng.random((n, n))
    imagen = np.zeros((n, n), dtype=np.int32)
    imagen[elev > 0.6] = 1
    imagen[(elev > 0.2) & (elev <= 0.6) & (patron > 0.4)] = 2
    imagen[(elev > -0.2) & (elev <= 0.2) & (patron > 0.5)] = 3
    imagen[(elev > -0.6) & (elev <= -0.2) & (patron > 0.3)] = 4
    imagen[elev <= -0.6] = 5
    imagen[(xx > 0.7) & (yy > 0.6) & (patron > 0.3)] = 5
    imagen[(xx < 0.3) & (yy < 0.3) & (elev > 0.8)] = 0
    ruido = rng.random((n, n))
    imagen[(ruido > 0.97) & (imagen != 5)] = 6
    return imagen


def generar_mapa_cobertura(anio, rng, output_dir):
    imagen = generar_cobertura_sintetica(anio, rng)
    fig, ax = plt.subplots(figsize=(10, 8))
    colores = [COLORES_CLASES[c] for c in CLASES_PRITHVI]
    cmap = ListedColormap(colores)
    im = ax.imshow(imagen, cmap=cmap, vmin=-0.5, vmax=len(CLASES_PRITHVI) - 0.5, extent=QUINDIO_BOUNDS)
    patches = [mpatches.Patch(color=COLORES_CLASES[c], label=c) for c in CLASES_PRITHVI]
    ax.legend(handles=patches, loc="lower left", bbox_to_anchor=(1.01, 0), title="Clases", fontsize=8)
    ax.set_title(f"Cobertura Terrestre - Quindio, Colombia\nAnio {anio}\n{ETIQUETA_SINTETICO}", fontsize=10)
    ax.set_xlabel("Longitud")
    ax.set_ylabel("Latitud")
    ax.annotate("N", xy=(0.95, 0.95), xycoords="axes fraction", fontsize=14, fontweight="bold")
    ax.annotate("^", xy=(0.95, 0.91), xycoords="axes fraction", fontsize=14)
    ruta = output_dir / f"01_mapa_cobertura_{anio}.png"
    plt.tight_layout()
    plt.savefig(ruta, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Mapa cobertura {anio}: {ruta.name}")
    return imagen


def generar_mapa_cambios(serie_imagenes, output_dir):
    anios = sorted(serie_imagenes.keys())
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    for idx, (t1, t2) in enumerate([(anios[0], anios[len(anios)//2]), (anios[len(anios)//2], anios[-1])]):
        ax = axes[idx]
        diff = serie_imagenes[t2] - serie_imagenes[t1]
        cambio = diff != 0
        rgb = np.ones((*diff.shape, 3))
        rgb[cambio] = [0.8, 0.1, 0.1]
        ax.imshow(rgb, extent=QUINDIO_BOUNDS)
        pct = 100 * cambio.sum() / cambio.size
        ax.set_title(f"Cambios {t1} -> {t2}\n{pct:.1f}% del area cambiado\n{ETIQUETA_SINTETICO}", fontsize=10)
        ax.set_xlabel("Longitud")
        ax.set_ylabel("Latitud")
        ax.annotate("N", xy=(0.95, 0.95), xycoords="axes fraction", fontsize=14, fontweight="bold")
        ax.annotate("^", xy=(0.95, 0.91), xycoords="axes fraction", fontsize=14)
    ruta = output_dir / "02_mapa_cambios.png"
    plt.tight_layout()
    plt.savefig(ruta, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Mapa cambios: {ruta.name}")


def generar_barras_area(serie_imagenes, output_dir):
    ha_por_pixel = 0.01
    datos = {}
    for anio, imagen in serie_imagenes.items():
        counts = np.bincount(imagen.flatten(), minlength=len(CLASES_PRITHVI))
        datos[anio] = counts * ha_por_pixel
    df = pd.DataFrame(datos, index=CLASES_PRITHVI)
    fig, ax = plt.subplots(figsize=(14, 7))
    df.plot(kind="bar", ax=ax, color=[COLORES_CLASES.get(c, "#999999") for c in df.index])
    ax.set_xlabel("Clase de cobertura")
    ax.set_ylabel("Area (hectareas)")
    ax.set_title(f"Area por clase de cobertura - Quindio\n{ETIQUETA_SINTETICO}", fontsize=11)
    ax.legend(title="Anio", bbox_to_anchor=(1.01, 1), loc="upper left")
    ax.tick_params(axis="x", rotation=45)
    ax.grid(True, axis="y", alpha=0.3)
    ruta = output_dir / "03_barras_area_clase.png"
    plt.tight_layout()
    plt.savefig(ruta, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Barras area: {ruta.name}")
    return df


def generar_matriz_transicion(serie_imagenes, output_dir):
    anios = sorted(serie_imagenes.keys())
    matriz = np.zeros((len(CLASES_PRITHVI), len(CLASES_PRITHVI)), dtype=np.float64)
    for i in range(1, len(anios)):
        t1 = serie_imagenes[anios[i-1]].flatten()
        t2 = serie_imagenes[anios[i]].flatten()
        for a, b in zip(t1, t2):
            matriz[a, b] += 1
    total = matriz.sum()
    if total > 0:
        matriz = 100 * matriz / total
    fig, ax = plt.subplots(figsize=(10, 8))
    im = ax.imshow(matriz, cmap="YlOrRd", aspect="auto")
    ax.set_xticks(range(len(CLASES_PRITHVI)))
    ax.set_yticks(range(len(CLASES_PRITHVI)))
    ax.set_xticklabels(CLASES_PRITHVI, rotation=45, ha="right")
    ax.set_yticklabels(CLASES_PRITHVI)
    ax.set_xlabel("Clase hacia")
    ax.set_ylabel("Clase desde")
    ax.set_title(f"Matriz de transicion de coberturas ({anios[0]}-{anios[-1]})\n{ETIQUETA_SINTETICO}", fontsize=10)
    for i in range(len(CLASES_PRITHVI)):
        for j in range(len(CLASES_PRITHVI)):
            ax.text(j, i, f"{matriz[i,j]:.1f}", ha="center", va="center", fontsize=7, color="black" if matriz[i,j] < 50 else "white")
    plt.colorbar(im, ax=ax, label="Porcentaje (%)")
    ruta = output_dir / "04_matriz_transicion.png"
    plt.tight_layout()
    plt.savefig(ruta, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Matriz transicion: {ruta.name}")
    return matriz


def generar_layout_final(serie_imagenes, matriz_transicion, output_dir):
    fig = plt.figure(figsize=(20, 14))
    gs = fig.add_gridspec(2, 3, hspace=0.3, wspace=0.3)
    fig.suptitle(f"CLASIFICACION Y DETECCION DE CAMBIOS DE COBERTURA TERRESTRE - QUINDIO, COLOMBIA\nModelo: Prithvi-EO-2.0 (IBM/NASA) | {ETIQUETA_SINTETICO}", fontsize=13, fontweight="bold", y=0.98)
    ax1 = fig.add_subplot(gs[0, 0:2])
    anio_final = max(serie_imagenes.keys())
    imagen_final = serie_imagenes[anio_final]
    colores = [COLORES_CLASES[c] for c in CLASES_PRITHVI]
    cmap = ListedColormap(colores)
    ax1.imshow(imagen_final, cmap=cmap, vmin=-0.5, vmax=len(CLASES_PRITHVI)-0.5, extent=QUINDIO_BOUNDS)
    patches = [mpatches.Patch(color=COLORES_CLASES[c], label=c) for c in CLASES_PRITHVI]
    ax1.legend(handles=patches, loc="lower left", bbox_to_anchor=(1.01, 0), title="Clases", fontsize=7)
    ax1.set_title(f"Mapa de cobertura - Anio {anio_final}", fontsize=11)
    ax1.set_xlabel("Longitud")
    ax1.set_ylabel("Latitud")
    ax2 = fig.add_subplot(gs[0, 2])
    n = len(CLASES_PRITHVI)
    imagen_transicion = np.array([[j for j in range(n)] for _ in range(n)])
    ax2.set_visible(False)
    ax_norte = fig.add_axes([0.72, 0.72, 0.05, 0.1])
    ax_norte.annotate("N", xy=(0.5, 0.7), ha="center", fontsize=16, fontweight="bold")
    ax_norte.annotate("^", xy=(0.5, 0.4), ha="center", fontsize=16)
    ax_norte.set_xlim(0, 1)
    ax_norte.set_ylim(0, 1)
    ax_norte.axis("off")
    ax3 = fig.add_subplot(gs[1, :2])
    anios = sorted(serie_imagenes.keys())
    cambios_pct = []
    for i in range(1, len(anios)):
        diff = serie_imagenes[anios[i]] - serie_imagenes[anios[i-1]]
        cambios_pct.append(100 * (diff != 0).sum() / diff.size)
    ax3.bar(anios[1:], cambios_pct, color="steelblue", edgecolor="black")
    ax3.set_xlabel("Anio")
    ax3.set_ylabel("Porcentaje de cambio (%)")
    ax3.set_title("Tasa anual de cambio de cobertura", fontsize=11)
    ax3.grid(True, alpha=0.3)
    ax4 = fig.add_subplot(gs[1, 2])
    ax4.axis("off")
    info_text = (
        "INFORMACION DEL MAPA\n"
        "================================\n"
        "Zona: Quindio, Colombia\n"
        f"Anios: {anios[0]}-{anios[-1]}\n"
        f"Resolucion: 10 m\n"
        f"Clases: {len(CLASES_PRITHVI)}\n"
        "CRS: EPSG:9377\n"
        "Modelo: Prithvi-EO-2.0\n"
        "Validacion: Dynamic World\n"
        "================================\n"
        f"{ETIQUETA_SINTETICO}"
    )
    ax4.text(0.05, 0.95, info_text, transform=ax4.transAxes, fontsize=9, verticalalignment="top", fontfamily="monospace", bbox=dict(boxstyle="round", facecolor="lightyellow", alpha=0.8))
    ax_escala = fig.add_axes([0.4, 0.02, 0.2, 0.03])
    ax_escala.set_xlim(0, 100)
    ax_escala.set_ylim(0, 1)
    ax_escala.add_patch(mpatches.Rectangle((0, 0.3), 25, 0.4, facecolor="black"))
    ax_escala.add_patch(mpatches.Rectangle((25, 0.3), 25, 0.4, facecolor="white", edgecolor="black"))
    ax_escala.add_patch(mpatches.Rectangle((50, 0.3), 25, 0.4, facecolor="black"))
    ax_escala.add_patch(mpatches.Rectangle((75, 0.3), 25, 0.4, facecolor="white", edgecolor="black"))
    ax_escala.text(12.5, 0.05, "0", ha="center", fontsize=8)
    ax_escala.text(50, 0.05, "5", ha="center", fontsize=8)
    ax_escala.text(87.5, 0.05, "10 km", ha="center", fontsize=8)
    ax_escala.axis("off")
    ax_coord = fig.add_axes([0.62, 0.02, 0.15, 0.03])
    ax_coord.axis("off")
    ax_coord.text(0.5, 0.5, f"Lat: {QUINDIO_BOUNDS[1]:.2f} a {QUINDIO_BOUNDS[3]:.2f}\nLon: {QUINDIO_BOUNDS[0]:.2f} a {QUINDIO_BOUNDS[2]:.2f}", transform=ax_coord.transAxes, fontsize=8, ha="center", va="center", fontfamily="monospace")
    ruta = output_dir / "05_layout_final_cartografico.png"
    plt.savefig(ruta, dpi=200, bbox_inches="tight")
    plt.close()
    print(f"  Layout final: {ruta.name}")


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print("=" * 60)
    print("GENERACION DE VISUALIZACIONES CON DATOS SINTETICOS")
    print(f"Destino: {OUTPUT_DIR}")
    print("=" * 60)
    rng = np.random.default_rng(42)
    serie_imagenes = {}
    for anio in ANIOS:
        serie_imagenes[anio] = generar_mapa_cobertura(anio, rng, OUTPUT_DIR)
    generar_mapa_cambios(serie_imagenes, OUTPUT_DIR)
    generar_barras_area(serie_imagenes, OUTPUT_DIR)
    matriz = generar_matriz_transicion(serie_imagenes, OUTPUT_DIR)
    generar_layout_final(serie_imagenes, matriz, OUTPUT_DIR)
    print("\n" + "=" * 60)
    print("RESUMEN DE ARCHIVOS GENERADOS")
    print("=" * 60)
    for f in sorted(OUTPUT_DIR.glob("*.png")):
        print(f"  {f.name}")
    print(f"\nTotal: {len(list(OUTPUT_DIR.glob('*.png')))} imagenes PNG")
    print(f"\nNOTA: {ETIQUETA_SINTETICO}")


if __name__ == "__main__":
    main()
