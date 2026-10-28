// BISMALLAH ETHIOBIZ UNIFIED AMHARIC & ENGLISH I18N SYSTEM
// Supports all subsystems: /shop, /jobs, /map, /social, /post, /tibeb, /dagu, /walta, /bizhome, /bizhealth, /bizservices, /bizfix

(function() {
    const DICTIONARY = {
        am: {
            // Navigation & Brand
            "Home": "ዋና ገጽ",
            "Shop": "መገበያያ (መጋላ)",
            "Magala": "መጋላ ገበያ",
            "Jobs": "የሥራ ዕድሎች",
            "Careers": "የሥራ ዕድሎች",
            "Map": "የካርታ ማውጫ",
            "Social": "አፎቻ ማኅበራዊ",
            "Tibeb": "ጥበብ",
            "Dagu": "ዳጉ አካዳሚ",
            "Walta": "ዋልታ መድረክ",
            "Services": "አገልግሎቶች",
            "Health": "ጤናና ክሊኒክ",
            "Properties": "ሪል እስቴት",
            "Login": "ይግቡ",
            "Register": "ይመዝገቡ",
            "Account": "መለያዬ",
            "Cart": "ጋሪ",

            // Common CTAs & Actions
            "Search": "ይፈልጉ",
            "Search...": "ይፈልጉ...",
            "Search businesses, clinics, hotels...": "ንግዶችን፣ ክሊኒኮችን፣ ሆቴሎችን ይፈልጉ...",
            "Search products, services, jobs...": "ምርቶችን፣ አገልግሎቶችን፣ ሥራዎችን ይፈልጉ...",
            "Order Now": "አሁን ይዘዙ",
            "Order Now →": "አሁን ይዘዙ →",
            "Apply Now": "አሁን ያመልክቱ",
            "Apply Now →": "አሁን ያመልክቱ →",
            "Book Now": "ቀጠሮ ይያዙ",
            "Book Service": "አገልግሎት ይያዙ",
            "Book Service →": "አገልግሎት ይያዙ →",
            "Reserve Now": "ቦታ ይያዙ",
            "Reserve Now →": "ቦታ ይያዙ →",
            "View Details": "ዝርዝሩን ይመልከቱ",
            "View Details →": "ዝርዝሩን ይመልከቱ →",
            "Read Article": "ጽሑፉን ያንብቡ",
            "Read Article →": "ጽሑፉን ያንብቡ →",
            "Enroll Now": "አሁን ይመዝገቡ",
            "Enroll Now →": "አሁን ይመዝገቡ →",
            "Join Discussion": "ውይይቱን ይቀላቀሉ",
            "Join Discussion →": "ውይይቱን ይቀላቀሉ →",
            "Directions": "አቅጣጫ",
            "🧭 Directions": "🧭 አቅጣጫ አሳይ",
            "Near Me": "በአቅራቢያዬ",
            "📍 Near Me": "📍 በአቅራቢያዬ",
            "Locate Me": "ቦታዬን ፈልግ",
            "🎯 Locate Me": "🎯 ቦታዬን ፈልግ",
            "Fit All": "ሁሉንም አሳይ",
            "🗺️ Fit All": "🗺️ ሁሉንም አሳይ",
            "Dossier": "መረጃ",
            "Back to List": "ወደ ዝርዝሩ ተመለስ",
            "← Back to List": "← ወደ ዝርዝሩ ተመለስ",
            "Confirm Reservation": "ቀጠሮውን ያረጋግጡ",
            "Filter": "አጣራ",
            "All": "ሁሉም",
            "All Feed": "ሁሉም ዝመናዎች",
            "Products & Goods": "ምርቶችና ዕቃዎች",
            "Job Openings": "ክፍት የሥራ ቦታዎች",
            "Service Bookings": "የአገልግሎት ቀጠሮዎች",
            "Afocha Stories": "የአፎቻ ታሪኮች",
            "Tibeb Articles": "የጥበብ ጽሑፎች",
            "Open": "ክፍት ነው",
            "Closed": "ዝግ ነው",
            "Verified Merchant": "የተረጋገጠ ነጋዴ",
            "Verified": "የተረጋገጠ",
            "Head Office": "ዋና መሥሪያ ቤት",
            "Branch": "ቅርንጫፍ",
            "⭐ Head Office": "⭐ ዋና መሥሪያ ቤት",
            "Competitive Salary": "ማራኪ ደመወዝ",
            "Full-time": "ሙሉ ጊዜ",
            "Part-time": "የትርፍ ሰዓት",
            "Contract": "በኮንትራት",
            "Price": "ዋጋ",
            "Inquire for Price": "ለዋጋ ይጠይቁ",
            "Available Online": "በመስመር ላይ ይገኛል",

            // Subsystems
            "BizHome": "ቢዝ ሆም",
            "BizHealth": "ቢዝ ጤና",
            "BizFix": "ቢዝ ጥገና",
            "BizRide": "ቢዝ ራይድ",
            "BizServices": "ቢዝ አገልግሎቶች"
        },
        en: {
            "Home": "Home",
            "Shop": "Shop",
            "Magala": "Magala Shop",
            "Jobs": "Jobs & Careers",
            "Careers": "Careers",
            "Map": "Map Directory",
            "Social": "Afocha Social",
            "Tibeb": "Tibeb Wisdom",
            "Dagu": "Dagu Academy",
            "Walta": "Walta Forum",
            "Services": "Services",
            "Health": "Health & Clinics",
            "Properties": "Properties",
            "Login": "Login",
            "Register": "Register",
            "Account": "My Account",
            "Cart": "Cart",
            "Search": "Search",
            "Order Now": "Order Now",
            "Apply Now": "Apply Now",
            "Book Now": "Book Now",
            "Verified Merchant": "Verified Merchant"
        }
    };

    let currentLang = 'en';

    function setLanguage(lang) {
        currentLang = lang;
        try {
            localStorage.setItem('ethiobiz_lang', lang);
        } catch(e) {}

        applyTranslations();
        updateToggleButtons();

        // Dispatch custom event for page scripts
        window.dispatchEvent(new CustomEvent('ethiobiz:lang_changed', { detail: { lang: lang } }));
    }

    function applyTranslations() {
        if (currentLang === 'en') {
            document.querySelectorAll('[data-i18n-orig]').forEach(el => {
                el.innerText = el.getAttribute('data-i18n-orig');
            });
            return;
        }

        const dict = DICTIONARY[currentLang] || {};

        // 1. Explicit data-i18n elements
        document.querySelectorAll('[data-i18n]').forEach(el => {
            const key = el.getAttribute('data-i18n');
            if (!el.hasAttribute('data-i18n-orig')) {
                el.setAttribute('data-i18n-orig', el.innerText.trim());
            }
            if (dict[key]) {
                el.innerText = dict[key];
            }
        });

        // 2. Common UI text matches
        document.querySelectorAll('button, a, span.stream-card-badge, .stream-card-link, .map-cat-chip, .btn-geo-action, .map-tool-btn, .btn-card-booking').forEach(el => {
            if (el.children.length === 0) {
                const txt = el.innerText.trim();
                if (txt && dict[txt]) {
                    if (!el.hasAttribute('data-i18n-orig')) {
                        el.setAttribute('data-i18n-orig', txt);
                    }
                    el.innerText = dict[txt];
                }
            }
        });

        // 3. Inputs placeholder
        document.querySelectorAll('input[placeholder]').forEach(el => {
            const ph = el.getAttribute('placeholder');
            if (ph && dict[ph]) {
                if (!el.hasAttribute('data-i18n-ph-orig')) {
                    el.setAttribute('data-i18n-ph-orig', ph);
                }
                el.setAttribute('placeholder', dict[ph]);
            }
        });
    }

    function updateToggleButtons() {
        document.querySelectorAll('.ethiobiz-lang-toggle-btn').forEach(btn => {
            if (currentLang === 'am') {
                btn.innerHTML = '🌐 አማርኛ (AM)';
                btn.classList.add('is-amharic');
            } else {
                btn.innerHTML = '🌐 English (EN)';
                btn.classList.remove('is-amharic');
            }
        });
    }

    function injectFloatingLangToggle() {
        // Only inject if not already present
        if (document.getElementById('ethiobiz-floating-lang-toggle')) return;

        const toggle = document.createElement('div');
        toggle.id = 'ethiobiz-floating-lang-toggle';
        toggle.style.cssText = `
            position: fixed;
            bottom: 24px;
            left: 24px;
            z-index: 9999;
            display: flex;
            align-items: center;
            background: #ffffff;
            border: 1px solid #cbd5e1;
            border-radius: 30px;
            box-shadow: 0 4px 18px rgba(0,0,0,0.12);
            overflow: hidden;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            font-size: 0.82rem;
            font-weight: 800;
        `;

        toggle.innerHTML = `
            <button id="btn-lang-en" style="border:none; padding: 7px 12px; cursor:pointer; background: ${currentLang==='en'?'#0d9488':'transparent'}; color:${currentLang==='en'?'#ffffff':'#334155'}; transition:all 0.2s ease;">EN</button>
            <button id="btn-lang-am" style="border:none; padding: 7px 12px; cursor:pointer; background: ${currentLang==='am'?'#0d9488':'transparent'}; color:${currentLang==='am'?'#ffffff':'#334155'}; font-family:'Noto Sans Ethiopic',sans-serif; transition:all 0.2s ease;">አማ</button>
        `;

        document.body.appendChild(toggle);

        document.getElementById('btn-lang-en').addEventListener('click', () => {
            setLanguage('en');
            document.getElementById('btn-lang-en').style.background = '#0d9488';
            document.getElementById('btn-lang-en').style.color = '#ffffff';
            document.getElementById('btn-lang-am').style.background = 'transparent';
            document.getElementById('btn-lang-am').style.color = '#334155';
        });

        document.getElementById('btn-lang-am').addEventListener('click', () => {
            setLanguage('am');
            document.getElementById('btn-lang-am').style.background = '#0d9488';
            document.getElementById('btn-lang-am').style.color = '#ffffff';
            document.getElementById('btn-lang-en').style.background = 'transparent';
            document.getElementById('btn-lang-en').style.color = '#334155';
        });
    }

    function initI18n() {
        try {
            const saved = localStorage.getItem('ethiobiz_lang');
            if (saved === 'am' || saved === 'en') {
                currentLang = saved;
            }
        } catch(e) {}

        injectFloatingLangToggle();
        if (currentLang === 'am') {
            applyTranslations();
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initI18n);
    } else {
        initI18n();
    }

    // Expose global controller
    window.EthioBizI18n = {
        setLanguage: setLanguage,
        getLanguage: () => currentLang,
        translate: (key) => (DICTIONARY[currentLang] || {})[key] || key
    };
})();
