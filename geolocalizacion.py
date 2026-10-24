import requests
import urllib.parse

url_geocodificacion = "https://graphhopper.com/api/1/geocode?"
url_ruta = "https://graphhopper.com/api/1/route?"

# API Key
clave = "8116d6a9-8f36-4a64-8610-a5b5158d13f5"

nombres_vehiculo = {
    "car": "auto",
    "bike": "bicicleta",
    "foot": "a pie"
}

def geocodificar(ubicacion, api_key):
    while ubicacion.strip() == "":
        ubicacion = input("La ubicación no puede estar vacía. Trata ingresarla nuevamente: ")

    params = {
        "q": ubicacion,
        "limit": "1",
        "locale": "es",
        "key": api_key
    }
    url = url_geocodificacion + urllib.parse.urlencode(params)
    respuesta = requests.get(url)
    estado = respuesta.status_code
    datos = respuesta.json()

    if estado == 200 and len(datos.get("hits", [])) > 0:
        hit = datos["hits"][0]
        lat = hit["point"]["lat"]
        lng = hit["point"]["lng"]
        nombre = hit.get("name", "")
        region = hit.get("state", "")
        pais = hit.get("country", "")
        tipo = hit.get("osm_value", "lugar")

        nombre_completo = ", ".join([p for p in [nombre, region, pais] if p])
        print(f"\n[OK] Encontrado: {nombre_completo} (Tipo: {tipo})")
        print(f"Coordenadas: Latitud {lat:.2f}, Longitud {lng:.2f}")
        return estado, lat, lng, nombre_completo
    else:
        print(f"\n[Error] No se encontró '{ubicacion}'. Código de respuesta: {estado}")
        if "message" in datos:
            print(f"Detalle: {datos['message']}")
        return estado, None, None, ubicacion


while True:
    print("\n" + "=" * 55)
    print("      SISTEMA DE RUTAS - BIBLIOTECA NACIONAL")
    print("=" * 55)
    print("Perfiles válidos: car (auto), bike (bicicleta), foot (a pie)")
    print("Para salir del programa ingrese 's' o 'salir'.")
    print("-" * 55)

    transporte = input("Seleccione el medio de transporte: ").strip().lower()
    if transporte in ["s", "salir"]:
        print("Saliendo del programa...")
        break

    if transporte not in nombres_vehiculo:
        transporte = "car"
        print("Opción no válida. Se utilizará 'car' (auto) por defecto.")

    
    origen_input = input("\nIngrese la ubicación inicial: ").strip()
    if origen_input.lower() in ["s", "salir"]:
        print("Saliendo del programa...")
        break

    est1, lat1, lng1, nom1 = geocodificar(origen_input, clave)
    if lat1 is None:
        print("No se pudo fijar el punto de origen. Intente otra vez.")
        continue

    
    destino_input = input("\nIngrese la ubicación de destino: ").strip()
    if destino_input.lower() in ["s", "salir"]:
        print("Saliendo del programa...")
        break

    est2, lat2, lng2, nom2 = geocodificar(destino_input, clave)
    if lat2 is None:
        print("No se pudo fijar el punto de destino. Intente otra vez.")
        continue

    
    puntos = f"&point={lat1}%2C{lng1}&point={lat2}%2C{lng2}"
    params_ruta = {
        "key": clave,
        "vehicle": transporte,
        "locale": "es"
    }
    url_final_ruta = url_ruta + urllib.parse.urlencode(params_ruta) + puntos

    res_ruta = requests.get(url_final_ruta)
    cod_ruta = res_ruta.status_code
    datos_ruta = res_ruta.json()

    print("\n" + "=" * 55)
    print(f"Estado de la API de Rutas: {cod_ruta}")

    if cod_ruta == 200 and "paths" in datos_ruta:
        tramo = datos_ruta["paths"][0]

        # Conversion
        km = tramo["distance"] / 1000.0
        duracion_min = (tramo["time"] / 1000.0) / 60.0
        horas_reloj = int(duracion_min // 60)
        minutos_reloj = int(duracion_min % 60)
        segundos_reloj = int((tramo["time"] / 1000.0) % 60)

        print("=" * 55)
        print(f"Origen: {nom1}")
        print(f"Destino: {nom2}")
        print(f"Medio de transporte: {nombres_vehiculo[transporte]}")
        print(f"Distancia total: {km:.2f} km")
        print(f"Duración estimada: {horas_reloj:02d}:{minutos_reloj:02d}:{segundos_reloj:02d} ({duracion_min:.2f} minutos)")
        print("=" * 55)
        print("NARRATIVA DEL VIAJE (Instrucciones paso a paso):")
        print("-" * 55)

        for i, paso in enumerate(tramo.get("instructions", []), start=1):
            texto = paso["text"]
            dist_paso_km = paso["distance"] / 1000.0
            tiempo_paso_min = (paso["time"] / 1000.0) / 60.0
            print(f"{i:>2}. {texto} (Distancia: {dist_paso_km:.2f} km | Tiempo: {tiempo_paso_min:.2f} min)")

        print("=" * 55)
    else:
        detalle = datos_ruta.get("message", "Error al procesar la ruta.")
        print(f"Error en la consulta: {detalle}")
        print("=" * 55)