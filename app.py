from flask import Flask, render_template, request, redirect, url_for, session, flash
import json
import os
import re
from datetime import datetime
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


@app.route('/areas')
def areas():
    """Lista de áreas disponibles"""
    return render_template('areas.html', areas=AREAS)

@app.route('/area/<area>')
def area_detalle(area):
    """Revistas por área"""
    revistas_area = []
    
    for titulo, datos in REVISTAS.items():
        if area in datos.get('areas', []):
            h_index = datos.get('scimago_info', {}).get('h_index', 'N/A')
            revistas_area.append({
                'titulo': titulo,
                'h_index': h_index
            })
    
    revistas_area.sort(key=lambda x: x['titulo'])
    
    return render_template('area_detalle.html', area=area, revistas=revistas_area, now=datetime.now())

@app.route('/catalogos')
def catalogos():
    """Lista de catálogos disponibles"""
    return render_template('catalogos.html', catalogos=CATALOGOS)

@app.route('/catalogo/<catalogo>')
def catalogo_detalle(catalogo):
    """Revistas por catálogo"""
    revistas_catalogo = []
    
    for titulo, datos in REVISTAS.items():
        if catalogo in datos.get('catalogos', []):
            h_index = datos.get('scimago_info', {}).get('h_index', 'N/A')
            revistas_catalogo.append({
                'titulo': titulo,
                'h_index': h_index
            })
    
    revistas_catalogo.sort(key=lambda x: x['titulo'])
    
    return render_template('catalogo_detalle.html', catalogo=catalogo, revistas=revistas_catalogo)

@app.route('/explorar')
def explorar():
    """Explorar revistas por letra inicial"""
    return render_template('explorar.html')

@app.route('/explorar/<letra>')
def explorar_letra(letra):
    """Revistas que comienzan con una letra específica"""
    revistas_letra = []
    
    for titulo, datos in REVISTAS.items():
        if titulo.lower().startswith(letra.lower()):
            h_index = datos.get('scimago_info', {}).get('h_index', 'N/A')
            revistas_letra.append({
                'titulo': titulo,
                'areas': datos.get('areas', []),
                'catalogos': datos.get('catalogos', []),
                'h_index': h_index
            })
    
    revistas_letra.sort(key=lambda x: x['titulo'])
    
    return render_template('explorar_letras.html', letra=letra, revistas=revistas_letra)


@app.route('/buscar')
def buscar():
    query = request.args.get('q', '').strip().lower()
    
    # Depuración - verifica en terminal lo que se está recibiendo
    print(f"Término de búsqueda recibido: '{query}'")
    print(f"Total revistas cargadas: {len(REVISTAS)}")
    
    if not query:
        return render_template('buscar.html', resultados=[], query='')
    
    resultados = []
    for titulo, datos in REVISTAS.items():
        # Búsqueda insensible a mayúsculas y minúsculas
        if query in titulo.lower():
            resultados.append({
                'titulo': titulo,
                'h_index': datos.get('scimago_info', {}).get('h_index', 'N/A'),
                'areas': datos.get('areas', []),
                'catalogos': datos.get('catalogos', []),
                'issn': datos.get('issn', 'N/A')  # Agrega más campos si es necesario
            })
    
    # Depuración - verifica los resultados encontrados
    print(f"Resultados encontrados: {len(resultados)}")
    
    return render_template('buscar.html', resultados=resultados, query=query)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Autenticación simple (en producción usar base de datos)
        if username and password:
            session['usuario'] = username
            flash(f'Bienvenido, {username}!', 'success')
            return redirect(url_for('inicio'))
        else:
            flash('Usuario o contraseña incorrectos', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Cerrar sesión"""
    session.pop('usuario', None)
    flash('Sesión cerrada correctamente', 'success')
    return redirect(url_for('inicio'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True)