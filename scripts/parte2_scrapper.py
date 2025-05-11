import os
import json
import time
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

# Rutas
RUTA_BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
RUTA_JSON_ENTRADA = os.path.join(RUTA_BASE, 'datos', 'json', 'revistas.json')
RUTA_JSON_SALIDA = os.path.join(RUTA_BASE, 'datos', 'json', 'revistas_completo.json')

# Cargar el JSON generado en la parte 1
with open(RUTA_JSON_ENTRADA, 'r', encoding='utf-8') as f:
    revistas = json.load(f)

# Función para buscar en SCIMAGO
def buscar_en_scimago(titulo):
    """
    Busca información de una revista en SCIMAGO
    
    Args:
        titulo (str): Título de la revista
        
    Returns:
        dict: Información obtenida de SCIMAGO
    """
    # Verificar si ya tenemos la información
    if "scimago_info" in revistas[titulo] and revistas[titulo]["scimago_info"].get("ultima_visita"):
        ultima_visita = datetime.strptime(revistas[titulo]["scimago_info"]["ultima_visita"], "%Y-%m-%d")
        dias_transcurridos = (datetime.now() - ultima_visita).days
        
        # Si la información tiene menos de 30 días, la usamos
        if dias_transcurridos < 30:
            print(f"  Usando información en caché para: {titulo}")
            return revistas[titulo]["scimago_info"]
    
    print(f"  Buscando en SCIMAGO: {titulo}")
    
    # Preparar la búsqueda
    search_url = f"https://www.scimagojr.com/journalsearch.php?q={titulo.replace(' ', '+')}"
    
    try:
        # Realizar la búsqueda
        response = requests.get(search_url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        if response.status_code != 200:
            print(f"  Error al buscar: {response.status_code}")
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Buscar resultados
        resultados = soup.select('.search_results a')
        if not resultados:
            print(f"  No se encontraron resultados para: {titulo}")
            return None
        
        # Tomar el primer resultado
        journal_url = "https://www.scimagojr.com/" + resultados[0]['href']
        
        # Esperar un poco para no sobrecargar el servidor
        time.sleep(1)
        
        # Obtener la página de la revista
        journal_response = requests.get(journal_url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        if journal_response.status_code != 200:
            print(f"  Error al obtener detalles: {journal_response.status_code}")
            return None
        
        journal_soup = BeautifulSoup(journal_response.text, 'html.parser')
        
        # Extraer información
        info = {
            "titulo_scimago": journal_soup.select_one('title').text.split(' - ')[0].strip() if journal_soup.select_one('title') else "",
            "sitio_web": "",
            "h_index": "",
            "subject_area": [],
            "publisher": "",
            "issn": "",
            "publication_type": "",
            "widget": journal_url,
            "ultima_visita": datetime.now().strftime("%Y-%m-%d")
        }
        
        # Extraer H-Index
        h_index_cell = journal_soup.select_one('td:-soup-contains("H index")')
        if h_index_cell and h_index_cell.find_next('td'):
            info["h_index"] = h_index_cell.find_next('td').text.strip()
        
        # Extraer ISSN
        issn_cell = journal_soup.select_one('td:-soup-contains("ISSN")')
        if issn_cell and issn_cell.find_next('td'):
            info["issn"] = issn_cell.find_next('td').text.strip()
        
        # Extraer Publisher
        publisher_cell = journal_soup.select_one('td:-soup-contains("Publisher")')
        if publisher_cell and publisher_cell.find_next('td'):
            info["publisher"] = publisher_cell.find_next('td').text.strip()
        
        # Extraer Publication Type
        type_cell = journal_soup.select_one('td:-soup-contains("Type")')
        if type_cell and type_cell.find_next('td'):
            info["publication_type"] = type_cell.find_next('td').text.strip()
        
        # Extraer Subject Areas
        subject_areas = journal_soup.select('.treecategory')
        for area in subject_areas:
            info["subject_area"].append(area.text.strip())
        
        # Extraer sitio web
        website_link = journal_soup.select_one('a[title="Journal Website"]')
        if website_link:
            info["sitio_web"] = website_link['href']
        
        print(f"  Información obtenida para: {titulo}")
        return info
        
    except Exception as e:
        print(f"  Error al procesar {titulo}: {str(e)}")
        return None

# Procesar cada revista
total = len(revistas)
contador = 0

for titulo in list(revistas.keys()):
    contador += 1
    print(f"Procesando revista {contador}/{total}: {titulo}")
    
    # Obtener información de SCIMAGO
    info_scimago = buscar_en_scimago(titulo)
    
    if info_scimago:
        revistas[titulo]["scimago_info"] = info_scimago
    
    # Guardar cada 10 revistas para no perder progreso
    if contador % 10 == 0:
        with open(RUTA_JSON_SALIDA, 'w', encoding='utf-8') as f:
            json.dump(revistas, f, indent=2, ensure_ascii=False)
        print(f"Guardado progreso: {contador}/{total}")
    
    # Esperar un poco entre solicitudes para no sobrecargar el servidor
    time.sleep(2)

# Guardar el resultado final
with open(RUTA_JSON_SALIDA, 'w', encoding='utf-8') as f:
    json.dump(revistas, f, indent=2, ensure_ascii=False)

print(f"Archivo JSON completo generado exitosamente en: {RUTA_JSON_SALIDA}")
