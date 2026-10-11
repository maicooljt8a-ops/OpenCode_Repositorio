# Bitácora del Proyecto — Clasificación y Detección de Cambios de Cobertura Terrestre del Quindío

## Estudiante
- **Nombre:** Maicol J. Torres
- **ID:** based-minion-3651
- **Materia:** Inteligencia Artificial aplicada al Territorio
- **Universidad:** Universidad Distrital Francisco José de Caldas
- **Proyecto:** Repositorio_Clase7

---

## Prompt de Plan (2026-10-10)

> Crea un programa en Python que me permita clasificar y detectar los cambios en el tiempo de la cobertura terrestre de una zona de Colombia, el Quindío, empleando modelos de inteligencia artificial espacial de código abierto.

### Plan Aprobado

**Objetivo:** Clasificar cobertura terrestre del Quindío y detectar cambios temporales con modelos de IA espacial de código abierto.

**Modelos seleccionados:**
- Prithvi-EO-2.0 (IBM/NASA) — Foundation model geoespacial, Apache 2.0
- Dynamic World (Google) — Validación de referencia, datos abiertos
- SAM 2 / SAMGeo (Meta/opengeos) — Segmentación de cambios, Apache 2.0 / MIT
- GeoAI (opengeos) — Framework geoespacial AI, MIT

**Fuentes de datos:**
- Sentinel-2 (ESA), 2018–2025
- Dynamic World (Google), validación
- Límites municipales GADM/IGAC
- MDE SRTM/ALOS PALSAR

**Flujo:**
1. Preparación: zona, descarga, composición anual
2. Clasificación baseline: Dynamic World
3. Modelo fundacional: fine-tuning Prithvi-EO-2.0
4. Detección de cambios: diferencias + SAM 2
5. Validación y exportación: métricas + reporte

**Decisiones técnicas:**
- CRS cálculo: EPSG:9377, CRS web: EPSG:4326
- Resolución: 10m
- Tamaño tile: 256×256
- Umbral de cambio: 0.15
- Autenticación EE: variable de entorno EE_PROJECT

---

## Mensaje de Aprobación (2026-10-10)

> Aprobado el plan. Ejecútalo completo, etapa por etapa, sin esperar mi confirmación entre etapas.
> La clasificación debe hacerla un modelo de IA espacial de código abierto (por ejemplo Prithvi-EO, Clay o Copernicus-FM con TorchGeo). Usa Earth Engine para obtener Sentinel-2 y Dynamic World solo como referencia de validación.
> Crea una bitácora (BITACORA.md) que consigne todas las decisiones, acciones y prompts utilizados, empezando por el prompt de Plan, el plan aprobado y este mensaje. Actualízala en cada etapa, incluyendo errores y cómo los resolviste.
> Esta carpeta ya es un repositorio de git conectado a GitHub: haz un commit claro en español al terminar cada etapa y push a main. Crea README.md, requirements.txt y .gitignore.
> Nunca escribas tokens, contraseñas ni claves en ningún archivo. El ID del proyecto de Earth Engine va en config.yaml o en una variable de entorno.
> Si necesitas algo que solo yo puedo hacer (por ejemplo, autenticarme en Earth Engine), detente, dime exactamente qué hacer y espera. Al terminar, resúmeme lo que hiciste.

---

## Registro de Ejecución

### Etapa 0: Inicialización (2026-10-10)

**Acciones:**
1. Verificado directorio de trabajo: `C:\Users\maico\OneDrive\Documentos\Default Project`
2. Descubierto que `.git` no existía. Se ejecutó `git init`.
3. Agregado remote: `https://github.com/maicoltas/Repositorio_Clase7.git`
4. Creado BITACORA.md, README.md, requirements.txt, .gitignore, config.yaml
5. Creados modulos `src/00_config.py` a `src/07_exportar_resultados.py`
6. Eliminados archivos obsoletos del proyecto anterior (`01_clasificacion_cobertura.py`, `config.py`)

**Decisiones:**
- Modelo principal: Prithvi-EO-2.0 (IBM/NASA) via TerraTorch, 300M parametros
- Dynamic World: solo validacion de referencia, nunca como fuente primaria
- SAM 2: reservado para delimitacion de zonas de cambio (fase posterior)
- Estructura modular 00-07 para orden de ejecucion secuencial
- Sin credenciales en codigo: EE_PROJECT via variable de entorno

**Errores y soluciones:**
- `.git` no existia pese a indicacion del usuario. Se inicializo repositorio.

---

### Etapa 1: Implementación de módulos (2026-10-10)

**Acciones:**
1. Creado `src/00_config.py`: parametros centralizados (zona Quindio, anios 2018-2025, clases)
2. Creado `src/01_descarga_datos.py`: Earth Engine para Sentinel-2 y Dynamic World
3. Creado `src/02_preprocesamiento.py`: indices espectrales, cloud masking, tiles
4. Creado `src/03_clasificacion_prithvi.py`: modelo Prithvi-EO-2.0 con TerraTorch
5. Creado `src/04_deteccion_cambios.py`: matriz de transicion y tasas de cambio
6. Creado `src/05_metricas_validacion.py`: OA, Kappa, F1, IoU vs Dynamic World
7. Creado `src/06_visualizacion.py`: graficas de series, matrices, distribuciones
8. Creado `src/07_exportar_resultados.py`: CSV, GeoJSON, GeoTIFF, JSON, HTML

**Archivos de soporte:**
- `requirements.txt`: dependencias (earthengine-api, torch, terratorch, etc.)
- `.gitignore`: excluye .venv, data/raw/*.tif, outputs/*.html, config.yaml con credenciales
- `README.md`: documentacion del proyecto
- `config.yaml`: plantilla de configuracion sin credenciales

---

*(La bitácora se actualiza al final de cada etapa)*

