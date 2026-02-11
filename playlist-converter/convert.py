import re

# Nombre del archivo que subiste
archivo_entrada = "FLOW ARGENTINA-PARAGUAY-URUGUAY STREAMS UPDATE 2025-15-12-1.txt"
archivo_salida = "lista_completa_flow.m3u"

def generar_m3u():
    try:
        with open(archivo_entrada, 'r', encoding='utf-8') as f:
            contenido = f.readlines()
            
        m3u = ["#EXTM3U\n"]
        grupo_actual = "GENERAL"
        
        i = 0
        while i < len(contenido):
            linea = contenido[i].strip()
            if not linea:
                i += 1
                continue
            
            # Detectar categorías (suelen estar en mayúsculas con "/") 
            if " / " in linea and not linea.startswith("http"):
                grupo_actual = linea.split(" / ")[0]
                i += 1
                continue
            
            # Detectar URL del canal 
            if linea.startswith("https://"):
                url = linea
                # Extraer nombre del canal desde la URL
                nombre_canal = url.split('/')[-1].replace('.mpd', '').replace('_', ' ')
                
                info_drm = ""
                if i + 1 < len(contenido):
                    siguiente = contenido[i+1].strip()
                    # Si la siguiente línea es una llave DRM (contiene ":") 
                    if ":" in siguiente and not siguiente.startswith("http"):
                        info_drm = siguiente
                        i += 2
                    else:
                        i += 1
                else:
                    i += 1
                
                # Escribir entrada M3U
                m3u.append(f'#EXTINF:-1 tvg-id="{nombre_canal}" tvg-name="{nombre_canal}" group-title="{grupo_actual}",{nombre_canal}\n')
                m3u.append("#KODIPROP:inputstream=inputstream.adaptive\n")
                if info_drm and "NO REQUIERE" not in info_drm.upper():
                    m3u.append("#KODIPROP:inputstream.adaptive.license_type=clearkey\n")
                    m3u.append(f"#KODIPROP:inputstream.adaptive.license_key={info_drm}\n")
                m3u.append(f"{url}\n\n")
            else:
                i += 1
                
        with open(archivo_salida, 'w', encoding='utf-8') as f:
            f.writelines(m3u)
            
        print(f"¡Éxito! Archivo '{archivo_salida}' generado con todos los canales.")
        
    except FileNotFoundError:
        print("Asegúrate de que el archivo de texto esté en la misma carpeta que el script.")

if __name__ == "__main__":
    generar_m3u()