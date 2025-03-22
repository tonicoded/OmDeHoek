function toggleFilterMenu() {
    document.getElementById("filter-categorieen").classList.toggle("hidden");
  }
  

function updateKmLabel() {
    const slider = document.getElementById("afstand");
    document.getElementById("km-label").innerText = slider.value;
  }
  
  function getLocation() {
    const btn = document.querySelector("button");
    btn.disabled = true;
    btn.innerText = "Laden...";
    document.getElementById("loader").classList.remove("hidden");
  
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(fetchPlaces, showError);
    } else {
      alert("Locatie wordt niet ondersteund.");
      resetLoading();
    }
  }
  
  function fetchPlaces(position) {
    const lat = position.coords.latitude;
    const lon = position.coords.longitude;
    const radius = parseInt(document.getElementById("afstand").value) * 1000;
    const kids = document.getElementById("kids_only").checked;
    const adult = document.getElementById("adult_only").checked;
  
    fetch("/api/get_places", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        lat: lat,
        lon: lon,
        radius: radius,
        filters: {
            categorieen: getGekozenCategorieen()
          }
          
      })
    })
      .then(res => res.json())
      .then(data => {
        toonResultaten(data);
        resetLoading();
      })
      .catch(err => {
        alert("Fout bij ophalen van locaties.");
        console.error(err);
        resetLoading();
      });
  }
  
  let alleResultaten = [];
  let huidigeIndex = 0;
  const batchGrootte = 10;
  
  function toonResultaten(data) {
    const container = document.getElementById("resultaten");
    container.innerHTML = "";
  
    if (data.length === 0) {
      container.innerHTML = "<p>Geen activiteiten gevonden binnen geselecteerde filters.</p>";
      return;
    }
  
    // Sorteer op afstand en reset index
    alleResultaten = data.sort((a, b) => a.afstand_km - b.afstand_km);
    huidigeIndex = 0;
  
    laadVolgendeBatch(); // toon eerste 10
  }
  function laadVolgendeBatch() {
    const container = document.getElementById("resultaten");
    const volgendeItems = alleResultaten.slice(huidigeIndex, huidigeIndex + batchGrootte);
  
    volgendeItems.forEach(p => {
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
  
    huidigeIndex += batchGrootte;
  }
  
  
  function toggleDarkMode() {
    document.body.classList.toggle("dark");
  }
  
  function showError(error) {
    alert("Kon locatie niet ophalen.");
    console.error(error);
    resetLoading();
  }
  function getGekozenCategorieen() {
    const checkboxes = document.querySelectorAll("#filter-categorieen input[type=checkbox]:checked");
    return Array.from(checkboxes).map(cb => cb.value);
  }
  
  function resetLoading() {
    const btn = document.querySelector("button");
    btn.disabled = false;
    btn.innerText = "📍 Zoek in de buurt";
    document.getElementById("loader").classList.add("hidden");
  }
  window.addEventListener("scroll", () => {
    if (
      window.innerHeight + window.scrollY >= document.body.offsetHeight - 100 &&
      huidigeIndex < alleResultaten.length
    ) {
      laadVolgendeBatch();
    }
  });
  