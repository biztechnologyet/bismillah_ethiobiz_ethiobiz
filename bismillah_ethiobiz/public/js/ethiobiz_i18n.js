// BISMALLAH ETHIOBIZ UNIFIED AMHARIC & ENGLISH I18N SYSTEM (Insha'Allah)
// Centralized bilingual engine for all pages: Homepage, /shop, /jobs, /map, /social, /post, /tibeb, /dagu, /walta, /bizhome, /bizhealth, /bizservices, /bizfix

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
            "Order Product ➔": "ምርቱን ይዘዙ ➔",
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
            "Read Article ➔": "ጽሑፉን ያንብቡ ➔",
            "Enroll Now": "አሁን ይመዝገቡ",
            "Enroll Now →": "አሁን ይመዝገቡ →",
            "Join Discussion": "ውይይቱን ይቀላቀሉ",
            "Join Discussion →": "ውይይቱን ይቀላቀሉ →",
            "Join Topic ➔": "ውይይቱን ይቀላቀሉ ➔",
            "Learn More ➔": "ተጨማሪ ይወቁ ➔",
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

            // Homepage Keys
            "stat-1": "🏢 የተረጋገጡ ድርጅቶች",
            "stat-2": "🛍️ የብዙ-ነጋዴዎች ንግድ",
            "stat-3": "💼 የተረጋገጡ የሥራ ዕድሎች",
            "stat-4": "⚡ የተረጋገጡ ቢዝ ሰርቪሶች",
            "hero-greeting-guest": "ሰላም፣ ወደ ኢትዮቢዝ እንኳን በደህና መጡ",
            "hero-slide-market-eyebrow": "የኢትዮቢዝ መድረክ",
            "hero-slide-market-title": "ንግድዎን ያሳድጉ። ደንበኞችዎን ያግኙ።",
            "hero-slide-market-description": "ንግድዎን ወደ ዲጂታል ያምጡ፣ ከአገር ውስጥ ደንበኞች ጋር ይገናኙ፣ እና ጠቃሚ አገልግሎቶችን፣ ትምህርትንና የሥራ ዕድሎችን በአንድ የኢትዮጵያ ሥርዓት ውስጥ ያግኙ።",
            "hero-slide-market-primary": "⚡ ነፃ የታይነት እና የስራ ፍሰት ኦዲት ያግኙ",
            "hero-slide-market-secondary": "ስለ ኢትዮቢዝ የበለጠ ይወቁ",
            "hero-slide-erp-eyebrow": "ዶቢዝ ስማርት ኢአርፒ",
            "hero-slide-erp-title": "ንግድዎን በግልጽነትና በብቃት ይምሩ።",
            "hero-slide-erp-description": "የሽያጭ፣ የእቃ ክምችት፣ የፋይናንስ፣ የደመወዝ እና የዕለት ተዕለት ሥራዎችን በአንድ ተግባራዊ የንግድ ሶፍትዌር ያቀናጁ።",
            "hero-slide-solutions-eyebrow": "ቢዝ ቴክኖሎጂ ሶሉሽንስ",
            "hero-slide-solutions-title": "ትክክለኛው ቴክኖሎጂ፣ በአገር ውስጥ ድጋፍ።",
            "hero-slide-solutions-description": "ብጁ ሶፍትዌሮችን ይገንቡ፣ የድርጅት ስርዓቶችን ያገናኙ፣ አሰራሮችን ያቀላጥፉ፣ እና አስተማማኝ የአይቲ ድጋፍ ያግኙ።",
            "hero-slide-marketplace-eyebrow": "መጋላ የገበያ መድረክ",
            "hero-slide-marketplace-title": "የአገር ውስጥ ምርቶችን ያግኙ። በእምነት ይሸምቱ።",
            "hero-slide-marketplace-description": "ከአገር ውስጥ ሻጮች ምርቶችን ይመርምሩ እና ለዕለት ተዕለት ፍላጎቶች የታመኑ አገልግሎቶችን በኢትዮቢዝ ውስጥ ያግኙ።",
            "hero-slide-jobs-eyebrow": "ኡሱ የሥራ ዕድሎች",
            "hero-slide-jobs-title": "ወደፊት የሚያራምድዎትን ሥራ ያግኙ።",
            "hero-slide-jobs-description": "የሙያ ዕድሎችን ይመርምሩ፣ ከችሎታዎ ጋር የሚስማሙ ሚናዎችን ያግኙ፣ እና ቀጣዩን እርምጃ ከኢትዮቢዝ ጋር ይውሰዱ።",
            "hero-slide-learning-eyebrow": "ዳጉ አካዳሚ",
            "hero-slide-learning-title": "ሙያ ይማሩ። እውቀትን ወደ ተግባር ይቀይሩ።",
            "hero-slide-learning-description": "እድገትዎን በሚያግዙ፣ እውቀትን ወደ ዕድል በሚቀይሩ ተግባራዊ የትምህርት መስመሮች ችሎታዎን ያዳብሩ።",
            "hero-pathways-title": "በሚፈልጉት ይጀምሩ",
            "hero-pathways-sub": "ለንግድ፣ ለድርጅት ስርዓቶች፣ ለትምህርት፣ ለማኅበራዊ ጥበብ፣ ለማኅበረሰብ እና ለድጋፍ የተዘጋጁ ልዩ መድረኮቻችንን ይመርምሩ።",
            "explore-title": "የኢትዮቢዝ ስነ-ምህዳርን ያስሱ",
            "explore-sub": "ለንግድ፣ ለድርጅት ስርዓቶች፣ ለትምህርት፣ ለማኅበራዊ ጥበብ፣ ለማኅበረሰብ እና ለድጋፍ የተዘጋጁ ልዩ መድረኮቻችንን ይመርምሩ።",
            "foryou-title": "🔥 ለእርስዎ የተመረጡ",
            "filter-all": "🔥 ለእርስዎ ዥረት",
            "filter-shop": "🛍️ ዲካ ገበያ",
            "filter-jobs": "💼 ኡሱ ሥራዎች",
            "filter-services": "⚡ ቢዝ ሰርቪሶች",
            "filter-health": "🩺 ቢዝ ጤና",
            "filter-home": "🏠 ቢዝ ሆም",
            "filter-fix": "🔧 ቢዝ ጥገና",
            "filter-dagu": "🎓 ዳጉ አካዳሚ",
            "filter-tibeb": "📝 ጥበብ",
            "filter-social": "🌟 አፎቻ ማኅበራዊ",
            "filter-forum": "💬 ዋልታ መድረክ",
            "filter-news": "📰 አዳዲስ ዜናዎች",
            "btn-like": "ወደድኩት",
            "btn-comment": "አስተያየት",
            "btn-repost": "አጋራ",
            "btn-share": "አጋራ",
            "btn-view-details": "ዝርዝሩን እይ ➔",
            "sentinel-text": "የቀጥታ ስነ-ምህዳር ዝመናዎችን በመጫን ላይ...",

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
        currentLang = (lang === 'am') ? 'am' : 'en';
        try {
            localStorage.setItem('ethiobiz_lang', currentLang);
        } catch(e) {}

        applyTranslations();
        updateToggleButtons();

        // Dispatch events for all page scripts
        window.dispatchEvent(new CustomEvent('ethiobiz-lang-changed', { detail: { lang: currentLang } }));
        window.dispatchEvent(new CustomEvent('ethiobiz:lang_changed', { detail: { lang: currentLang } }));
        document.dispatchEvent(new CustomEvent('ethiobiz-lang-changed', { detail: { lang: currentLang } }));
    }

    function applyTranslations() {
        if (currentLang === 'en') {
            document.querySelectorAll('[data-i18n-orig]').forEach(el => {
                el.innerText = el.getAttribute('data-i18n-orig');
            });
            document.querySelectorAll('[data-i18n-ph-orig]').forEach(el => {
                el.setAttribute('placeholder', el.getAttribute('data-i18n-ph-orig'));
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
        document.querySelectorAll('.ethiobiz-nav-lang-btn').forEach(btn => {
            const lang = btn.getAttribute('data-lang');
            btn.classList.toggle('active', lang === currentLang);
        });
    }

    function injectNavbarLangToggle() {
        // Prevent duplicate injection
        if (document.getElementById('ethiobiz-navbar-lang-pill')) return;

        // Ensure floating toggle is removed
        const oldFloat = document.getElementById('ethiobiz-floating-lang-toggle');
        if (oldFloat) oldFloat.remove();
        const oldHomeToggle = document.getElementById('ethiobiz-lang-toggle-btn');
        if (oldHomeToggle && oldHomeToggle.parentElement && oldHomeToggle.parentElement.id === 'lang-toggle-container') {
            oldHomeToggle.parentElement.remove();
        }

        // Create unified navbar pill
        const pill = document.createElement('div');
        pill.id = 'ethiobiz-navbar-lang-pill';
        pill.className = 'ethiobiz-navbar-lang-pill';
        pill.innerHTML = `
            <span class="lang-globe-icon" aria-hidden="true">🌐</span>
            <button type="button" class="ethiobiz-nav-lang-btn ${currentLang === 'en' ? 'active' : ''}" data-lang="en">EN</button>
            <span class="lang-divider">|</span>
            <button type="button" class="ethiobiz-nav-lang-btn ${currentLang === 'am' ? 'active' : ''}" data-lang="am">አማ</button>
        `;

        // Inject Styles
        if (!document.getElementById('ethiobiz-nav-lang-style')) {
            const style = document.createElement('style');
            style.id = 'ethiobiz-nav-lang-style';
            style.textContent = `
                .ethiobiz-navbar-lang-pill {
                    display: inline-flex;
                    align-items: center;
                    gap: 3px;
                    background: rgba(255, 255, 255, 0.94);
                    border: 1px solid rgba(13, 148, 136, 0.35);
                    border-radius: 999px;
                    padding: 2px 7px;
                    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
                    backdrop-filter: blur(8px);
                    -webkit-backdrop-filter: blur(8px);
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Noto Sans Ethiopic", sans-serif;
                    font-size: 11.5px;
                    font-weight: 700;
                    margin: 0 8px;
                    transition: all 0.2s ease;
                    z-index: 10001;
                }
                .ethiobiz-navbar-lang-pill:hover {
                    border-color: #0d9488;
                    box-shadow: 0 4px 14px rgba(13, 148, 136, 0.2);
                }
                .lang-globe-icon {
                    font-size: 12px;
                    opacity: 0.85;
                }
                .lang-divider {
                    color: #cbd5e1;
                    font-size: 10px;
                    line-height: 1;
                }
                .ethiobiz-nav-lang-btn {
                    border: none;
                    background: transparent;
                    color: #475569;
                    padding: 3px 6px;
                    border-radius: 999px;
                    cursor: pointer;
                    font-size: 11.5px;
                    font-weight: 700;
                    transition: all 0.2s ease;
                    outline: none;
                }
                .ethiobiz-nav-lang-btn:hover {
                    color: #0d9488;
                }
                .ethiobiz-nav-lang-btn.active {
                    background: #0d9488;
                    color: #ffffff !important;
                    box-shadow: 0 1px 6px rgba(13, 148, 136, 0.35);
                }
                @media (max-width: 768px) {
                    .ethiobiz-navbar-lang-pill {
                        padding: 2px 5px;
                        font-size: 11px;
                        margin: 0 4px;
                    }
                    .ethiobiz-nav-lang-btn {
                        padding: 2px 5px;
                        font-size: 11px;
                    }
                }
            `;
            document.head.appendChild(style);
        }

        // Attach click events
        pill.querySelectorAll('.ethiobiz-nav-lang-btn').forEach(b => {
            b.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                const l = b.getAttribute('data-lang');
                setLanguage(l);
            });
        });

        // Find best host in DOM
        const targets = [
            document.querySelector('.navbar .container .navbar-collapse .navbar-nav'),
            document.querySelector('.navbar .navbar-nav'),
            document.querySelector('.navbar .container'),
            document.querySelector('.nav-actions'),
            document.querySelector('.ethiobiz-nav-actions'),
            document.querySelector('header nav'),
            document.querySelector('.navbar')
        ];

        let mounted = false;
        for (const t of targets) {
            if (t) {
                t.appendChild(pill);
                mounted = true;
                break;
            }
        }

        if (!mounted) {
            // Safe fallback top-right dock
            pill.style.position = 'fixed';
            pill.style.top = '14px';
            pill.style.right = '70px';
            document.body.appendChild(pill);
        }
    }

    function initI18n() {
        try {
            const saved = localStorage.getItem('ethiobiz_lang');
            if (saved === 'am' || saved === 'en') {
                currentLang = saved;
            }
        } catch(e) {}

        injectNavbarLangToggle();
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
        translate: (key) => (DICTIONARY[currentLang] || {})[key] || key,
        t: (key) => (DICTIONARY[currentLang] || {})[key] || key
    };
})();
