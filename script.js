function updateKmLabel() {
    const slider = document.getElementById("afstand");
    document.getElementById("km-label").innerText = slider.value;
}

function getLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(fetchPlaces, showError);
    } else {
        alert("Locatie wordt niet ondersteund.");
    }
}

function fetchPlaces(position) {
    const lat = position.coords.latitude;
    const lon = position.coords.longitude;
    const radius = parseInt(document.getElementById("afstand").value) * 1000;
    const kids = document.getElementById("kids_only").checked;
    const adult = document.getElementById("adult_only").checked;

    // Gebruik hier jouw externe IP + poort 8000
    fetch("/api/get_places", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            lat: lat,
            lon: lon,
            radius: radius,
            filters: {
                kids_only: kids,
                adult_only: adult
            }
        })
    })
    .then(res => res.json())
    .then(data => toonResultaten(data))
    .catch(err => {
        alert("Fout bij ophalen van locaties.");
        console.error(err);
    });
}

function toonResultaten(data) {
    const container = document.getElementById("resultaten");
    container.innerHTML = "";
  
    if (data.length === 0) {
      container.innerHTML = "<p>Geen activiteiten gevonden binnen geselecteerde filters.</p>";
      return;
    }
  
    // Sorteer op afstand oplopend
    data.sort((a, b) => a.afstand_km - b.afstand_km);
  
    data.forEach(p => {
      const kaartLink = `https://www.google.com/maps?q=${p.lat},${p.lon}&z=16&output=embed`;
  
      const div = document.createElement("div");
      div.className = "kaart";
  
      div.innerHTML = `
        <iframe
          src="${kaartLink}"
          width="100%" height="200" style="border:0; border-radius:12px;"
          allowfullscreen="" loading="lazy">
        </iframe>
        <div class="inhoud">
          <h3>${p.name}</h3>
          <p>🧭 Type: ${p.type} • 📍 ${p.afstand_km} km</p>
          <a href="https://www.google.com/maps/search/?api=1&query=${p.lat},${p.lon}" target="_blank">🗺️ Route</a>
        </div>
      `;
  
      container.appendChild(div);
    });
  }
  

function showError(error) {
    alert("Kon locatie niet ophalen.");
    console.error(error);
}
