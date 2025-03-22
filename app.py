from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get_places', methods=['POST'])
def get_places():
    data = request.get_json()
    lat = data['lat']
    lon = data['lon']
    radius = data.get('radius', 5000)
    filters = data.get('filters', {})

    query = f"""
    [out:json];
    (
      node["tourism"~"museum|zoo|theme_park|attraction"](around:{radius},{lat},{lon});
      node["leisure"~"park|playground"](around:{radius},{lat},{lon});
      node["amenity"~"theatre|cinema"](around:{radius},{lat},{lon});
    );
    out center;
    """

    response = requests.post(
        'https://overpass-api.de/api/interpreter',
        data=query.encode('utf-8'),
        headers={"Content-Type": "text/plain"}
    )

    all_places = response.json().get("elements", [])
    results = []

    for el in all_places:
        tags = el.get("tags", {})
        name = tags.get("name", "Naam onbekend")
        if name == "Naam onbekend":
            continue  # skip lege namen

        place_type = (
            tags.get("tourism") or
            tags.get("leisure") or
            tags.get("amenity") or
            "overig"
        ).lower()

        # Slimme filtering
        name_lc = name.lower()
        is_kids = any(k in name_lc for k in ["zoo", "kinder", "familie", "theme", "playground", "dieren", "speeltuin"])
        is_adult = any(a in name_lc for a in ["erotic", "sex", "strip", "club", "casino", "redlight"])

        if filters.get("kids_only") and not is_kids:
            continue
        if filters.get("adult_only") and not is_adult:
            continue

        # Unsplash image URL (random afbeelding per naam)
        zoekterm = name.replace(" ", "+").strip()
        if not zoekterm:
         zoekterm = "landscape"

        # sig=random zorgt voor variatie, voorkomt caching
        image = f"https://source.unsplash.com/400x200/?{zoekterm}&sig={abs(hash(name)) % 1000}"


        results.append({
           "name": name,
           "type": place_type,
           "lat": el.get("lat"),
           "lon": el.get("lon"),
           "image": image
})


    return jsonify(results)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
