import urllib.parse
import requests

route_url = "https://graphhopper.com/api/1/route?"

# API Key de Graphhopper
key = "853f8b91-bab8-4b53-9324-c3c80f5a5db5"


def geocoding(location, key):
    while location == "":
        location = input("Por favor, ingrese una ubicación válida: ").strip()

    geocode_url = "https://graphhopper.com/api/1/geocode?"
    # Se agrega locale=es para que la información geográfica retorne en español
    url = geocode_url + urllib.parse.urlencode(
        {"q": location, "limit": "1", "key": key, "locale": "es"}
    )

    replydata = requests.get(url)
    json_data = replydata.json()
    json_status = replydata.status_code

    if json_status == 200 and len(json_data.get("hits", [])) != 0:
        lat = json_data["hits"][0]["point"]["lat"]
        lng = json_data["hits"][0]["point"]["lng"]
        name = json_data["hits"][0]["name"]
        value = json_data["hits"][0].get("osm_value", "ciudad")
        country = json_data["hits"][0].get("country", "")
        state = json_data["hits"][0].get("state", "")

        if len(state) != 0 and len(country) != 0:
            new_loc = f"{name}, {state}, {country}"
        elif len(country) != 0:
            new_loc = f"{name}, {country}"
        else:
            new_loc = name

        print(
            f"URL de Geocodificación para {new_loc} (Tipo: {value}):\n{url}"
        )
    else:
        lat = "null"
        lng = "null"
        new_loc = location
        if json_status != 200:
            print(
                f"Estado Geocode API: {json_status}\nMensaje de error: {json_data.get('message', 'Desconocido')}"
            )
        else:
            print(
                f"No se encontraron resultados para la ubicación: {location}"
            )

    return json_status, lat, lng, new_loc


while True:
    print("\n" + "+" * 50)
    print("Perfiles de vehículos disponibles en Graphhopper:")
    print("+" * 50)
    print("auto (car), bicicleta (bike), a pie (foot)")
    print("+" * 50)

    perfiles = {
        "auto": "car",
        "car": "car",
        "bicicleta": "bike",
        "bike": "bike",
        "a pie": "foot",
        "pie": "foot",
        "foot": "foot",
    }

    vehiculo_input = (
        input("Ingrese el perfil de transporte deseado: ").strip().lower()
    )

    if vehiculo_input in ["s", "salir", "q", "quit"]:
        print(
            "¡Gracias por utilizar el sistema de geolocalización! Finalizando programa..."
        )
        break

    if vehiculo_input in perfiles:
        vehicle = perfiles[vehiculo_input]
    else:
        vehicle = "car"
        print(
            "Perfil no válido o no ingresado. Se usará el perfil por defecto: auto (car)."
        )

    loc1 = input("Ubicación de partida (o 's' / 'salir'): ").strip()
    if loc1.lower() in ["s", "salir", "q", "quit"]:
        print("Programa cancelado por el usuario.")
        break
    orig = geocoding(loc1, key)

    loc2 = input("Ubicación de destino (o 's' / 'salir'): ").strip()
    if loc2.lower() in ["s", "salir", "q", "quit"]:
        print("Programa cancelado por el usuario.")
        break
    dest = geocoding(loc2, key)

    print("=" * 60)
    if (
        orig[0] == 200
        and dest[0] == 200
        and orig[1] != "null"
        and dest[1] != "null"
    ):
        op = f"&point={orig[1]}%2C{orig[2]}"
        dp = f"&point={dest[1]}%2C{dest[2]}"

        # Se incluye locale=es para obtener instrucciones en español
        paths_url = (
            route_url
            + urllib.parse.urlencode(
                {"key": key, "vehicle": vehicle, "locale": "es"}
            )
            + op
            + dp
        )
        paths_response = requests.get(paths_url)
        paths_status = paths_response.status_code
        paths_data = paths_response.json()

        print(f"Estado de la API de Ruta: {paths_status}")
        print(f"URL de la API de Ruta:\n{paths_url}")
        print("=" * 60)
        print(f"Ruta desde {orig[3]} hacia {dest[3]} en {vehicle}")
        print("=" * 60)

        if paths_status == 200:
            distancia_metros = paths_data["paths"][0]["distance"]
            tiempo_milisegundos = paths_data["paths"][0]["time"]

            km = distancia_metros / 1000.0
            millas = km / 1.60934

            seg = int((tiempo_milisegundos / 1000) % 60)
            minutos = int((tiempo_milisegundos / 1000 / 60) % 60)
            horas = int(tiempo_milisegundos / 1000 / 60 / 60)

            print(f"Distancia recorrida: {millas:.2f} millas / {km:.2f} km")
            print(
                f"Duración estimada del viaje: {horas:02d}:{minutos:02d}:{seg:02d}"
            )
            print("=" * 60)
            print("Instrucciones paso a paso del viaje (Español):")
            print("=" * 60)

            instrucciones = paths_data["paths"][0]["instructions"]
            for paso in instrucciones:
                texto_guia = paso["text"]
                dist_paso = paso["distance"]
                km_paso = dist_paso / 1000.0
                mi_paso = km_paso / 1.60934
                print(
                    f"- {texto_guia} ({km_paso:.2f} km / {mi_paso:.2f} millas)"
                )

            print("=" * 60)
        else:
            print(
                f"Error en el cálculo de la ruta: {paths_data.get('message', 'Sin conexión directa')}"
            )
            print("*" * 60)