/**
 * EthioBiz Universal User Autofill & Identity Engine
 * Bismallah Ar-Rahman Ar-Rahim
 * Automatically populates logged-in user details across all booking,
 * inquiry, lease, repair, healthcare and checkout forms.
 */

(function () {
  window.ETHIOBIZ_USER_PROFILE = null;

  function fetchUserProfile(callback) {
    if (window.ETHIOBIZ_USER_PROFILE) {
      if (callback) callback(window.ETHIOBIZ_USER_PROFILE);
      return;
    }

    fetch("/api/method/bismillah_ethiobiz.ethiobiz_identity.get_current_user_profile", {
      credentials: "same-origin"
    })
      .then((r) => r.json())
      .then((data) => {
        const res = data.message || data;
        if (res && res.status === "success") {
          window.ETHIOBIZ_USER_PROFILE = res;
          applyAutofill(document);
          if (callback) callback(res);
        }
      })
      .catch((e) => {
        console.warn("EthioBiz Identity Autofill check skipped:", e);
      });
  }

  function applyAutofill(root) {
    const p = window.ETHIOBIZ_USER_PROFILE;
    if (!p || !p.logged_in) return;

    const container = root || document;

    // 1. NAME FIELDS
    const nameSelectors = [
      "#custName",
      "#fix-contact-name",
      "#book-patient-name",
      "#bs-name",
      "#bk-name",
      "#checkout-name",
      "#applicant-name",
      "#regHostName",
      "#shopCustName",
      "#orderCustName",
      'input[name="customer_name"]',
      'input[name="patient_name"]',
      'input[name="applicant_name"]',
      'input[name="contact_name"]',
      'input[placeholder*="Abebe" i]',
      'input[placeholder*="Your name" i]'
    ];
    container.querySelectorAll(nameSelectors.join(", ")).forEach((el) => {
      if (!el.value || el.value === el.placeholder) {
        el.value = p.full_name || p.user;
        el.dispatchEvent(new Event("input", { bubbles: true }));
        el.dispatchEvent(new Event("change", { bubbles: true }));
      }
    });

    // 2. PHONE FIELDS
    const phoneSelectors = [
      "#custPhone",
      "#fix-contact-phone",
      "#book-patient-phone",
      "#bs-phone",
      "#bk-phone",
      "#checkout-phone",
      "#applicant-phone",
      "#regHostPhone",
      "#shopCustPhone",
      "#orderCustPhone",
      'input[name="phone"]',
      'input[name="customer_phone"]',
      'input[name="patient_phone"]',
      'input[name="mobile"]',
      'input[placeholder*="09" i]',
      'input[placeholder*="09xxxxxxxx" i]'
    ];
    if (p.phone) {
      container.querySelectorAll(phoneSelectors.join(", ")).forEach((el) => {
        if (!el.value || el.value === el.placeholder) {
          el.value = p.phone;
          el.dispatchEvent(new Event("input", { bubbles: true }));
          el.dispatchEvent(new Event("change", { bubbles: true }));
        }
      });
    }

    // 3. EMAIL FIELDS
    const emailSelectors = [
      "#custEmail",
      "#book-patient-email",
      "#bs-email",
      "#bk-email",
      "#checkout-email",
      "#regHostEmail",
      "#shopCustEmail",
      "#orderCustEmail",
      'input[name="email"]',
      'input[name="customer_email"]',
      'input[name="patient_email"]',
      'input[type="email"]'
    ];
    if (p.email) {
      container.querySelectorAll(emailSelectors.join(", ")).forEach((el) => {
        if (!el.value || el.value === el.placeholder) {
          el.value = p.email;
          el.dispatchEvent(new Event("input", { bubbles: true }));
          el.dispatchEvent(new Event("change", { bubbles: true }));
        }
      });
    }

    // 4. ADDRESS FIELDS
    const addrSelectors = [
      "#custAddress",
      "#fix-address",
      "#fix-location",
      "#bs-address",
      "#shopCustAddress",
      "#orderCustAddress",
      "#checkout-address",
      'textarea[name="address"]',
      'input[name="address"]',
      'input[placeholder*="Bole Medhanialem" i]',
      'textarea[placeholder*="Area / landmark" i]'
    ];
    if (p.address) {
      container.querySelectorAll(addrSelectors.join(", ")).forEach((el) => {
        if (!el.value || el.value === el.placeholder) {
          el.value = p.address;
          el.dispatchEvent(new Event("input", { bubbles: true }));
          el.dispatchEvent(new Event("change", { bubbles: true }));
        }
      });
    }

    // 5. UPDATE EMBEDDED TOP PROFILE CARDS
    const fullName = p.full_name || p.user || "EthioBiz Member";
    const initials = fullName
      .split(" ")
      .map((w) => w[0])
      .filter(Boolean)
      .slice(0, 2)
      .join("")
      .toUpperCase() || "👤";
    const metaParts = [];
    if (p.phone) metaParts.push("📞 " + p.phone);
    if (p.email) metaParts.push("✉️ " + p.email);
    const metaStr = metaParts.join(" • ") || "Verified Profile";

    container.querySelectorAll(".ethiobiz-user-name").forEach((el) => {
      el.innerText = fullName;
    });
    container.querySelectorAll(".ethiobiz-user-meta").forEach((el) => {
      el.innerText = metaStr;
    });
    container.querySelectorAll(".ethiobiz-user-avatar").forEach((el) => {
      el.innerText = initials;
    });

    // 6. INJECT PROFILE BANNER IN MODALS ONLY IF NO TOP PROFILE CARD EXISTS
    const modalBodies = container.querySelectorAll(
      ".modal-body, .bs-modal-box, #booking-modal-card, .home-booking-modal-body, #modal-booking-form-area"
    );
    modalBodies.forEach((body) => {
      if (!body.querySelector(".ethiobiz-autofill-banner") && !body.querySelector(".ethiobiz-user-profile-top-card")) {
        const banner = document.createElement("div");
        banner.className = "ethiobiz-autofill-banner";
        banner.style.cssText =
          "background: linear-gradient(135deg, rgba(13, 148, 136, 0.12), rgba(2, 132, 199, 0.1)); border: 1px solid rgba(13, 148, 136, 0.28); border-radius: 12px; padding: 10px 14px; margin-bottom: 15px; display: flex; align-items: center; justify-content: space-between; font-size: 13px; color: #0f766e;";
        banner.innerHTML = `
          <div style="display:flex; align-items:center; gap:8px;">
            <span style="font-size:16px;">👤</span>
            <div>
              <div style="font-weight:700; color:#0f766e;">Auto-Filled: ${p.full_name}</div>
              <div style="font-size:11.5px; color:#475569;">${p.phone ? '📱 ' + p.phone : ''} ${p.email ? ' • ✉️ ' + p.email : ''}</div>
            </div>
          </div>
          <span style="background:#0d9488; color:#ffffff; font-size:10.5px; font-weight:700; padding:3px 8px; border-radius:12px; text-transform:uppercase;">✓ Verified Profile</span>
        `;
        body.insertBefore(banner, body.firstChild);
      }
    });
  }

  // Hook into DOMContentLoaded
  document.addEventListener("DOMContentLoaded", function () {
    fetchUserProfile();

    // Observe modal opens or dynamic DOM injections
    const observer = new MutationObserver(function (mutations) {
      mutations.forEach(function (m) {
        if (m.addedNodes && m.addedNodes.length) {
          applyAutofill(document);
        }
      });
    });

    observer.observe(document.body, { childList: true, subtree: true });

    // Re-check on clicks that open modals
    document.addEventListener("click", function (e) {
      if (
        e.target.closest(
          '[data-toggle="modal"], [data-bs-toggle="modal"], .btn-vertical-primary, .bs-btn, .btn-primary, .feed-action-cta-btn, button'
        )
      ) {
        setTimeout(function () {
          applyAutofill(document);
        }, 150);
        setTimeout(function () {
          applyAutofill(document);
        }, 500);
      }
    });
  });

  window.ethiobizAutofillProfile = applyAutofill;
  window.getEthioBizUser = function (cb) {
    fetchUserProfile(cb);
  };
})();
