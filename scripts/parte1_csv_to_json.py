import os
import json

# Rutas de entrada y salida
RUTA_BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
RUTA_CSV_AREAS = os.path.join(RUTA_BASE, 'datos', 'csv', 'areas')
RUTA_CSV_CATALOGOS = os.path.join(RUTA_BASE, 'datos', 'csv', 'catalogos')
RUTA_JSON_SALIDA = os.path.join(RUTA_BASE, 'datos', 'json', 'revistas.json')

# Diccionario principal
revistas = {}

def procesar_archivos(ruta, tipo):
    for archivo in os.listdir(ruta):
        if archivo.endswith('.csv'):
            nombre = (
            archivo.replace("_RadGridExport.csv", "")
                .replace(".csv", "")
                .replace(" RadGridExport", "")
                .strip()) # Ej: CIENCIAS_BIO o SCOPUS
            ruta_completa = os.path.join(ruta, archivo)
            with open(ruta_completa, 'r', encoding='latin-1') as f:
                lineas = f.readlines()
                for linea in lineas:
                    titulo = linea.strip().lower()
                    if not titulo or titulo.startswith("titulo"):
                        continue
                    if titulo not in revistas:
                        revistas[titulo] = {"areas": [], "catalogos": []}
                    if tipo == "area" and nombre not in revistas[titulo]["areas"]:
                        revistas[titulo]["areas"].append(nombre)
                    elif tipo == "catalogo" and nombre not in revistas[titulo]["catalogos"]:
                        revistas[titulo]["catalogos"].append(nombre)

# Procesar ambas carpetas
procesar_archivos(RUTA_CSV_AREAS, "area")
procesar_archivos(RUTA_CSV_CATALOGOS, "catalogo")

# Guardar como JSON
os.makedirs(os.path.dirname(RUTA_JSON_SALIDA), exist_ok=True)
with open(RUTA_JSON_SALIDA, 'w', encoding='utf-8') as f:
    json.dump(revistas, f, indent=2, ensure_ascii=False)

print(f"Archivo JSON generado exitosamente en: {RUTA_JSON_SALIDA}")
