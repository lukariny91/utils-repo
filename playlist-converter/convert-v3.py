import os

def procesar_archivo_flow(filepath):
    config = {}
    streams = []
    
    if not os.path.exists(filepath):
        print(f"Error: No se encontró el archivo '{filepath}'")
        return []

    # Abrimos con utf-8-sig para evitar problemas con carácteres invisibles de Windows (BOM)
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        # Limpiamos cada línea de espacios en blanco y tabulaciones
        lines = [line.strip() for line in f if line.strip()]

    i = 0
    while i < len(lines):
        line = lines[i]

        # 1. Capturar Headers de configuración
        if line.startswith(("ORIGIN-", "REFERER-")):
            if ':' in line:
                key, value = line.split(":", 1)
                config[key.strip()] = value.strip()
            i += 1
            continue

        # 2. Capturar Streams
        if line.startswith("http"):
            # Limpiar URL de posibles espacios o textos como "(NEW)"
            url_completa = line.split()[0].strip()
            
            # Obtener nombre y limpiar extensiones
            nombre_archivo = url_completa.split('/')[-1]
            nombre_limpio = nombre_archivo.split('?')[0] # Quitar parámetros si los hay
            nombre_limpio = nombre_limpio.replace(".mpd", "").replace(".m3u8", "").replace(".m3u", "").strip()
            
            # Buscar Key DRM
            drm_key = None
            if i + 1 < len(lines):
                next_line = lines[i+1]
                # Si la línea siguiente no es URL ni Config, es potencialmente una KEY
                if not next_line.startswith("http") and not next_line.startswith(("ORIGIN-", "REFERER-")):
                    if "NO REQUIERE" not in next_line.upper():
                        drm_key = next_line.strip()
                    i += 1 

            # Lógica de asignación de País
            pais = "ARG"
            nombre_upper = nombre_limpio.upper()
            if "_UY" in nombre_upper or " UY" in nombre_upper or nombre_upper.endswith("UY"):
                pais = "UY"
            elif "_PY" in nombre_upper or " PY" in nombre_upper or nombre_upper.endswith("PY"):
                pais = "PY"

            # Obtener headers según país
            origin = config.get(f"ORIGIN-{pais}", config.get("ORIGIN-ARG", ""))
            referer = config.get(f"REFERER-{pais}", config.get("REFERER-ARG", ""))

            streams.append({
                "nombre": nombre_limpio,
                "pais": pais,
                "url": url_completa,
                "key": drm_key,
                "origin": origin,
                "referer": referer
            })
        i += 1
    return streams

def generar_m3u(streams, nombre_salida="playlist_flow.m3u"):
    with open(nombre_salida, "w", encoding='utf-8') as m3u:
        m3u.write("#EXTM3U\n\n")
        
        for item in streams:
            # Escribir metadatos del canal
            m3u.write(f'#EXTINF:-1 group-title="{item["pais"]}", {item["nombre"]}\n')
            
            # Variables de Kodi requeridas
            m3u.write('#KODIPROP:inputstream=inputstream.adaptive\n')
            m3u.write('#KODIPROP:inputstream.adaptive.license_type=clearkey\n')
            
            # Escribir Key solo si existe
            if item["key"]:
                m3u.write(f'#KODIPROP:inputstream.adaptive.license_key={item["key"]}\n')
            
            # Headers Origin y Referer
            m3u.write(f'#EXTVLCOPT:http-origin={item["origin"]}\n')
            m3u.write(f'#EXTVLCOPT:http-referrer={item["referer"]}\n')
            
            # URL del stream
            m3u.write(f'{item["url"]}\n\n') # Doble salto de línea para separar bloques

    print(f"Archivo '{nombre_salida}' generado exitosamente.")

# --- Ejecución ---
nombre_txt = 'lista_flow.txt'
canales = procesar_archivo_flow(nombre_txt)
generar_m3u(canales)