from flask import Flask, render_template, request, redirect, url_for, session, flash
import json
import os
import re
from datetime import datetime


app = Flask(__name__)
app.secret_key = 'unison_revistas_academicas'  # Clave para sesiones

# Cargar datos
RUTA_BASE = os.path.abspath(os.path.dirname(__file__))
RUTA_JSON = os.path.join(RUTA_BASE, 'datos', 'json', 'revistas_completo.json')

with open(RUTA_JSON, 'r', encoding='utf-8') as f:
    REVISTAS = json.load(f)

# Obtener listas únicas de áreas y catálogos
AREAS = set()
CATALOGOS = set()

for revista_data in REVISTAS.values():
    for area in revista_data.get('areas', []):
        AREAS.add(area)
    for catalogo in revista_data.get('catalogos', []):
        CATALOGOS.add(catalogo)

AREAS = sorted(list(AREAS))
CATALOGOS = sorted(list(CATALOGOS))

# Rutas de la aplicación
@app.route('/')
def inicio():
    """Página de inicio"""
    now = datetime.now()
    total_revistas = len(REVISTAS)
    total_areas = len(AREAS)
    total_catalogos = len(CATALOGOS)
    
    # Obtener algunas estadísticas
    revistas_con_hindex = sum(1 for r in REVISTAS.values() if r.get('scimago_info', {}).get('h_index'))
    
    return render_template(
    'inicio.html', 
    total_revistas=total_revistas,
    total_areas=total_areas,
    total_catalogos=total_catalogos,
    revistas_con_hindex=revistas_con_hindex,
    now=now  
)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True)
