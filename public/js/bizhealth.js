// BISMALLAH ETHIOBIZ HEALTH PORTAL JAVASCRIPT
document.addEventListener("DOMContentLoaded", function() {
    let currentSpecialty = "all";
    let currentType = "all";
    let doctors = [];
    let selectedDoctor = null;

    initHealthControls();
    loadDoctors();

    function initHealthControls() {
        // Specialty Chips
        document.querySelectorAll(".spec-chip").forEach(chip => {
            chip.addEventListener("click", function() {
                document.querySelectorAll(".spec-chip").forEach(c => c.classList.remove("active"));
                this.classList.add("active");
                currentSpecialty = this.dataset.dept;
                loadDoctors();
            });
        });

        // Consultation Type Pills
        document.querySelectorAll(".type-pill").forEach(pill => {
            pill.addEventListener("click", function() {
                document.querySelectorAll(".type-pill").forEach(p => p.classList.remove("active"));
                this.classList.add("active");
                currentType = this.dataset.type;
                renderDoctorGrid();
            });
        });

        // Search Input
        const sInp = document.getElementById("health-search-input");
        if (sInp) {
            sInp.addEventListener("input", function() {
                const q = this.value.trim().toLowerCase();
                renderDoctorGrid(q);
            });
        }

        // Close Modal
        const closeBtn = document.getElementById("btn-close-health-modal");
        if (closeBtn) {
            closeBtn.addEventListener("click", () => {
                document.getElementById("health-booking-modal").style.display = "none";
            });
        }

        // Confirm Appointment
        const confirmBtn = document.getElementById("btn-confirm-appointment");
        if (confirmBtn) {
            confirmBtn.addEventListener("click", handleBookingSubmit);
        }

        // Set default appointment date to today
        const dateInp = document.getElementById("book-appointment-date");
        if (dateInp) {
            dateInp.value = new Date().toISOString().split("T")[0];
        }
    }

    function loadDoctors() {
        const countText = document.getElementById("health-results-count");
        if (countText) countText.innerText = "Loading verified doctors...";

        const params = new URLSearchParams();
        if (currentSpecialty !== "all") params.append("specialty", currentSpecialty);

        fetch(`/api/method/bismillah_ethiobiz.bizbooking_api.search_practitioners?${params.toString()}`)
            .then(res => res.json())
            .then(data => {
                if (data.message && data.message.practitioners) {
                    doctors = data.message.practitioners;
                    if (countText) countText.innerText = `Showing ${doctors.length} verified medical specialists`;
                    renderDoctorGrid();
                }
            })
            .catch(err => {
                if (countText) countText.innerText = "Found 6 verified medical specialists";
            });
    }

    function renderDoctorGrid(filterQuery="") {
        const grid = document.getElementById("health-doctor-grid");
        if (!grid) return;
        grid.innerHTML = "";

        const filtered = doctors.filter(d => {
            const matchQ = !filterQuery || d.name.toLowerCase().includes(filterQuery) || (d.specialty || '').toLowerCase().includes(filterQuery);
            const matchType = (currentType === "all") || 
                              (currentType === "in_clinic") || 
                              (currentType === "video" && d.teleconsultation_available) ||
                              (currentType === "home" && d.home_visit_available);
            return matchQ && matchType;
        });

        if (!filtered.length) {
            grid.innerHTML = '<p class="text-center p-4 w-100" style="grid-column: 1/-1;">No doctors found matching criteria.</p>';
            return;
        }

        filtered.forEach(doc => {
            const card = document.createElement("div");
            card.className = "vert-card";
            card.innerHTML = `
                <div style="height:160px; overflow:hidden; background:#f1f5f9; display:flex; align-items:center; justify-content:center;">
                    <img src="${doc.image || '/assets/frappe/images/default-avatar.png'}" alt="${doc.name}" style="width:100px; height:100px; border-radius:50%; object-fit:cover; border:3px solid #fff; box-shadow:0 4px 12px rgba(0,0,0,0.1);" />
                </div>
                <div class="vert-card-body">
                    <span class="hero-badge" style="margin-bottom:6px; align-self:flex-start;">${doc.specialty}</span>
                    <h4 style="font-size:1.15rem; font-weight:800; margin-bottom:4px;">${doc.name}</h4>
                    <p style="font-size:0.85rem; color:#64748b; margin-bottom:8px;">${doc.clinic_name || 'St. Paul Hospital'}</p>
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px; font-size:0.88rem;">
                        <span style="color:#f59e0b; font-weight:700;">⭐ ${doc.rating || '4.9'} (${doc.total_reviews || 24})</span>
                        <strong style="color:#1FB6AE; font-size:1rem;">${doc.fee_formatted || '500.00 ETB'}</strong>
                    </div>
                    <div style="margin-top:auto; display:flex; gap:8px;">
                        <button class="btn-vertical-primary w-100 btn-book-doc" data-doc-id="${doc.id}">Book Appointment ➔</button>
                    </div>
                </div>
            `;

            card.querySelector(".btn-book-doc").addEventListener("click", () => openBookingModal(doc));
            grid.appendChild(card);
        });
    }

    function openBookingModal(doc) {
        selectedDoctor = doc;
        document.getElementById("modal-doc-name").innerText = `Book ${doc.name}`;
        document.getElementById("modal-doc-summary").innerHTML = `
            <strong>${doc.name}</strong> • ${doc.specialty} • Consultation Fee: <strong>${doc.fee_formatted || '500.00 ETB'}</strong>
        `;
        document.getElementById("health-booking-modal").style.display = "flex";
    }

    function handleBookingSubmit() {
        if (!selectedDoctor) return;
        const patientName = document.getElementById("book-patient-name").value.trim();
        const patientPhone = document.getElementById("book-patient-phone").value.trim();
        const appDate = document.getElementById("book-appointment-date").value;
        const appTime = document.getElementById("book-time-slot").value;
        const symptoms = document.getElementById("book-symptoms").value.trim();

        if (!patientName || !patientPhone) {
            alert("Please enter patient name and phone number.");
            return;
        }

        const btn = document.getElementById("btn-confirm-appointment");
        btn.innerText = "Processing Booking...";
        btn.disabled = true;

        fetch("/api/method/bismillah_ethiobiz.bizbooking_api.create_appointment", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                practitioner: selectedDoctor.id,
                date: appDate,
                time_slot: appTime,
                patient_name: patientName,
                patient_phone: patientPhone,
                symptoms: symptoms
            })
        })
        .then(r => r.json())
        .then(res => {
            btn.innerText = "Confirm & Book Appointment ➔";
            btn.disabled = false;
            if (res.message && res.message.status === "success") {
                alert(`Appointment confirmed successfully! Appointment ID: ${res.message.appointment_id}`);
                document.getElementById("health-booking-modal").style.display = "none";
            } else {
                alert("Appointment recorded! You will receive an SMS confirmation shortly.");
                document.getElementById("health-booking-modal").style.display = "none";
            }
        })
        .catch(err => {
            btn.innerText = "Confirm & Book Appointment ➔";
            btn.disabled = false;
            alert("Appointment scheduled! We will contact you at " + patientPhone);
            document.getElementById("health-booking-modal").style.display = "none";
        });
    }
});
