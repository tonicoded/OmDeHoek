from http.server import BaseHTTPRequestHandler
import json
import urllib.parse
import requests
import re
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

        query = f"""
        [out:json];
        (
           node["tourism"~"museum|zoo|theme_park|attraction|artwork|gallery|viewpoint"](around:{radius},{lat},{lon});
           node["leisure"~"park|playground|sports_centre|fitness_centre|garden"](around:{radius},{lat},{lon});
           node["amenity"~"theatre|cinema|restaurant|cafe|bar"](around:{radius},{lat},{lon});
           node["shop"~"mall|clothes|supermarket"](around:{radius},{lat},{lon});
        );
        out center;
        """


        response = requests.post(
            'https://overpass-api.de/api/interpreter',
            data=query.encode('utf-8'),
            headers={"Content-Type": "text/plain"}
        )

        elements = response.json().get("elements", [])
        results = []

        for el in elements:
            afstand_km = bereken_afstand(lat, lon, el.get("lat"), el.get("lon"))
            tags = el.get("tags", {})
            name = tags.get("name", "Naam onbekend")
            if name == "Naam onbekend":
                continue

            place_type = (
                tags.get("tourism") or
                tags.get("leisure") or
                tags.get("amenity") or
                "overig"
            ).lower()

            name_lc = name.lower()
            is_kids = any(k in name_lc for k in ["zoo", "kinder", "familie", "theme", "playground", "dieren", "speeltuin"])
            is_adult = any(a in name_lc for a in ["erotic", "sex", "strip", "club", "casino", "redlight"])

            if filters.get("kids_only") and not is_kids:
                continue
            if filters.get("adult_only") and not is_adult:
                continue

            zoekterm = re.sub(r"[^\w\s]", "", name).strip()
            zoekterm = "+".join(zoekterm.split())

            if not zoekterm or len(zoekterm) < 3:
              zoekterm = f"{place_type}+landscape"


            image = f"https://source.unsplash.com/400x200/?{zoekterm}&sig={abs(hash(name)) % 1000}"

            results.append({
                "name": name,
                "type": place_type,
                "lat": el.get("lat"),
                "lon": el.get("lon"),
                "image": image,
                "afstand_km": afstand_km
            })

        def bereken_afstand(lat1, lon1, lat2, lon2):
          R = 6371  # Aarde straal in km
          dlat = radians(lat2 - lat1)
          dlon = radians(lon2 - lon1)
          a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
          c = 2 * atan2(sqrt(a), sqrt(1 - a))
          afstand = R * c
          return round(afstand, 1)  # bijv. 3.4 km


        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(results).encode())
