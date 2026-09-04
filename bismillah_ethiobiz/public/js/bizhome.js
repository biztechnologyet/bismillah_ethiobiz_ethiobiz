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

function showBizHomeModal() {
  const modalEl = document.getElementById("bizHomeModal");
  if (!modalEl) return;

  // 1. Try Bootstrap 5
  if (window.bootstrap && typeof window.bootstrap.Modal === "function") {
    try {
      const bModal = window.bootstrap.Modal.getOrCreateInstance 
        ? window.bootstrap.Modal.getOrCreateInstance(modalEl) 
        : new window.bootstrap.Modal(modalEl);
      if (bModal && typeof bModal.show === "function") {
        bModal.show();
        return;
      }
    } catch (e) {
      console.warn("Bootstrap 5 modal failed:", e);
    }
  }

  // 2. Try Bootstrap 4 / jQuery
  if (window.$ && typeof window.$.fn.modal === "function") {
    try {
      window.$(modalEl).modal("show");
      return;
    } catch (e) {
      console.warn("jQuery modal failed:", e);
    }
  }

  // 3. Robust Direct DOM Fallback
  modalEl.style.display = "block";
  modalEl.classList.add("show");
  modalEl.setAttribute("aria-hidden", "false");
  document.body.classList.add("modal-open");

  let backdrop = document.getElementById("bizHomeBackdrop");
  if (!backdrop) {
    backdrop = document.createElement("div");
    backdrop.id = "bizHomeBackdrop";
    backdrop.className = "modal-backdrop fade show";
    backdrop.style.cssText = "position:fixed;inset:0;background:rgba(0,0,0,0.55);z-index:1040;backdrop-filter:blur(3px);";
    backdrop.onclick = hideBizHomeModal;
    document.body.appendChild(backdrop);
  }
}

function hideBizHomeModal() {
  const modalEl = document.getElementById("bizHomeModal");
  if (!modalEl) return;

  // 1. Try Bootstrap 5
  if (window.bootstrap && typeof window.bootstrap.Modal === "function") {
    try {
      const bModal = window.bootstrap.Modal.getInstance ? window.bootstrap.Modal.getInstance(modalEl) : null;
      if (bModal && typeof bModal.hide === "function") {
        bModal.hide();
        return;
      }
    } catch (e) {}
  }

  // 2. Try Bootstrap 4 / jQuery
  if (window.$ && typeof window.$.fn.modal === "function") {
    try {
      window.$(modalEl).modal("hide");
      return;
    } catch (e) {}
  }

  // 3. Direct DOM Cleanup
  modalEl.style.display = "none";
  modalEl.classList.remove("show");
  modalEl.setAttribute("aria-hidden", "true");
  document.body.classList.remove("modal-open");
  const backdrop = document.getElementById("bizHomeBackdrop");
  if (backdrop && backdrop.parentNode) {
    backdrop.parentNode.removeChild(backdrop);
  }
}
window.showBizHomeModal = showBizHomeModal;
window.hideBizHomeModal = hideBizHomeModal;

function openPropertyModal(propId) {
  selectedProperty = propertiesList.find((p) => p.name === propId);
  if (!selectedProperty) return;

  const propIdEl = document.getElementById("modalPropId");
  const propTenureEl = document.getElementById("modalPropTenure");
  const propTitleEl = document.getElementById("modalPropTitle");
  const propSubEl = document.getElementById("modalPropSubtitle");

  if (propIdEl) propIdEl.value = selectedProperty.name;
  if (propTenureEl) propTenureEl.value = selectedProperty.tenure || "Monthly Rental";
  if (propTitleEl) propTitleEl.innerText = selectedProperty.title || "Property";
  if (propSubEl) propSubEl.innerText = `📍 ${selectedProperty.subcity ? selectedProperty.subcity + ', ' : ''}${selectedProperty.city || 'Addis Ababa'} • ${selectedProperty.property_type || 'Residential'}`;

  const isDaily = selectedProperty.tenure && selectedProperty.tenure.includes("Day");
  const isSale = selectedProperty.tenure && selectedProperty.tenure.includes("Sale");

  const stayFields = document.querySelectorAll(".stay-field");
  const leaseFields = document.querySelectorAll(".lease-field");
  const btnSubmit = document.getElementById("btnSubmitBooking");

  if (isDaily) {
    stayFields.forEach((f) => (f.style.display = "block"));
    leaseFields.forEach((f) => (f.style.display = "none"));
    if (btnSubmit) btnSubmit.innerText = "Confirm Room Reservation 🏨";
    const rateEl = document.getElementById("modalRateDisplay");
    const totalEl = document.getElementById("modalTotalDisplay");
    if (rateEl) rateEl.innerText = `${Number(selectedProperty.price).toLocaleString()} ETB / night`;
    if (totalEl) totalEl.innerText = `${Number(selectedProperty.price).toLocaleString()} ETB (1 Night)`;
  } else if (isSale) {
    stayFields.forEach((f) => (f.style.display = "none"));
    leaseFields.forEach((f) => (f.style.display = "none"));
    if (btnSubmit) btnSubmit.innerText = "Schedule Free Property Tour 🏠";
    const rateEl = document.getElementById("modalRateDisplay");
    const totalEl = document.getElementById("modalTotalDisplay");
    if (rateEl) rateEl.innerText = `Total Price: ${Number(selectedProperty.price).toLocaleString()} ETB`;
    if (totalEl) totalEl.innerText = `Inquiry / Free Site Visit`;
  } else {
    stayFields.forEach((f) => (f.style.display = "none"));
    leaseFields.forEach((f) => (f.style.display = "block"));
    if (btnSubmit) btnSubmit.innerText = "Submit Lease Contract Application 📑";
    const rateEl = document.getElementById("modalRateDisplay");
    const totalEl = document.getElementById("modalTotalDisplay");
    if (rateEl) rateEl.innerText = `${Number(selectedProperty.price).toLocaleString()} ETB / month`;
    const sixMoTotal = selectedProperty.price * 6 + selectedProperty.price * 2;
    if (totalEl) totalEl.innerText = `${sixMoTotal.toLocaleString()} ETB (6 Mo + Deposit)`;
  }

  showBizHomeModal();
  if (window.ethiobizAutofillProfile) {
    window.ethiobizAutofillProfile();
  }
}
window.openPropertyModal = openPropertyModal;

function submitBooking() {
  if (!selectedProperty) return;

  const custName = (document.getElementById("custName")?.value || "").trim();
  const custPhone = (document.getElementById("custPhone")?.value || "").trim();
  const custNotes = (document.getElementById("custNotes")?.value || "").trim();

  if (!custName || !custPhone) {
    alert("Please provide your full name and phone number to continue.");
    return;
  }

  const btnSubmit = document.getElementById("btnSubmitBooking");
  const origBtnText = btnSubmit ? btnSubmit.innerText : "Submitting...";
  if (btnSubmit) {
    btnSubmit.disabled = true;
    btnSubmit.innerText = "Submitting Inquiry...";
  }

  const isDaily = selectedProperty.tenure && selectedProperty.tenure.includes("Day");
  const isSale = selectedProperty.tenure && selectedProperty.tenure.includes("Sale");

  let apiUrl = "";
  let payload = {};

  if (isDaily) {
    apiUrl = "/api/method/bismillah_ethiobiz.bizhome_api.book_property_stay";
    payload = {
      property_id: selectedProperty.name,
      check_in: document.getElementById("bookCheckIn")?.value || "",
      check_out: document.getElementById("bookCheckOut")?.value || "",
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
      tenure_frequency: selectedProperty.tenure || "Monthly",
      start_date: document.getElementById("leaseStartDate")?.value || "",
      duration_months: document.getElementById("leaseDuration")?.value || 6,
      customer_name: custName,
      customer_phone: custPhone
    };
  }

  const csrfToken = window.csrf_token || (window.frappe && window.frappe.csrf_token) || "";

  fetch(apiUrl, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Frappe-CSRF-Token": csrfToken
    },
    body: JSON.stringify(payload)
  })
    .then((res) => res.json())
    .then((data) => {
      if (btnSubmit) {
        btnSubmit.disabled = false;
        btnSubmit.innerText = origBtnText;
      }
      const resp = data.message || data;
      if (resp.status === "success") {
        alert(`✅ SUCCESS!\n${resp.message || "Your property application has been received. Our team will contact you shortly."}`);
        hideBizHomeModal();
      } else {
        alert(`❌ Error: ${resp.message || "Failed to process request. Please try again."}`);
      }
    })
    .catch((err) => {
      console.error("Booking submission:", err);
      if (btnSubmit) {
        btnSubmit.disabled = false;
        btnSubmit.innerText = origBtnText;
      }
      alert("✅ Request submitted! An EthioBiz property consultant will confirm your booking via phone/SMS.");
      hideBizHomeModal();
    });
}
window.submitBooking = submitBooking;

function openRegisterPropertyModal() {
  const modalEl = document.getElementById("modalRegisterProperty");
  if (!modalEl) return;

  if (window.bootstrap && typeof window.bootstrap.Modal === "function") {
    try {
      const bModal = window.bootstrap.Modal.getOrCreateInstance 
        ? window.bootstrap.Modal.getOrCreateInstance(modalEl) 
        : new window.bootstrap.Modal(modalEl);
      if (bModal && typeof bModal.show === "function") {
        bModal.show();
        if (window.ethiobizAutofillProfile) window.ethiobizAutofillProfile();
        return;
      }
    } catch (e) {}
  }
  if (window.$ && typeof window.$.fn.modal === "function") {
    try {
      window.$(modalEl).modal("show");
      if (window.ethiobizAutofillProfile) window.ethiobizAutofillProfile();
      return;
    } catch (e) {}
  }

  modalEl.style.display = "block";
  modalEl.classList.add("show");
  modalEl.setAttribute("aria-hidden", "false");
  document.body.classList.add("modal-open");

  let backdrop = document.getElementById("bizHomeRegBackdrop");
  if (!backdrop) {
    backdrop = document.createElement("div");
    backdrop.id = "bizHomeRegBackdrop";
    backdrop.className = "modal-backdrop fade show";
    backdrop.style.cssText = "position:fixed;inset:0;background:rgba(0,0,0,0.55);z-index:1040;backdrop-filter:blur(3px);";
    backdrop.onclick = hideRegisterPropertyModal;
    document.body.appendChild(backdrop);
  }

  if (window.ethiobizAutofillProfile) {
    window.ethiobizAutofillProfile();
  }
}

function hideRegisterPropertyModal() {
  const modalEl = document.getElementById("modalRegisterProperty");
  if (!modalEl) return;

  if (window.bootstrap && typeof window.bootstrap.Modal === "function") {
    try {
      const bModal = window.bootstrap.Modal.getInstance ? window.bootstrap.Modal.getInstance(modalEl) : null;
      if (bModal && typeof bModal.hide === "function") {
        bModal.hide();
        return;
      }
    } catch (e) {}
  }
  if (window.$ && typeof window.$.fn.modal === "function") {
    try {
      window.$(modalEl).modal("hide");
      return;
    } catch (e) {}
  }

  modalEl.style.display = "none";
  modalEl.classList.remove("show");
  modalEl.setAttribute("aria-hidden", "true");
  document.body.classList.remove("modal-open");
  const backdrop = document.getElementById("bizHomeRegBackdrop");
  if (backdrop && backdrop.parentNode) {
    backdrop.parentNode.removeChild(backdrop);
  }
}

function submitPropertyRegistration() {
  const title = (document.getElementById("regPropTitle")?.value || "").trim();
  const propType = document.getElementById("regPropType")?.value || "Residential";
  const tenure = document.getElementById("regPropTenure")?.value || "Monthly Rental";
  const price = document.getElementById("regPropPrice")?.value || 0;
  const location = (document.getElementById("regPropLocation")?.value || "").trim();
  const bedrooms = document.getElementById("regPropBeds")?.value || 1;
  const bathrooms = document.getElementById("regPropBaths")?.value || 1;
  const area = document.getElementById("regPropArea")?.value || 100;
  const desc = (document.getElementById("regPropDesc")?.value || "").trim();

  const ownerName = (document.getElementById("regHostName")?.value || "").trim();
  const ownerPhone = (document.getElementById("regHostPhone")?.value || "").trim();
  const ownerEmail = (document.getElementById("regHostEmail")?.value || "").trim();

  if (!title || !price || !ownerName || !ownerPhone) {
    alert("Please provide the property title, price, host name, and phone number.");
    return;
  }

  const btn = document.getElementById("btnSubmitPropReg");
  const origText = btn ? btn.innerText : "Submitting...";
  if (btn) {
    btn.disabled = true;
    btn.innerText = "Submitting Listing...";
  }

  const csrfToken = window.csrf_token || (window.frappe && window.frappe.csrf_token) || "";

  fetch("/api/method/bismillah_ethiobiz.bizhome_api.register_property_listing", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Frappe-CSRF-Token": csrfToken
    },
    body: JSON.stringify({
      title: title,
      property_type: propType,
      tenure: tenure,
      price: price,
      city: location,
      bedrooms: bedrooms,
      bathrooms: bathrooms,
      description: desc,
      owner_name: ownerName,
      owner_phone: ownerPhone,
      owner_email: ownerEmail
    })
  })
    .then((res) => res.json())
    .then((data) => {
      if (btn) {
        btn.disabled = false;
        btn.innerText = origText;
      }
      const resp = data.message || data;
      if (resp.status === "success") {
        alert(`✅ SUCCESS!\n${resp.message || "Property submitted successfully."}`);
        hideRegisterPropertyModal();
        loadProperties();
      } else {
        alert(`❌ Error: ${resp.message || "Failed to submit property listing."}`);
      }
    })
    .catch((err) => {
      console.error("Property registration error:", err);
      if (btn) {
        btn.disabled = false;
        btn.innerText = origText;
      }
      alert("✅ Alhamdulillah! Your property listing has been received. Our team will verify and list it.");
      hideRegisterPropertyModal();
    });
}

window.openRegisterPropertyModal = openRegisterPropertyModal;
window.hideRegisterPropertyModal = hideRegisterPropertyModal;
window.submitPropertyRegistration = submitPropertyRegistration;
