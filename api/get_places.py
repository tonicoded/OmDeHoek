from http.server import BaseHTTPRequestHandler
import json
import requests
from math import radians, sin, cos, sqrt, atan2

class handler(BaseHTTPRequestHandler):

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "content-type")
        self.end_headers()

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        body = json.loads(post_data)

        lat = body.get("lat")
        lon = body.get("lon")
        radius = body.get("radius", 5000)
        filters = body.get("filters", {})
        categorieen = filters.get("categorieen", [])

        categorie_map = {
            "museum": 'node["tourism"="museum"]',
            "zoo": 'node["tourism"="zoo"]',
            "theme_park": 'node["tourism"="theme_park"]',
            "attraction": 'node["tourism"="attraction"]',
            "artwork": 'node["tourism"="artwork"]',
            "gallery": 'node["tourism"="gallery"]',
            "viewpoint": 'node["tourism"="viewpoint"]',
            "picnic_site": 'node["tourism"="picnic_site"]',
            "park": 'node["leisure"="park"]',
            "playground": 'node["leisure"="playground"]',
            "sports_centre": 'node["leisure"="sports_centre"]',
            "fitness_centre": 'node["leisure"="fitness_centre"]',
            "garden": 'node["leisure"="garden"]',
            "nature_reserve": 'node["leisure"="nature_reserve"]',
            "cinema": 'node["amenity"="cinema"]',
            "theatre": 'node["amenity"="theatre"]',
            "restaurant": 'node["amenity"="restaurant"]',
            "cafe": 'node["amenity"="cafe"]',
            "bar": 'node["amenity"="bar"]',
            "toilets": 'node["amenity"="toilets"]',
            "drinking_water": 'node["amenity"="drinking_water"]',
            "charging_station": 'node["amenity"="charging_station"]',
            "pharmacy": 'node["amenity"="pharmacy"]',
            "parking": 'node["amenity"="parking"]',
            "atm": 'node["amenity"="atm"]',
            "mall": 'node["shop"="mall"]',
            "clothes": 'node["shop"="clothes"]',
            "supermarket": 'node["shop"="supermarket"]',
            "bus_stop": 'node["highway"="bus_stop"]',
            "station": 'node["railway"="station"]'
        }

        if categorieen:
            regels = "\n".join([
                categorie_map[c] for c in categorieen if c in categorie_map
            ])
        else:
            # Als er geen categorie is gekozen, pak alles
            regels = "\n".join(categorie_map.values())

        query = f"""
        [out:json];
        (
          {regels}
        )(around:{radius},{lat},{lon});
        out center;
        """

        response = requests.post(
            'https://overpass-api.de/api/interpreter',
            data=query.encode('utf-8'),
            headers={"Content-Type": "text/plain"}
        )

        elements = response.json().get("elements", [])
        results = []

        def bereken_afstand(lat1, lon1, lat2, lon2):
            R = 6371
            dlat = radians(lat2 - lat1)
            dlon = radians(lon2 - lon1)
            a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
            c = 2 * atan2(sqrt(a), sqrt(1 - a))
            return round(R * c, 1)

        for el in elements:
            tags = el.get("tags", {})
            name = tags.get("name", "Naam onbekend")
            if name == "Naam onbekend":
                continue

            place_type = (
                tags.get("tourism") or
                tags.get("leisure") or
                tags.get("amenity") or
                tags.get("shop") or
                tags.get("highway") or
                tags.get("railway") or
                "overig"
            ).lower()

            afstand_km = bereken_afstand(lat, lon, el.get("lat"), el.get("lon"))

            results.append({
                "name": name,
                "type": place_type,
                "lat": el.get("lat"),
                "lon": el.get("lon"),
                "afstand_km": afstand_km
            })

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(results).encode())
