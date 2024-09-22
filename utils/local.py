import requests
import math
import os

def get_coordinates_from_cep(cep, api_key):
    url = f"https://api.opencagedata.com/geocode/v1/json?q={cep},Brazil&key={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data['results']:
            latitude = data['results'][0]['geometry']['lat']
            longitude = data['results'][0]['geometry']['lng']
            return latitude, longitude
        else:
            print(f"Coordenadas não encontradas para o CEP: {cep}")
            return None
    else:
        print(f"Erro na requisição para o CEP: {cep}")
        return None

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Raio da Terra em km
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))

    return R * c

# def find_ceps_within_distance(ceps, api_key, reference_cep, max_distance_km):
#     cep_coordinates = {}

#     reference_coords = get_coordinates_from_cep(reference_cep, api_key)
#     if not reference_coords:
#         print(f"Coordenadas não encontradas para o CEP de referência: {reference_cep}")
#         return {}

#     ref_lat, ref_lon = reference_coords

#     for cep in ceps:
#         coords = get_coordinates_from_cep(cep, api_key)
#         if coords:
#             cep_coordinates[cep] = coords
#         else:
#             print(f"Coordenadas não encontradas para o CEP: {cep}")

#     filtered_ceps = {}
#     for cep, (lat, lon) in cep_coordinates.items():
#         distance = haversine(ref_lat, ref_lon, lat, lon)
#         if distance <= max_distance_km:
#             filtered_ceps[cep] = {"latitude": lat, "longitude": lon, "distance_km": distance}

#     return filtered_ceps

# ceps = [
#     "01001000", "29024530", "01003000", "01004000", "01005000",
#     "01006000", "01007000", "01008000", "01009000", "01010000"
# ]


def loadCeps(file_path):
    codes = {}
    with open(file_path, 'r', encoding='latin-1') as file:
        for line in file:
            if ' - ' in line:
                parts = line.strip().split(' - ')
                if len(parts) == 3:  
                    cep = parts[0].strip()
                    latitude = parts[1].strip()
                    longitude = parts[2].strip()
                    codes[cep] = (latitude, longitude)
    return codes

base_dir = os.path.dirname(os.path.abspath(__file__))
ceps = loadCeps(os.path.join(base_dir, 'ceps_bd.txt'))

api_key = "f3853bcd03d04d3cbd13ef68ef5f14ee"

reference_cep = "58407450"

max_distance_km = 50

filtered_ceps = {}

def get_cep_around(reference_cep, api_key):
    reference_coords = get_coordinates_from_cep('58407450', api_key)
    print(reference_coords)
    if not reference_coords:
        print(f"Coordenadas não encontradas para o CEP de referência: {reference_cep}")
        return {}

    ref_lat, ref_lon = reference_coords

    for cep, (lat, lon) in ceps.items():
        if lat != 'NULL' and lon != 'NULL':
            distance = haversine(ref_lat, ref_lon, float(lat), float(lon))
            if distance <= max_distance_km:
                filtered_ceps[cep] = {"latitude": lat, "longitude": lon, "distance_km": distance}

get_cep_around(reference_cep, api_key)
for cep in filtered_ceps.keys():  
    print(cep)
    
# filtered_ceps = find_ceps_within_distance(ceps, api_key, reference_cep, max_distance_km)

# print(f"CEPs dentro de {max_distance_km} km do CEP {reference_cep}:")
# for cep, details in filtered_ceps.items():
#     print(f"CEP: {cep}, Latitude: {details['latitude']}, Longitude: {details['longitude']}, Distância: {details['distance_km']:.2f} km")
