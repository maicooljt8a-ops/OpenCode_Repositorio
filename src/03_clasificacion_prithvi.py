import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader

from src.config import (
    CLASES_PRITHVI, TILE_SIZE, BATCH_SIZE, NUM_WORKERS, DATA_PROCESSED,
)


class QuindioDataset(Dataset):
    def __init__(self, images, labels=None, transform=None):
        self.images = images
        self.labels = labels
        self.transform = transform

    def __len__(self):
        return len(self.images)

    def __getitem__(self, idx):
        image = self.images[idx]
        if self.transform:
            image = self.transform(image)
        if self.labels is not None:
            label = self.labels[idx]
            return image, label
        return image


def obtener_modelo_prithvi(num_clases=len(CLASES_PRITHVI)):
    try:
        from terratorch.registry import BACKBONE_REGISTRY
        backbone = BACKBONE_REGISTRY.build("ibm-nasa-geospatial/Prithvi-EO-2.0-300M-TL")
        model = PrithviSegmentation(backbone, num_clases)
        print("Modelo Prithvi-EO-2.0 cargado desde TerraTorch")
        return model
    except ImportError:
        print("WARNING: terratorch no instalado. Usando arquitectura simplificada.")
        return None
    except Exception as e:
        print(f"ERROR cargando Prithvi: {e}")
        return None


class PrithviSegmentation(torch.nn.Module):
    def __init__(self, backbone, num_clases):
        super().__init__()
        self.backbone = backbone
        self.decoder = torch.nn.Sequential(
            torch.nn.Conv2d(768, 256, 3, padding=1),
            torch.nn.ReLU(),
            torch.nn.Conv2d(256, num_clases, 1),
        )

    def forward(self, x):
        features = self.backbone(x)
        if isinstance(features, (list, tuple)):
            features = features[-1]
        logits = self.decoder(features)
        return logits


def inferir_prithvi(modelo, imagen, device="cpu"):
    modelo.eval()
    modelo.to(device)
    with torch.no_grad():
        if not isinstance(imagen, torch.Tensor):
            imagen = torch.from_numpy(imagen).float()
        if imagen.ndim == 3:
            imagen = imagen.unsqueeze(0)
        imagen = imagen.to(device)
        logits = modelo(imagen)
        prediccion = torch.argmax(logits, dim=1)
    return prediccion.cpu().numpy()


def clasificar_zona_prithvi(modelo, serie_procesada, device="cpu"):
    clasificaciones = {}
    for anio, datos in serie_procesada.items():
        print(f"  Clasificando {anio} con Prithvi...")
        imagen = datos.get("array_s2")
        if imagen is None:
            continue
        pred = inferir_prithvi(modelo, imagen, device)
        clasificaciones[anio] = {
            "prediccion": pred,
            "clases": CLASES_PRITHVI,
        }
    return clasificaciones


def guardar_modelo(modelo, ruta):
    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    torch.save(modelo.state_dict(), ruta)
    print(f"Modelo guardado: {ruta}")


def cargar_modelo(ruta, num_clases=len(CLASES_PRITHVI)):
    modelo = obtener_modelo_prithvi(num_clases)
    if modelo and Path(ruta).exists():
        modelo.load_state_dict(torch.load(ruta, map_location="cpu"))
        print(f"Modelo cargado: {ruta}")
    return modelo


def main():
    print("=" * 60)
    print("CLASIFICACION CON PRITHI-EO-2.0 - QUINDIO")
    print("=" * 60)
    print(f"Clases: {CLASES_PRITHVI}")
    print(f"Tile: {TILE_SIZE}x{TILE_SIZE}")
    print(f"Batch: {BATCH_SIZE}")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Dispositivo: {device}")
    modelo = obtener_modelo_prithvi()
    if modelo is None:
        print("Modelo no disponible. Entrene manualmente o instale terratorch.")
    return modelo


if __name__ == "__main__":
    main()
