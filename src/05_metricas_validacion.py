import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import json
import numpy as np
from sklearn.metrics import (
    confusion_matrix, classification_report, cohen_kappa_score,
    accuracy_score, f1_score,
)

from src.config import CLASES_PRITHVI, CLASES_DYNAMIC_WORLD, DATA_PROCESSED, OUTPUTS


def calcular_metricas_clasificacion(y_true, y_pred, clases):
    oa = accuracy_score(y_true, y_pred)
    kappa = cohen_kappa_score(y_true, y_pred)
    f1_macro = f1_score(y_true, y_pred, average="macro", zero_division=0)
    f1_weighted = f1_score(y_true, y_pred, average="weighted", zero_division=0)
    report = classification_report(y_true, y_pred, target_names=clases, output_dict=True, zero_division=0)
    cm = confusion_matrix(y_true, y_pred, labels=range(len(clases)))
    return {
        "overall_accuracy": float(oa),
        "kappa": float(kappa),
        "f1_macro": float(f1_macro),
        "f1_weighted": float(f1_weighted),
        "classification_report": report,
        "confusion_matrix": cm.tolist(),
        "clases": clases,
    }


def validar_contra_dynamic_world(prediccion_prithvi, probabilidades_dw, clases_dw):
    clases_validas = [c for c in CLASES_DYNAMIC_WORLD if c in clases_dw]
    metricas = {}
    for clase in clases_validas:
        if clase in probabilidades_dw:
            dw_mask = probabilidades_dw[clase] > 0.5
            prithvi_mask = prediccion_prithvi == CLASES_PRITHVI.index(clase) if clase in CLASES_PRITHVI else None
            if prithvi_mask is not None:
                interseccion = np.logical_and(dw_mask, prithvi_mask).sum()
                union = np.logical_or(dw_mask, prithvi_mask).sum()
                iou = interseccion / union if union > 0 else 0
                metricas[clase] = {"iou": float(iou), "dw_pixeles": int(dw_mask.sum()), "prithvi_pixeles": int(prithvi_mask.sum())}
    return metricas


def guardar_metricas(metricas, nombre_archivo="metricas_validacion.json"):
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    ruta = OUTPUTS / nombre_archivo
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(metricas, f, ensure_ascii=False, indent=2)
    print(f"Metricas guardadas: {ruta}")


def generar_informe_validacion(metricas, ruta_salida):
    with open(ruta_salida, "w", encoding="utf-8") as f:
        f.write("# Informe de Validacion - Clasificacion de Cobertura\n\n")
        f.write("## Metricas Generales\n\n")
        f.write(f"- **Overall Accuracy:** {metricas.get('overall_accuracy', 'N/A'):.4f}\n")
        f.write(f"- **Kappa:** {metricas.get('kappa', 'N/A'):.4f}\n")
        f.write(f"- **F1 Macro:** {metricas.get('f1_macro', 'N/A'):.4f}\n")
        f.write(f"- **F1 Weighted:** {metricas.get('f1_weighted', 'N/A'):.4f}\n")
    print(f"Informe generado: {ruta_salida}")


def main():
    print("=" * 60)
    print("VALIDACION - QUINDIO")
    print("=" * 60)
    print(f"Clases Prithvi: {CLASES_PRITHVI}")
    print(f"Clases Dynamic World: {CLASES_DYNAMIC_WORLD}")
    print("Validacion lista. Se requieren datos de prediccion y referencia.")


if __name__ == "__main__":
    main()
