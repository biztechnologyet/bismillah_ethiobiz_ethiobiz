// BISMALLAH ETHIOBIZ HEALTH — DOCTOR DETAIL PAGE v1.0.0
document.addEventListener("DOMContentLoaded", function () {
    var slug = window.DOCTOR_SLUG || new URLSearchParams(window.location.search).get("slug") || "";
    var doctor = null;

    function fmtSlot(slot) {
        var parts = String(slot || "").split(":");
        if (parts.length < 2) return slot;
        var hh = parseInt(parts[0], 10);
        if (isNaN(hh)) return slot;
        var suf = hh >= 12 ? "PM" : "AM";
        return (((hh + 11) % 12) + 1) + ":" + parts[1] + " " + suf;
    }

    function loadDetail() {
        fetch("/api/method/bismillah_ethiobiz.bizhealth_api.get_doctor_detail?slug=" + encodeURIComponent(slug))
            .then(function (r) { return r.json(); })
            .then(function (data) {
                var d = data.message || {};
                if (d.status !== "success" || !d.doctor) {
                    window.location.href = "/bizhealth";
                    return;
                }
                doctor = d.doctor;
                renderDoctor(doctor);
            })
            .catch(function () { window.location.href = "/bizhealth"; });
    }

    function renderDoctor(d) {
        var card = document.getElementById("dd-doctor-card");
        if (!card) return;
        var initials = d.name.replace("Dr. ", "").split(" ").map(function (w) { return w[0]; }).join("").substring(0, 2);
        var modes = [];
        if (d.teleconsultation_available) modes.push('<span class="spec-chip" style="background:#eff6ff; color:#1d4ed8;">📹 Video Consult</span>');
        if (d.home_visit_available) modes.push('<span class="spec-chip" style="background:#fef3c7; color:#92400e;">🏠 Home Visit</span>');
        modes.push('<span class="spec-chip" style="background:#f0fdf4; color:#047857;">🏥 In-Clinic</span>');

        card.innerHTML =
            '<div style="max-width:560px; margin:0 auto; text-align:center;">' +
                '<div style="width:96px; height:96px; border-radius:50%; margin:0 auto 12px; overflow:hidden; background:' + (d.image && d.image.indexOf("default-avatar") === -1 ? "transparent" : "var(--vert-health-light)") + '; display:flex; align-items:center; justify-content:center; font-size:2.2rem; font-weight:900; color:var(--vert-health);">' +
                    (d.image && d.image.indexOf("default-avatar") === -1 ? '<img src="' + d.image + '" style="width:100%; height:100%; object-fit:cover;" alt="" />' : initials) +
                '</div>' +
                '<h1 style="font-size:1.6rem; font-weight:900; color:#0f172a; margin:0 0 4px;">' + d.name + '</h1>' +
                '<div style="font-weight:600; color:var(--vert-health); margin-bottom:4px;">' + d.specialty + '</div>' +
                '<div style="font-weight:600; color:#475569; font-size:0.9rem; margin-bottom:10px;">' + d.qualifications + '</div>' +
                '<div class="doc-summary-badge" style="margin:6px auto; max-width:440px;">' +
                    '⭐ ' + d.rating + ' <span style="color:#94a3b8;">(' + d.total_reviews + ')</span>' +
                    ' &nbsp;•&nbsp; 📍 ' + d.clinic +
                    ' &nbsp;•&nbsp; 💰 ' + d.fee_formatted +
                    ' &nbsp;•&nbsp; 🗣 ' + d.languages +
                '</div>' +
                '<div style="display:flex; gap:8px; justify-content:center; flex-wrap:wrap; margin-top:10px;">' + modes.join("") + '</div>' +
            '</div>';

        var about = document.getElementById("dd-about-text");
        if (about) about.textContent = d.bio || ("Dr. " + d.name + " is a " + d.specialty + " specialist at " + d.clinic + ". EthioBiz Health verifies every physician listed on the platform.");

        // Book deep-link carries doctor + (optional) date/time
        var cta = document.getElementById("dd-book-cta");
        if (cta) cta.href = "/bizhealth?doctor=" + encodeURIComponent(d.id) + "&date=" + (document.getElementById("dd-date").value || "");
    }

    function loadSlots() {
        if (!doctor) return;
        var date = document.getElementById("dd-date").value;
        if (!date) return;
        var slotsWrap = document.getElementById("dd-slots");
        slotsWrap.innerHTML = '<span style="color:#94a3b8; font-size:0.85rem;">Loading real slots…</span>';
        fetch("/api/method/bismillah_ethiobiz.bizhealth_api.get_doctor_slots?doctor_id=" + encodeURIComponent(doctor.id) + "&date=" + encodeURIComponent(date))
            .then(function (r) { return r.json(); })
            .then(function (data) {
                var slots = ((data.message && data.message.slots) || []).filter(function (s) { return s.is_available !== false; });
                if (!slots.length) {
                    slotsWrap.innerHTML = '<span style="color:#b91c1c; font-size:0.85rem;">No slots available on this date. Try another day.</span>';
                    return;
                }
                slotsWrap.innerHTML = "";
                slots.forEach(function (s) {
                    var chip = document.createElement("button");
                    chip.type = "button";
                    chip.className = "spec-chip";
                    chip.textContent = fmtSlot(s.slot);
                    chip.style.border = "1.5px solid var(--vert-health)";
                    chip.style.color = "var(--vert-health)";
                    chip.addEventListener("click", function () {
                        var cta = document.getElementById("dd-book-cta");
                        if (cta) cta.href = "/bizhealth?doctor=" + encodeURIComponent(doctor.id) + "&date=" + encodeURIComponent(date) + "&time=" + encodeURIComponent(s.slot);
                    });
                    slotsWrap.appendChild(chip);
                });
            })
            .catch(function () {
                slotsWrap.innerHTML = '<span style="color:#b91c1c; font-size:0.85rem;">Could not load slots.</span>';
            });
    }

    var dateInp = document.getElementById("dd-date");
    if (dateInp) {
        dateInp.value = new Date().toISOString().split("T")[0];
        dateInp.min = new Date().toISOString().split("T")[0];
        dateInp.addEventListener("change", loadSlots);
    }
    var refreshBtn = document.getElementById("dd-refresh");
    if (refreshBtn) refreshBtn.addEventListener("click", loadSlots);

    loadDetail();
    var cta = document.getElementById("dd-book-cta");
    if (cta) cta.addEventListener("click", function () { if (doctor) cta.href = "/bizhealth?doctor=" + encodeURIComponent(doctor.id); });
});