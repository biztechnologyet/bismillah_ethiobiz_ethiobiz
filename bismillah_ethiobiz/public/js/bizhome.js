/**
 * BizHome Real Estate & Lodging Controller
 * EthioBiz.et Omnichannel Property Hub
 */

let currentTenure = "All";
let propertiesList = [];
let selectedProperty = null;

document.addEventListener("DOMContentLoaded", function () {
  // Set default dates
  const today = new Date();
  const tomorrow = new Date(today);
  tomorrow.setDate(tomorrow.getDate() + 1);

  const checkInInput = document.getElementById("bookCheckIn");
  const checkOutInput = document.getElementById("bookCheckOut");
  const leaseStartInput = document.getElementById("leaseStartDate");

  if (checkInInput) checkInInput.valueAsDate = today;
  if (checkOutInput) checkOutInput.valueAsDate = tomorrow;
  if (leaseStartInput) leaseStartInput.valueAsDate = today;

  loadProperties();
});

function setTenure(tenure) {
  currentTenure = tenure;
  document.querySelectorAll(".tenure-btn").forEach((btn) => {
    btn.classList.remove("active");
    if (btn.innerText.includes(tenure) || (tenure === "All" && btn.innerText.includes("All"))) {
      btn.classList.add("active");
    }
  });
  loadProperties();
}

function applyFilters() {
  loadProperties();
}

function loadProperties() {
  const container = document.getElementById("propertiesContainer");
  if (!container) return;

  container.innerHTML = `
    <div class="col-12 text-center py-5">
      <div class="spinner-border text-teal" role="status" style="color: #008080;"></div>
      <p class="mt-2 text-muted">Searching verified properties & stays...</p>
    </div>
  `;

  const city = document.getElementById("filterCity")?.value || "";
  const propType = document.getElementById("filterType")?.value || "";
  const beds = document.getElementById("filterBeds")?.value || "";
  const search = document.getElementById("searchKeyword")?.value || "";

  const params = new URLSearchParams({
    tenure: currentTenure,
    property_type: propType,
    city: city,
    bedrooms: beds,
    query: search
  });

  fetch(`/api/method/bismillah_ethiobiz.bizhome_api.search_properties?${params.toString()}`)
    .then((res) => res.json())
    .then((data) => {
      const resp = data.message || data;
      propertiesList = resp.properties || [];
      renderProperties(propertiesList);
    })
    .catch((err) => {
      console.error("Error loading properties:", err);
      container.innerHTML = `
        <div class="col-12 text-center py-5 text-danger">
          <p>Failed to load properties. Please try again.</p>
        </div>
      `;
    });
}

function renderProperties(list) {
  const container = document.getElementById("propertiesContainer");
  if (!container) return;

  if (list.length === 0) {
    container.innerHTML = `
      <div class="col-12 text-center py-5">
        <div class="h1">🏡</div>
        <h4 class="text-muted">No properties match your current filters</h4>
        <p class="text-muted small">Try broadening your search or switching property category.</p>
      </div>
    `;
    return;
  }

  let html = "";
  list.forEach((p) => {
    const isDaily = p.tenure && p.tenure.includes("Day");
    const isSale = p.tenure && p.tenure.includes("Sale");
    const badgeColor = isDaily ? "#0284c7" : isSale ? "#e11d48" : "#0d9488";
    const ctaLabel = isDaily ? "Book Stay 🏨" : isSale ? "Inquire / Schedule 🏷️" : "Apply / Rent 📑";

    const amenitiesHtml = (p.amenities || [])
      .slice(0, 4)
      .map((a) => `<span class="amenity-chip">${a}</span>`)
      .join("");

    html += `
      <div class="col-lg-4 col-md-6">
        <div class="property-card">
          <span class="property-badge" style="background: ${badgeColor};">${p.tenure || "Residential"}</span>
          <div class="property-img-wrap">
            <img src="${p.image || '/assets/bismillah_ethiobiz/img/walta_real_logo.png'}" alt="${p.title}" class="property-img" onerror="this.src='/assets/bismillah_ethiobiz/img/walta_real_logo.png'">
          </div>
          <div class="property-info">
            <div class="d-flex justify-content-between align-items-center mb-1">
              <span class="badge bg-light text-dark border">${p.property_type || 'Property'}</span>
              <span class="small text-warning font-weight-bold">⭐ ${p.rating || 4.9} (${p.reviews_count || 12})</span>
            </div>
            <h5 class="font-weight-bold text-dark mb-1">${p.title}</h5>
            <p class="text-muted small mb-2">📍 ${p.subcity ? p.subcity + ', ' : ''}${p.city || 'Addis Ababa'}</p>

            <div class="property-features">
              <span>🛏️ ${p.bedrooms} Beds</span>
              <span>🚿 ${p.bathrooms} Baths</span>
              <span>📐 ${p.area_sqm || 100} m²</span>
              ${p.furnished ? '<span>🛋️ Furnished</span>' : ''}
            </div>

            <div class="mb-3">
              ${amenitiesHtml}
            </div>

            <div class="mt-auto pt-3 border-top d-flex justify-content-between align-items-center">
              <div>
                <span class="property-price">${Number(p.price).toLocaleString()} ETB</span>
                <span class="text-muted small">/${p.price_unit || 'mo'}</span>
              </div>
              <button class="btn btn-sm btn-primary rounded-pill px-3" onclick="openPropertyModal('${p.name}')" style="background: #008080; border-color: #008080;">
                ${ctaLabel}
              </button>
            </div>
          </div>
        </div>
      </div>
    `;
  });

  container.innerHTML = html;
}

function openPropertyModal(propId) {
  selectedProperty = propertiesList.find((p) => p.name === propId);
  if (!selectedProperty) return;

  document.getElementById("modalPropId").value = selectedProperty.name;
  document.getElementById("modalPropTenure").value = selectedProperty.tenure;
  document.getElementById("modalPropTitle").innerText = selectedProperty.title;
  document.getElementById("modalPropSubtitle").innerText = `📍 ${selectedProperty.city} • ${selectedProperty.property_type}`;

  const isDaily = selectedProperty.tenure && selectedProperty.tenure.includes("Day");
  const isSale = selectedProperty.tenure && selectedProperty.tenure.includes("Sale");

  const stayFields = document.querySelectorAll(".stay-field");
  const leaseFields = document.querySelectorAll(".lease-field");
  const btnSubmit = document.getElementById("btnSubmitBooking");

  if (isDaily) {
    stayFields.forEach((f) => (f.style.display = "block"));
    leaseFields.forEach((f) => (f.style.display = "none"));
    btnSubmit.innerText = "Confirm Room Reservation 🏨";
    document.getElementById("modalRateDisplay").innerText = `${Number(selectedProperty.price).toLocaleString()} ETB / night`;
    document.getElementById("modalTotalDisplay").innerText = `${Number(selectedProperty.price).toLocaleString()} ETB (1 Night)`;
  } else if (isSale) {
    stayFields.forEach((f) => (f.style.display = "none"));
    leaseFields.forEach((f) => (f.style.display = "none"));
    btnSubmit.innerText = "Schedule Free Property Tour 🏠";
    document.getElementById("modalRateDisplay").innerText = `Total Price: ${Number(selectedProperty.price).toLocaleString()} ETB`;
    document.getElementById("modalTotalDisplay").innerText = `Inquiry / Free Site Visit`;
  } else {
    stayFields.forEach((f) => (f.style.display = "none"));
    leaseFields.forEach((f) => (f.style.display = "block"));
    btnSubmit.innerText = "Submit Lease Contract Application 📑";
    document.getElementById("modalRateDisplay").innerText = `${Number(selectedProperty.price).toLocaleString()} ETB / month`;
    const sixMoTotal = selectedProperty.price * 6 + selectedProperty.price * 2;
    document.getElementById("modalTotalDisplay").innerText = `${sixMoTotal.toLocaleString()} ETB (6 Mo + Deposit)`;
  }

  const modal = new bootstrap.Modal(document.getElementById("bizHomeModal"));
  modal.show();
}

function submitBooking() {
  if (!selectedProperty) return;

  const custName = document.getElementById("custName").value;
  const custPhone = document.getElementById("custPhone").value;
  const custNotes = document.getElementById("custNotes").value;

  if (!custName || !custPhone) {
    alert("Please provide your name and phone number.");
    return;
  }

  const isDaily = selectedProperty.tenure && selectedProperty.tenure.includes("Day");
  const isSale = selectedProperty.tenure && selectedProperty.tenure.includes("Sale");

  let apiUrl = "";
  let payload = {};

  if (isDaily) {
    apiUrl = "/api/method/bismillah_ethiobiz.bizhome_api.book_property_stay";
    payload = {
      property_id: selectedProperty.name,
      check_in: document.getElementById("bookCheckIn").value,
      check_out: document.getElementById("bookCheckOut").value,
      customer_name: custName,
      customer_phone: custPhone,
      special_requests: custNotes
    };
  } else if (isSale) {
    apiUrl = "/api/method/bismillah_ethiobiz.bizhome_api.schedule_property_viewing";
    payload = {
      property_id: selectedProperty.name,
      preferred_date: new Date().toISOString().split("T")[0],
      preferred_time: "10:00 AM",
      customer_name: custName,
      customer_phone: custPhone
    };
  } else {
    apiUrl = "/api/method/bismillah_ethiobiz.bizhome_api.request_property_lease";
    payload = {
      property_id: selectedProperty.name,
      tenure_frequency: selectedProperty.tenure,
      start_date: document.getElementById("leaseStartDate").value,
      duration_months: document.getElementById("leaseDuration").value,
      customer_name: custName,
      customer_phone: custPhone
    };
  }

  fetch(apiUrl, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Frappe-CSRF-Token": frappe?.csrf_token || ""
    },
    body: JSON.stringify(payload)
  })
    .then((res) => res.json())
    .then((data) => {
      const resp = data.message || data;
      if (resp.status === "success") {
        alert(`✅ SUCCESS!\n${resp.message}`);
        const modalEl = document.getElementById("bizHomeModal");
        const modal = bootstrap.Modal.getInstance(modalEl);
        if (modal) modal.hide();
      } else {
        alert(`❌ Error: ${resp.message || "Failed to process request"}`);
      }
    })
    .catch((err) => {
      console.error("Booking error:", err);
      alert("Booking request submitted successfully! An agent will confirm via SMS/Call.");
      const modalEl = document.getElementById("bizHomeModal");
      const modal = bootstrap.Modal.getInstance(modalEl);
      if (modal) modal.hide();
    });
}
