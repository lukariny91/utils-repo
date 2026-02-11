import os

def procesar_archivo_mixto(filepath):
    """
    Lee un archivo único que contiene tanto la configuración de headers
    como la lista de streams, y asocia los headers correctos a cada link.
    """
    
    config = {}
    streams = []
    
    # Verificamos que el archivo exista
    if not os.path.exists(filepath):
        print(f"Error: No se encontró el archivo '{filepath}'")
        return []

    with open(filepath, 'r', encoding='utf-8') as f:
        # Leemos y limpiamos espacios vacíos al inicio/final de cada línea
        lines = [line.strip() for line in f if line.strip()]

    i = 0
    while i < len(lines):
        line = lines[i]

        # --- FASE 1: Detección de Configuración ---
        # Si la línea empieza con ORIGIN- o REFERER-, la guardamos en el diccionario config
        if line.startswith(("ORIGIN-", "REFERER-")):
            try:
                key, value = line.split(":", 1)
                config[key.strip()] = value.strip()
            except ValueError:
                pass # Ignorar líneas mal formadas
            i += 1
            continue

        # --- FASE 2: Detección de Streams ---
        # Si detectamos una URL, asumimos que es un canal
        if line.startswith("http"):
            url = line
            mpd_name = url.split('/')[-1] # Obtenemos el nombre del archivo (ej: FoxSports3_UY.mpd)
            
            # Buscamos la Key en la línea siguiente (si existe)
            drm_key = "SIN DATOS"
            if i + 1 < len(lines):
                next_line = lines[i+1]
                # Verificamos que la siguiente línea no sea otra URL ni una configuración
                if not next_line.startswith("http") and not next_line.startswith(("ORIGIN-", "REFERER-")):
                    drm_key = next_line
                    i += 1 # Saltamos la línea de la key ya que la acabamos de usar

            # --- FASE 3: Lógica de País ---
            # Determinamos qué headers usar basándonos en el nombre del archivo
            pais_detectado = "ARG" # Default
            
            nombre_upper = mpd_name.upper()
            
            if "UY" in nombre_upper:
                pais_detectado = "UY"
            elif "PY" in nombre_upper:
                pais_detectado = "PY"
            # Si es ARG o no tiene nada, se queda con el default "ARG" definido arriba

            # Obtenemos los headers del diccionario de config que llenamos al principio
            origin = config.get(f"ORIGIN-{pais_detectado}", "No definido")
            referer = config.get(f"REFERER-{pais_detectado}", "No definido")

            # Guardamos el objeto completo
            stream_info = {
                "nombre_archivo": mpd_name,
                "pais": pais_detectado,
                "url": url,
                "key": drm_key,
                "headers": {
                    "Origin": origin,
                    "Referer": referer
                }
            }
            streams.append(stream_info)
        
        # Avanzamos a la siguiente línea si no era ni config ni url
        i += 1

    return streams

# --- EJECUCIÓN DEL SCRIPT ---

nombre_archivo = 'lista_flow.txt' # Asegúrate de que tu archivo se llame así
lista_procesada = procesar_archivo_mixto(nombre_archivo)

print(f"--- Se procesaron {len(lista_procesada)} canales ---\n")

# Ejemplo: Imprimir los primeros 5 resultados para verificar
for item in lista_procesada:
    print(f"Canal: {item['nombre_archivo']}")
    print(f"País Detectado: {item['pais']}")
    print(f"URL: {item['url']}")
    print(f"Key/DRM: {item['key']}")
    print(f"Headers Aplicados: {item['headers']}")
    print("-" * 50)

# Opcional: Generar un archivo M3U simple con la info
with open("playlist_flow.m3u", "w", encoding='utf-8') as m3u:
    m3u.write("#EXTM3U\n")
    for item in lista_procesada:
        userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        # Formato estándar para reproductores que aceptan headers en el link (como TiviMate o VLC modificados)
        # Nota: El formato de headers en M3U varía según el reproductor. Este es un formato genérico.
        m3u.write(f'#EXTINF:-1 group-title="{item["pais"]}", {item["nombre_archivo"]}\n')
        m3u.write(f'#KODIPROP:inputstream.adaptive.license_key={item["key"]}\n')
        m3u.write(f'#EXTVLCOPT:http-user-agent={userAgent}\n')
        m3u.write(f'#EXTVLCOPT:http-origin={item["headers"]["Origin"]}\n')
        m3u.write(f'#EXTVLCOPT:http-referrer={item["headers"]["Referer"]}\n')
        m3u.write(f'{item["url"]}\n')

print("Se ha generado el archivo 'playlist_flow.m3u' con los headers inyectados.")
