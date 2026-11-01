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
            "filter-shop": "🛍️ ዲኮ ገበያ",
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
            "BizServices": "ቢዝ አገልግሎቶች",

            // ============================================================
            // GLOBAL UI, BRAND & ACTIONS
            // Covers navbar/footer/forms/CTAs on every website page.
            // ============================================================
            "EthioBiz": "ኢትዮቢዝ",
            "DOBiz": "ዶቢዝ",
            "DOBiz SmartERP": "ዶቢዝ ስማርት ኢአርፒ",
            "Dikko Shop": "ዲኮ ሾፕ",
            "Oosoo Jobs": "ኡሱ ሥራዎች",
            "Hadeeda AI": "ሐዲዳ AI",
            "BizMap": "ቢዝማፕ",
            "BizBooking": "ቢዝቡኪንግ",
            "Afocha": "አፎቻ",
            "Get Started": "ይጀምሩ",
            "Learn More": "ተጨማሪ ይወቁ",
            "Contact Sales": "የሽያጭ ክፍልን ያግኙ",
            "Contact Support": "ድጋፍን ያግኙ",
            "Help & Support": "እርዳታና ድጋፍ",
            "Create Account": "መለያ ይክፈቱ",
            "Sign Up": "ይመዝገቡ",
            "Sign In": "ይግቡ",
            "Submit": "አስገባ",
            "Save": "አስቀምጥ",
            "Cancel": "ሰርዝ",
            "Close": "ዝጋ",
            "Next": "ቀጣይ",
            "Previous": "ቀዳሚ",
            "Back": "ተመለስ",
            "Continue": "ቀጥል",
            "View All": "ሁሉንም ይመልከቱ",
            "See More": "ተጨማሪ ይመልከቱ",
            "Read More": "ተጨማሪ ያንብቡ",
            "Explore": "ያስሱ",
            "Download": "አውርድ",
            "Upload": "ስቀል",
            "Pay Now": "አሁን ይክፈሉ",
            "Add to Cart": "ወደ ጋሪ ጨምር",
            "Checkout": "ክፍያ",
            "Quantity": "ብዛት",
            "Total": "ጠቅላላ",
            "Subtotal": "ንዑስ ድምር",
            "Free": "ነፃ",
            "Demo": "ማሳያ",
            "Book a Demo": "ማሳያ ይያዙ",
            "Start Free Trial": "ነፃ ሙከራ ይጀምሩ",
            "Request a Demo": "ማሳያ ይጠይቁ",
            "Get a Quote": "ዋጋ ይጠይቁ",
            "Call Us": "ይደውሉልን",
            "Email Us": "ኢሜይል ይላኩልን",
            "Phone": "ስልክ",
            "Email": "ኢሜይል",
            "Address": "አድራሻ",
            "Working Hours": "የሥራ ሰዓት",
            "Follow Us": "ይከተሉን",
            "Newsletter": "ጋዜጣ",
            "Subscribe": "ይመዝገቡ",
            "Language": "ቋንቋ",
            "English": "እንግሊዝኛ",
            "Amharic": "አማርኛ",
            "Select Language": "ቋንቋ ይምረጡ",
            "Welcome": "እንኳን ደህና መጡ",
            "All Rights Reserved": "መብቱ በሕግ የተጠበቀ ነው",

            // ============================================================
            // MAGALA — MARKETPLACE PILLAR
            // ============================================================
            "EMPOWERING ETHIOPIAN ENTERPRISE INSHA'ALLAH...": "የኢትዮጵያን ድርጅቶች እናበረታታለን ኢንሻአላህ...",
            "LIVE ECOSYSTEM": "ቀጥታ ስነ-ምህዳር",
            "EthioBiz Pillar III: Marketplace of the Body": "የኢትዮቢዝ ሦስተኛው ምሰሶ፡ የሰውነት ገበያ",
            "MARKETPLACE OF THE BODY • ETHIOBIZ & DOBIZ ERP": "የሰውነት ገበያ • ኢትዮቢዝ እና ዶቢዝ ኢአርፒ",
            "Prosperity Through Integrity.": "በታማኝነት የተገኘ ብልጽግና።",
            "Sign Up for DOBiz ERP": "ለዶቢዝ ኢአርፒ ይመዝገቡ",
            "Explore BizMap": "ቢዝማፕን ያስሱ",
            "ACTIVE COMMERCE CHANNELS": "ንቁ የንግድ መስመሮች",
            "Discover, Book & Transact Across Ethiopia": "በመላው ኢትዮጵያ ያግኙ፣ ይያዙ እና ይግባቡ",
            "BizMap Discovery": "የቢዝማፕ ፍለጋ",
            "Open BizMap Explorer": "የቢዝማፕ አሳሽ ይክፈቱ",
            "BizBooking Services": "የቢዝቡኪንግ አገልግሎቶች",
            "Start Instant Booking": "ፈጣን ቀጠሮ ይጀምሩ",
            "Dikko Shop Marketplace": "የዲኮ ሾፕ ገበያ",
            "Visit Dikko Shop": "ዲኮ ሾፕን ይጎብኙ",
            "Oosoo Jobs & Talent": "ኡሱ ሥራዎችና ችሎታ",
            "Explore Oosoo Jobs": "ኡሱ ሥራዎችን ያስሱ",
            "COMPLETE ENTERPRISE SUITE": "ሙሉ የድርጅት ስብስብ",
            "DOBiz SmartERP Industry Solutions": "የዶቢዝ ስማርት ኢአርፒ የኢንዱስትሪ መፍትሄዎች",
            "Biz Technology Solutions": "ቢዝ ቴክኖሎጂ ሶሉሽንስ",
            "TRADE & DISTRIBUTION": "ንግድና ስርጭት",
            "DOBiz Retail & Wholesale": "ዶቢዝ ግብይትና ጅምላ",
            "Telebirr, CBE & multi-currency payment": "ቴሌብር፣ CBE እና ብዙ ምንዛሬ ክፍያ",
            "Barcode generation & batch tracking": "ባርኮድ ማመንጨትና ባች ክትትል",
            "Automatic branch stock replenishment": "ራስ-ሰር የቅርንጫፍ ክምችት ምላድ",
            "Explore DOBiz Retail": "ዶቢዝ ግብይትን ያስሱ",
            "INDUSTRIAL & PRODUCTION": "ኢንዱስትሪና ምርት",
            "DOBiz Manufacturing": "ዶቢዝ ምርት",
            "Multi-stage BOM & Recipe costing": "ባለ ብዙ ደረጃ BOM እና የምግብ ዋጋ",
            "Scrap, yield & QA inspection control": "ቆሻሻ፣ ምርትና የጥራት ቁጥጥር",
            "Predictive machine maintenance with AI": "በAI የሚተነበይ የማሽን ጥገና",
            "Explore DOBiz Manufacturing": "ዶቢዝ ምርትን ያስሱ",
            "RESTAURANTS & HOTELS": "ምግብ ቤቶችና ሆቴሎች",
            "DOBiz Hospitality & POS": "ዶቢዝ እንግዳ ተቀባይነትና POS",
            "Fast-paced KDS order synchronization": "ፈጣን የKDS ትዕዛዝ ማመሳሰል",
            "Table reservation & billing split": "የጠረጴዛ ቀጠሮና የክፍያ ክፍፍል",
            "Daily revenue & shift reconciliations": "የዕለት ገቢና የፈረቃ ማስታረቅ",
            "Explore DOBiz Hospitality": "ዶቢዝ እንግዳ ተቀባይነትን ያስሱ",
            "CLINICS & HOSPITALS": "ክሊኒኮችና ሆስፒታሎች",
            "DOBiz Healthcare & HMS": "ዶቢዝ ጤናና HMS",
            "Patient intake & digital doctor prescriptions": "የታካሚ ቅበላና ዲጂታል የዶክተር መድኃኒት ማዘዣ",
            "Pharmacy batch expiry tracking": "የፋርማሲ ባች ማብቂያ ክትትል",
            "BizBooking integration for appointments": "ለቀጠሮዎች የቢዝቡኪንግ ውህደት",
            "Explore DOBiz Healthcare": "ዶቢዝ ጤናን ያስሱ",
            "SCHOOLS & UNIVERSITIES": "ትምህርት ቤቶችና ዩኒቨርሲቲዎች",
            "DOBiz Education ERP": "ዶቢዝ የትምህርት ኢአርፒ",
            "Automated term fee & penalty tracking": "ራስ-ሰር የሴሚስተር ክፍያና ቅጣት ክትትል",
            "Student gradebook & report cards": "የተማሪ ውጤት መዝገብና ሪፖርት ካርድ",
            "Staff attendance & payroll ledger": "የሠራተኛ መገኘትና የደመወዝ መዝገብ",
            "Explore DOBiz Education": "ዶቢዝ ትምህርትን ያስሱ",
            "PROPERTY & CONSTRUCTION": "ንብረትና ግንባታ",
            "DOBiz Real Estate": "ዶቢዝ ሪል እስቴት",
            "Unit rental cycles & automated billing": "የክፍል ኪራይ ዑደትና ራስ-ሰር ክፍያ",
            "Site contractor expense management": "የጣቢያ ኮንትራክተር ወጪ አስተዳደር",
            "BizMap geospatial property tags": "የቢዝማፕ ጂኦስፓሻል የንብረት መለያዎች",
            "Explore DOBiz Real Estate": "ዶቢዝ ሪል እስቴትን ያስሱ",
            "FARMING & AGRIBUSINESS": "እርሻና አግሮ-ቢዝነስ",
            "DOBiz Agriculture": "ዶቢዝ እርሻ",
            "Seed, fertilizer & harvest yield ledger": "የዘር፣ ማዳበሪያና ምርት መዝገብ",
            "Cooperative member accounts & dividend": "የህብረት ሥራ ማኅበር አባል ሂሳብና ትርፍ ድርሻ",
            "Direct connection to Dikko Shop wholesale": "ከዲኮ ሾፕ ጅምላ ጋር ቀጥታ ግንኙነት",
            "Explore DOBiz Agriculture": "ዶቢዝ እርሻን ያስሱ",
            "LOGISTICS & FLEET": "ሎጂስቲክስና ተሽከርካሪ",
            "DOBiz Transportation": "ዶቢዝ ትራንስፖርት",
            "Route dispatch & waybill generation": "የመንገድ ስርጭትና የወጪ ደረሰኝ ማመንጨት",
            "Fuel efficiency tracking per kilometer": "በኪሎሜትር የነዳጅ ቅልጥፍና ክትትል",
            "Automated insurance & service renewal alerts": "ራስ-ሰር የመድንና የአገልግሎት እድሳት ማሳወቂያ",
            "Explore DOBiz Transportation": "ዶቢዝ ትራንስፖርትን ያስሱ",
            "TEST DOBIZ LIVE ACCESS": "ዶቢዝን በቀጥታ ይሞክሩ",
            "Test DOBiz SmartERP in Real-Time": "ዶቢዝ ስማርት ኢአርፒን በቀጥታ ይሞክሩ",
            "Default DOBiz:": "ነባሪ ዶቢዝ፡",
            "Full Enterprise Cloud Suite": "ሙሉ የድርጅት ደመና ስብስብ",
            "Username:": "የተጠቃሚ ስም፡",
            "Copy": "ቅዳ",
            "Password:": "የይለፍ ቃል፡",
            "Access Mode:": "የመዳረሻ ዐውድ፡",
            "Interactive Admin / Cashier": "በይነተገናኝ አስተዳዳሪ / ገንዘብ ተቀባይ",
            "Login to Test": "ለመሞከር ይግቡ",
            "Sign Up for DOBiz": "ለዶቢዝ ይመዝገቡ",
            "Need Custom Implementation?": "ብጁ ትግበራ ይፈልጋሉ?",
            "Speak directly with our senior ERP architect in Addis Ababa, Hawassa, or Harar:": "በአዲስ አበባ፣ ሐዋሳ ወይም ሐረር ከሚገኘው ከመጀመሪያ ደረጃ የERP አርክቴክታችን ጋር በቀጥታ ይነጋገሩ፡",
            "Call for Consultation": "ለምክክር ይደውሉ",
            "SOVEREIGN BUSINESS INTELLIGENCE": "ሉዓላዊ የቢዝነስ ኢንተለጀንስ",
            "Meet Hadeeda — Your Ethiopian AI Copilot": "ሐዲዳን ያግኙ — የእርስዎ ኢትዮጵያዊ AI አጋዥ",
            "Meet Hadeeda": "ሐዲዳን ያግኙ",
            "Executive Assistant & Ops": "የሥራ አስፈጻሚ አጋዥና ሥራዎች",
            "Financial Ledger & Tax Copilot": "የፋይናንስ መዝገብና የግብር አጋዥ",
            "Stock & Reorder Supervisor": "የክምችትና ትዕዛዝ ተቆጣጣሪ",
            "BizMap & Geo-Campaigner": "ቢዝማፕና ጂኦ-ዘመቻ",
            "Ready to Elevate Your Business Prosperity?": "የንግድዎን ብልጽግና ለማሳደግ ዝግጁ ነዎት?",
            "Start DOBiz Signup": "የዶቢዝ ምዝገባ ይጀምሩ",
            "Book a Demo Session": "የማሳያ ክፍለ ጊዜ ይያዙ",
            "Rooted in Ethiopian Heritage. Built for Global Integrity.": "በኢትዮጵያ ቅርስ ላይ የተመሠረተ። ለዓለም አቀፍ ታማኝነት የተገነባ።",
            "Rooted in Ethiopian Heritage. Built for Humanity.": "በኢትዮጵያ ቅርስ ላይ የተመሠረተ። ለሰብአዊነት የተገነባ።",
            "Magala Ecosystem Pillar III": "የመጋላ ስነ-ምህዳር ሦስተኛው ምሰሶ",

            // ============================================================
            // DAGU — KNOWLEDGE PILLAR
            // ============================================================
            "CONNECTING MINDS & WISDOM INSHA'ALLAH...": "አእምሮንና ጥበብን እናገናኛለን ኢንሻአላህ...",
            "PILLAR II: MIND": "ሁለተኛው ምሰሶ፡ አእምሮ",
            "The Internet of Truth & Verified Academy": "የእውነት ኢንተርኔትና የተረጋገጠ አካዳሚ",
            "Become an Instructor": "አሠልጣኝ ይሁኑ",
            "THE SECOND PILLAR OF ETHIOBIZ • KNOWLEDGE OF THE MIND": "የኢትዮቢዝ ሁለተኛው ምሰሶ • የአእምሮ እውቀት",
            "What have your eyes seen?": "ዓይኖችዎ ምን አዩ?",
            "Explore Dagu Courses": "የዳጉ ኮርሶችን ያስሱ",
            "Register as Instructor": "እንደ አሠልጣኝ ይመዝገቡ",
            "The Dagu Roots": "የዳጉ ሥሮች",
            "KNOWLEDGE IS A JOURNEY": "እውቀት ጉዞ ነው",
            "Turn Your Knowledge Into Opportunity": "እውቀትዎን ወደ ዕድል ይቀይሩ",
            "Publish Free or Paid Content:": "ነፃ ወይም የሚከፈልበት ይዘት ያትሙ፡",
            "Join a Verified Network:": "የተረጋገጠ መረብን ይቀላቀሉ፡",
            "Register as a Dagu Instructor": "እንደ ዳጉ አሠልጣኝ ይመዝገቡ",
            "Browse Catalog": "ካታሎግ ይመልከቱ",
            "Join the Dagu Faculty": "የዳጉ መምህራን ቡድንን ይቀላቀሉ",
            "Deliver certified courses in tech, DOBiz ERP, trade, agribusiness, accounting, and healthcare.": "በቴክኖሎጂ፣ ዶቢዝ ERP፣ ንግድ፣ አግሮ-ቢዝነስ፣ ሒሳብና ጤና የተረጋገጡ ኮርሶችን ያስተምሩ።",
            "Start Instructor Application": "የአሠልጣኝ ማመልከቻ ይጀምሩ",
            "Have questions about instructor onboarding?": "ስለ አሠልጣኝ ምዝገባ ጥያቄ አለዎት?",
            "THE SACRED ROOTS OF DAGU": "የዳጉ ቅዱሳን ሥሮች",
            "The Ancestral Internet of Truth": "የቀድሞዎቹ የእውነት ኢንተርኔት",
            "Seen & Heard": "የታየና የተሰማ",
            "Shared Responsibility": "የጋራ ኃላፊነት",
            "Verified Wisdom": "የተረጋገጠ ጥበብ",
            "THE DIGITAL EVOLUTION": "የዲጂታል ዝግመተ ለውጥ",
            "Dagu Learning Center & LMS": "የዳጉ የትምህርት ማዕከልና LMS",
            "Explore LMS Academy": "የLMS አካዳሚን ያስሱ",
            "CERTIFIED PATHWAYS": "የተረጋገጡ መንገዶች",
            "Curated Wisdom Paths": "የተመረጡ የጥበብ መንገዶች",
            "Gain practical, market-ready competencies designed to empower the modern Ethiopian workforce InSha'Allah.": "ዘመናዊውን የኢትዮጵያ የሠራተኛ ኃይል ለማብቃት የተነደፉ ተግባራዊና ለገበያ ዝግጁ ችሎታዎችን ያግኙ ኢንሻአላህ።",
            "DOBiz Certified": "የዶቢዝ የተረጋገጠ",
            "DOBiz SmartERP Mastery": "የዶቢዝ ስማርት ኢአርፒ ብቃት",
            "View Syllabus": "ስርዓተ ትምህርቱን ይመልከቱ",
            "Growth & Trade": "ዕድገትና ንግድ",
            "Digital Commerce & Retail Operations": "ዲጂታል ንግድና የችርቻሮ ሥራዎች",
            "Finance & Tax": "ፋይናንስና ግብር",
            "Managerial Accounting & Compliance": "የአስተዳደር ሒሳብና ተገዢነት",
            "Enlighten the World With Your Knowledge": "በእውቀትዎ ዓለሙን ያብሩ",
            "Register as Dagu Instructor": "እንደ ዳጉ አሠልጣኝ ይመዝገቡ",
            "Dagu Knowledge of the Mind Pillar II": "ዳጉ የአእምሮ እውቀት ሁለተኛው ምሰሶ",

            // ============================================================
            // DOBiz SMARTERP PRODUCT PAGES
            // ============================================================
            "Manage · Grow · Connect": "ያስተዳድሩ · ያድጉ · ይገናኙ",
            "Why DOBiz": "ለምን ዶቢዝ",
            "Modules": "ሞጁሎች",
            "Industries": "ኢንዱስትሪዎች",
            "FAQ": "ተደጋጋሚ ጥያቄዎች",
            "Smarter.": "የበለጠ ብልህ።",
            "one intelligent business system": "አንድ ብልህ የንግድ ሥርዓት",
            "Start Your Business Journey": "የንግድ ጉዞዎን ይጀምሩ",
            "Explore DOBiz": "ዶቢዝን ያስሱ",
            "One Platform": "አንድ መድረክ",
            "One Source of Truth": "አንድ የእውነት ምንጭ",
            "Cloud Ready": "ደመና ዝግጁ",
            "Intelligent": "ብልህ",
            "Business Overview": "የንግድ አጠቃላይ እይታ",
            "Sales": "ሽያጭ",
            "Orders": "ትዕዛዞች",
            "Customers": "ደንበኞች",
            "Your intelligent business assistant, always here to help.": "ብልህ የንግድ አጋዥዎ፣ ሁልጊዜ ለመርዳት ዝግጁ።",
            "ERP": "ኢአርፒ",
            "One Integrated Platform": "አንድ የተዋሃደ መድረክ",
            "Cloud Business Access": "የደመና የንግድ መዳረሻ",
            "Intelligent Assistance": "ብልህ ድጋፍ",
            "Built to Scale": "ለማስፋፋት የተገነባ",
            "MORE OPPORTUNITIES FOR YOUR BUSINESS": "ለንግድዎ ተጨማሪ ዕድሎች",
            "Sell More. Hire Smarter. All from DOBiz.": "በየበለጠ ይሽጡ። በብልህነት ይቅጠሩ። ሁሉም ከዶቢዝ።",
            "Sell Your Products & Services to a Wider Audience": "ምርቶችዎንና አገልግሎቶችዎን ለሰፊ ተመልካቾች ይሽጡ",
            "Publish your products and services directly from DOBiz to Dikko Shop and reach thousands of customers online.": "ምርቶችዎንና አገልግሎቶችዎን ከዶቢዝ በቀጥታ ወደ ዲኮ ሾፕ ያትሙ እና በመስመር ላይ ሺዎች ደንበኞችን ያግኙ።",
            "From DOBiz to Dikko Shop": "ከዶቢዝ ወደ ዲኮ ሾፕ",
            "Go to Dikko Shop": "ወደ ዲኮ ሾፕ ይሂዱ",
            "Find the Right People for Your Team": "ለቡድንዎ ትክክለኛውን ሰዎች ያግኙ",
            "From DOBiz to Oosoo Jobs": "ከዶቢዝ ወደ ኡሱ ሥራዎች",
            "We're Hiring!": "እኛ እንቀጥራለን!",
            "Post Job from DOBiz": "ከዶቢዝ ሥራ ያትሙ",
            "Go to Oosoo Jobs": "ወደ ኡሱ ሥራዎች ይሂዱ",
            "BUILT FOR YOUR INDUSTRY": "ለኢንዱስትሪዎ የተገነባ",
            "DOBiz Solutions for Every Sector": "ለሁሉም ዘርፍ የዶቢዝ መፍትሄዎች",
            "Tailored features and workflows for different business needs.": "ለተለያዩ የንግድ ፍላጎቶች የተዘጋጁ ባህሪያትና የሥራ ፍሰቶች።",
            "DOBiz Retail": "ዶቢዝ ግብይት",
            "Retail, POS, inventory and sales management.": "ችርቻሮ፣ POS፣ ክምችትና ሽያጭ አስተዳደር።",
            "Explore Retail": "ችርቻሮን ያስሱ",
            "DOBiz Service": "ዶቢዝ አገልግሎት",
            "Service delivery, projects, customers and billing.": "የአገልግሎት አሰጣጥ፣ ፕሮጀክቶች፣ ደንበኞችና ክፍያ።",
            "Explore Service": "አገልግሎትን ያስሱ",
            "Production, materials, work orders and control.": "ምርት፣ ቁሳቁሶች፣ የሥራ ትዕዛዞችና ቁጥጥር።",
            "Explore Manufacturing": "ምርትን ያስሱ",
            "DOBiz Education": "ዶቢዝ ትምህርት",
            "Educational administration, people and finance.": "የትምህርት አስተዳደር፣ ሰዎችና ፋይናንስ።",
            "Explore Education": "ትምህርትን ያስሱ",
            "DOBiz Health": "ዶቢዝ ጤና",
            "Healthcare operations, patients and services.": "የጤና ሥራዎች፣ ታካሚዎችና አገልግሎቶች።",
            "Explore Health": "ጤናን ያስሱ",
            "GET STARTED": "ይጀምሩ",
            "From setup to smarter business.": "ከማዋቀር እስከ ብልህ ንግድ።",
            "Start with what you need today and expand as your business grows.": "ዛሬ የሚፈልጉትን ይጀምሩ እና ንግድዎ እያደገ ሲሄድ ያስፋፉ።",
            "Create Your Business": "ንግድዎን ይፍጠሩ",
            "Set up your organization and establish your business environment.": "ድርጅትዎን ያዋቅሩ እና የንግድ አካባቢዎን ይመስርቱ።",
            "Configure Your Modules": "ሞጁሎችዎን ያዋቅሩ",
            "Activate and configure the business functions you need.": "የሚፈልጉትን የንግድ ተግባራት ያንቁ እና ያዋቅሩ።",
            "Bring Your Data": "ውሂብዎን ያምጡ",
            "Organize customers, items, suppliers, accounts and operational data.": "ደንበኞችን፣ ዕቃዎችን፣ አቅራቢዎችን፣ ሂሳቦችንና የሥራ ውሂብን ያደራጁ።",
            "Run Smarter": "በብልህነት ያስኬዱ",
            "Operate, monitor, automate and grow from one connected platform.": "ከአንድ የተገናኘ መድረክ ያስኬዱ፣ ይከታተሉ፣ በራስ-ሰር ያካሂዱ እና ያድጉ።",
            "READY TO TRANSFORM YOUR BUSINESS?": "ንግድዎን ለመለወጥ ዝግጁ ነዎት?",
            "Build your business on DOBiz SmartERP.": "ንግድዎን በዶቢዝ ስማርት ኢአርፒ ላይ ይገንቡ።",
            "Login to DOBiz": "ወደ ዶቢዝ ይግቡ",
            "Frequently asked questions.": "ተደጋጋሚ ጥያቄዎች።",
            "Platform": "መድረክ",
            "Solutions": "መፍትሄዎች",
            "A Biz Technology Solutions Product.": "የቢዝ ቴክኖሎጂ ሶሉሽንስ ምርት።",

            // ============================================================
            // WALTA — SUPPORT PILLAR
            // ============================================================
            "WALTA": "ዋልታ",
            "YOUR SHIELD OF SUPPORT...": "የድጋፍ ጋሻዎ...",
            "THE FOURTH PILLAR OF ETHIOBIZ • SHIELD OF ASSISTANCE": "የኢትዮቢዝ አራተኛው ምሰሶ • የእርዳታ ጋሻ",
            "Sovereign Protection & Helpdesk": "ሉዓላዊ ጥበቃና የድጋፍ ጠረጴዛ",
            "Bismillah, how can we help your business thrive?": "ቢስሚላህ፣ ንግድዎ እንዲያብብ እንዴት ልንረዳው እንችላለን?",
            "Open Support Ticket": "የድጋፍ ትኬት ይክፈቱ",
            "Walta Forum": "የዋልታ መድረክ",
            "Explore Channels": "ሰርጦችን ያስሱ",
            "SOVEREIGN RESOLUTION CHANNELS": "ሉዓላዊ የመፍትሄ ሰርጦች",
            "Comprehensive Enterprise Support": "ሁሉን አቀፍ የድርጅት ድጋፍ",
            "Select your preferred pathway for technical guidance, bug resolution, or community collaboration.": "ለቴክኒካዊ መመሪያ፣ ለስህተት መፍትሄ ወይም ለማኅበረሰብ ትብብር የሚመርጡትን መንገድ ይምረጡ።",
            "Formal Ticketing System": "መደበኛ የትኬት ሥርዓት",
            "Open a dedicated support ticket for technical bugs, or module configuration requests with SLA guarantees.": "ለቴክኒካዊ ስህተቶች ወይም ከSLA ዋስትና ጋር ለሞጁል ማዋቀሪያ ጥያቄዎች የተዘጋጀ የድጋፍ ትኬት ይክፈቱ።",
            "Knowledge Base & Docs": "የእውቀት መሠረትና ሰነዶች",
            "Browse Documentation": "ሰነዶችን ይመልከቱ",
            "Walta Community Forum": "የዋልታ ማኅበረሰብ መድረክ",
            "Join Community Forum": "የማኅበረሰብ መድረኩን ይቀላቀሉ",
            "Hadeeda BizAI Assistant": "የሐዲዳ BizAI አጋዥ",
            "Chat with Hadeeda": "ከሐዲዳ ጋር ይወያዩ",
            "DIRECT ENGINEER ACCESS": "ቀጥታ የኢንጂነር መዳረሻ",
            "Urgent Direct Contact": "አስቸኳይ ቀጥታ ግንኙነት",
            "Connect directly with our senior cloud infrastructure team for critical system emergencies InSha'Allah.": "ለወሳኝ የስርዓት አደጋዎች ከመጀመሪያ ደረጃ የደመና መሠረተ ልማት ቡድናችን ጋር በቀጥታ ይገናኙ ኢንሻአላህ።",
            "Email Helpdesk": "የኢሜይል ድጋፍ",
            "Direct Hotline": "ቀጥታ መስመር",
            "Official Telegram": "ኦፊሴላዊ ቴሌግራም",
            "Average Response Time": "አማካይ የምላሽ ጊዜ",
            "Under 2 Hours": "ከ2 ሰዓት በታች",
            "Protected by Walta": "በዋልታ የተጠበቀ",

            // ============================================================
            // AFOCHA — COMMUNITY PILLAR
            // ============================================================
            "AFOCHA": "አፎቻ",
            "CONNECTING HEARTS & HUMANITY...": "ልቦችንና ሰብአዊነትን እናገናኛለን...",
            "THE FIFTH PILLAR OF ETHIOBIZ • LOVE & COMMUNITY": "የኢትዮቢዝ አምስተኛው ምሰሶ • ፍቅርና ማኅበረሰብ",
            "Family & Sovereign Heart.": "ቤተሰብና ሉዓላዊ ልብ።",
            "Open Afocha Social Feed": "የአፎቻ ማኅበራዊ ዥረት ይክፈቱ",
            "The Afocha Circle": "የአፎቻ ክበብ",
            "THE SPIRIT OF MUTUAL AID": "የጋራ እርዳታ መንፈስ",
            "The Circle of Community": "የማኅበረሰብ ክበብ",
            "The traditional Ethiopian spirit of Iddir and Afocha, digitized to unite our sovereign society InSha'Allah.": "የኢድርና የአፎቻ ባህላዊ የኢትዮጵያ መንፈስ፣ ሉዓላዊ ማኅበረሰባችንን ለማንደቅ በዲጂታል የተቀየረ ኢንሻአላህ።",
            "Shared Joy": "የጋራ ደስታ",
            "Shared Burden": "የጋራ ሸክም",
            "The Unbreakable Circle": "የማይሰበር ክበብ",
            "Global Afocha": "ዓለም አቀፍ አፎቻ",
            "DIGITAL TOOLS FOR UNITY": "ለአንድነት ዲጂታል መሣሪያዎች",
            "Building Sovereign Community": "ሉዓላዊ ማኅበረሰብን መገንባት",
            "Practical digital features to connect, support, and grow our Ethiopian family worldwide.": "የኢትዮጵያ ቤተሰባችንን በዓለም አቀፍ ደረጃ ለማገናኘት፣ ለመደገፍና ለማሳደግ ተግባራዊ ዲጂታል ባህሪያት።",
            "LIVE NOW": "አሁን በቀጥታ",
            "Afocha Social Feed": "የአፎቻ ማኅበራዊ ዥረት",
            "Explore Social Stream": "ማኅበራዊ ዥረቱን ያስሱ",
            "COMING SOON": "በቅርቡ",
            "Volunteer Network": "የበጎ ፈቃደኞች መረብ",
            "In Active Development": "በንቃት እየተሠራ ነው",
            "Digital Iddir & Mutual Aid": "ዲጂታል ኢድርና የጋራ እርዳታ",
            "Traditional Ethiopian micro-insurance and mutual support systems, secured with sovereign cloud transparency.": "ባህላዊ የኢትዮጵያ ጥቃቅን መድንና የጋራ ድጋፍ ሥርዓቶች፣ በሉዓላዊ ደመና ግልጽነት የተጠበቁ።",
            "Cultural Gatherings & Festivals": "የባህል ስብሰባዎችና በዓላት",
            "Celebrate Ethiopia's rich cultural heritage through verified digital event schedules and community gatherings.": "የኢትዮጵያን የበለጸገ የባህል ቅርስ በተረጋገጡ ዲጂታል የዝግጅት መርሐግብሮችና የማኅበረሰብ ስብሰባዎች ያክብሩ።",
            "The Culmination of Human Flourishing": "የሰብአዊ ብልጽግና ጫፍ",
            "Join the Circle of Love & Enterprise": "የፍቅርና የንግድ ክበብን ይቀላቀሉ",
            "Enter Afocha Feed": "የአፎቻ ዥረት ይግቡ",
            "Join EthioBiz Cloud": "የኢትዮቢዝ ደመናን ይቀላቀሉ",

            // ============================================================
            // DOBiz SIGNUP — ONBOARDING PORTAL
            // ============================================================
            "OFFICIAL ONBOARDING PORTAL": "ኦፊሴላዊ የምዝገባ ፖርታል",
            "DOBiz Smart ERP Self-Service Signup": "የዶቢዝ ስማርት ERP ራስ-አገልግሎት ምዝገባ",
            "Discover Features: To know more about DOBiz SmartERP, explore our full product overview:": "ባህሪያትን ያግኙ፡ ስለ ዶቢዝ ስማርት ኢአርፒ የበለጠ ለማወቅ ሙሉ የምርት አጠቃላይ እይታችንን ያስሱ፡",
            "Explore DOBiz ERP": "ዶቢዝ ERPን ያስሱ",
            "Self-Help Tutorials: To learn DOBiz SmartERP, checkout our step-by-step video courses:": "የራስ-እርዳታ ትምህርቶች፡ ዶቢዝ ስማርት ኢአርፒን ለመማር ደረጃ በደረጃ የቪዲዮ ኮርሶቻችንን ይመልከቱ፡",
            "Open User Guide": "የተጠቃሚ መመሪያ ይክፈቱ",
            "Select Your Industry Vertical": "የኢንዱስትሪ ዘርፍዎን ይምረጡ",
            "Choose Your Subscription Package": "የደንበኝነት ጥቅልዎን ይምረጡ",
            "/ month": "/ በወር",
            "Up to 3 Active Users": "እስከ 3 ንቁ ተጠቃሚዎች",
            "Single module tier ideal for micro-businesses starting their digital journey.": "ዲጂታል ጉዞቸውን ለሚጀምሩ ጥቃቅን ንግዶች ተስማሚ የአንድ ሞጁል ደረጃ።",
            "Finance & Accounting": "ፋይናንስና ሒሳብ",
            "Inventory & Point of Sale": "ክምችትና የሽያጭ ነጥብ",
            "HR & Payroll": "የሰው ኃይልና ደመወዝ",
            "1 Selected Core Module (Finance OR Inventory OR HR)": "1 የተመረጠ ዋና ሞጁል (ፋይናንስ ወይም ክምችት ወይም ሰው ኃይል)",
            "Amharic & English Interface": "የአማርኛና እንግሊዝኛ በይነገጽ",
            "Local Tax & Billing Compliance": "የአገር ውስጥ ግብርና የክፍያ ተገዢነት",
            "Standard Email & Phone Support": "መደበኛ የኢሜይልና ስልክ ድጋፍ",
            "EthioBiz Shop Product Publishing": "የኢትዮቢዝ ሾፕ ምርት ማተም",
            "Show all features": "ሁሉንም ባህሪያት ይመልከቱ",
            "MOST POPULAR": "በጣም ተወዳጅ",
            "Up to 10 Active Users": "እስከ 10 ንቁ ተጠቃሚዎች",
            "Multi-module operational suite for growing enterprises and multi-branch operations.": "ለሚያድጉ ድርጅቶችና ለብዙ ቅርንጫፍ ሥራዎች የብዙ ሞጁል የሥራ ስብስብ።",
            "Industry Module of Your Choice": "የመረጡት የኢንዱስትሪ ሞጁል",
            "3 Selected DOBiz ERP Modules": "3 የተመረጡ የዶቢዝ ERP ሞጁሎች",
            "Full Financials & Inventory Control": "ሙሉ ፋይናንስና የክምችት ቁጥጥር",
            "BEST VALUE (15K FULL)": "ምርጥ ዋጋ (15ሺ ሙሉ)",
            "Unlimited Active Users": "ያልተገደቡ ንቁ ተጠቃሚዎች",
            "Complete all-in-one DOBiz SmartERP suite with full dedicated industry modules.": "ሙሉ የተዘጋጁ የኢንዱስትሪ ሞጁሎች ያሉት ሁሉን አቀፍ የዶቢዝ ስማርት ኢአርፒ ስብስብ።",
            "All 12 Industry Modules": "ሁሉም 12 የኢንዱስትሪ ሞጁሎች",
            "ALL DOBiz Core & Industry Modules": "ሁሉም የዶቢዝ ዋናና የኢንዱስትሪ ሞጁሎች",
            "Unlimited Staff Users": "ያልተገደቡ የሠራተኛ ተጠቃሚዎች",
            "Multi-Branch & Multi-Company Support": "የብዙ ቅርንጫፍና የብዙ ኩባንያ ድጋፍ",
            "Select Billing Term (1-12 Months) & Receive Instant Discounts": "የክፍያ ጊዜ ይምረጡ (1-12 ወራት) እና ፈጣን ቅናሾችን ያግኙ",
            "Select Subscription Term (Months):": "የደንበኝነት ጊዜ ይምረጡ (ወራት)፡",
            "months": "ወራት",
            "month": "ወር",
            "3 Months": "3 ወራት",
            "Standard Term": "መደበኛ ጊዜ",
            "6 Months": "6 ወራት",
            "Save 10% Off": "10% ቅናሽ",
            "1 Year (12 Mo)": "1 ዓመት (12 ወር)",
            "Save 20% Off": "20% ቅናሽ",
            "Coupon Code (Optional)": "የኩፖን ኮድ (አማራጭ)",
            "Enter Enterprise & Contact Information": "የድርጅትና የመገኛ መረጃ ያስገቡ",
            "Full Name": "ሙሉ ስም",
            "Last Name": "የአባት ስም",
            "Official Business Email": "ኦፊሴላዊ የንግድ ኢሜይል",
            "Work Email": "የሥራ ኢሜይል",
            "Phone Number": "ስልክ ቁጥር",
            "Company / Organization Legal Name": "የኩባንያ / ድርጅት ሕጋዊ ስም",
            "Your Role": "የእርስዎ ሚና",
            "Settlement & Payment": "ክፍያና ማስታረቅ",
            "Pay Online (AddisPay) Card, Telebirr, CBE Birr, Bank Apps": "በመስመር ላይ ይክፈሉ (AddisPay) ካርድ፣ ቴሌብር፣ CBE ብር፣ የባንክ መተግባሪያዎች",
            "Bank Transfer Manual transfer + proof upload": "የባንክ ዝውውር በእጅ ዝውውር + ማስረጃ ስቀል",
            "Pay securely online via AddisPay": "በAddisPay በደህንነት በመስመር ላይ ይክፈሉ",
            "After registration you will be redirected to the AddisPay secure checkout. Supports:": "ከምዝገባ በኋላ ወደ AddisPay አስተማማኝ ክፍያ ገጽ ይዛወራሉ። የሚደግፋቸው፡",
            "Please transfer the total subscription investment to the verified settlement accounts below:": "እባክዎ ጠቅላላ የደንበኝነት ክፍያውን ከታች ወደተረጋገጡት የማስታረቂያ ሂሳቦች ያስተላልፉ፡",
            "Payment Reference / Transaction ID (Optional)": "የክፍያ ማጣቀሻ / የግብይት መለያ (አማራጭ)",
            "Bank Channel Used": "የተጠቀመው የባንክ መስመር",
            "Other Bank": "ሌላ ባንክ",
            "Other": "ሌላ",
            "Complete Registration & Provision Tenant": "ምዝገባን ጨርስ እና ተከራይ አዘጋጅ",
            "Registration Complete Alhamdulillah!": "ምዝገባ ተጠናቅቋል አልሐምዱሊላህ!",
            "Registered Name:": "የተመዘገበ ስም፡",
            "Login Email:": "የመግቢያ ኢሜይል፡",
            "Phone:": "ስልክ፡",
            "Signup Reference:": "የምዝገባ ማጣቀሻ፡",
            "Company:": "ኩባንያ፡",
            "Industry Edition:": "የኢንዱስትሪ ዕትም፡",
            "Selected Package:": "የተመረጠ ጥቅል፡",
            "Billing Term:": "የክፍያ ጊዜ፡",
            "Discount Applied:": "የተተገበረ ቅናሽ፡",
            "Coupon Discount:": "የኩፖን ቅናሽ፡",
            "Launch Offer:": "የምረቃ ቅናሽ፡",
            "Settlement Amount:": "የማስታረቂያ መጠን፡",
            "Account Status:": "የመለያ ሁኔታ፡",
            "Set Password & Login": "የይለፍ ቃል ያስቀምጡ እና ይግቡ",
            "View User Guide & Tutorials": "የተጠቃሚ መመሪያና ትምህርቶችን ይመልከቱ",
            "Product Overview": "የምርት አጠቃላይ እይታ",
            "Select Bank / Wallet": "ባንክ / ዋሌት ይምረጡ",

            // ============================================================
            // TRIAL WEB FORM
            // ============================================================
            "Industry": "ኢንዱስትሪ",
            "Trial Management": "የሙከራ አስተዳደር",
            "Status": "ሁኔታ",
            "Trial Start Date": "የሙከራ መጀመሪያ ቀን",
            "Company": "ኩባንያ",
            "Pending": "በመጠበቅ ላይ",
            "Trial Active": "ሙከራ ንቁ",
            "Converted": "የተቀየረ",
            "Expired": "ጊዜው ያለፈ",
            "Healthcare & Clinics": "ጤናና ክሊኒኮች",
            "Hotels & Hospitality": "ሆቴሎችና እንግዳ ተቀባይነት",
            "Restaurants & Food Service": "ምግብ ቤቶችና የምግብ አገልግሎት",
            "Real Estate & Property": "ሪል እስቴትና ንብረት",
            "Retail & Wholesale": "ችርቻሮና ጅምላ",
            "Manufacturing & Assembly": "ምርትና ስብሰባ",
            "Education & Schools": "ትምህርትና ትምህርት ቤቶች",
            "Non-Profit & NGOs": "ለትርፍ ያልተቋቋሙና መንግሥታዊ ያልሆኑ ድርጅቶች",
            "Professional Services": "ሙያዊ አገልግሎቶች",
            "Transportation & Logistics": "ትራንስፖርትና ሎጂስቲክስ",
            "Agriculture": "እርሻ",
            "Construction": "ግንባታ",
            "Government": "መንግሥት",
            "Non-Profit": "ለትርፍ ያልተቋቋመ",
            "Property Management": "የንብረት አስተዳደር",
            "Hotel Management": "የሆቴል አስተዳደር",
            "Restaurant": "ምግብ ቤት",
            "Maintenance": "ጥገና",
            "Healthcare & Clinic": "ጤናና ክሊኒክ",
            "Hotel & Hospitality": "ሆቴልና እንግዳ ተቀባይነት",
            "Restaurant & POS": "ምግብ ቤትና POS",
            "Property & Real Estate": "ንብረትና ሪል እስቴት",
            "Transportation & Fleet": "ትራንስፖርትና ተሽከርካሪ",
            "Agriculture & Agribusiness": "እርሻና አግሮ-ቢዝነስ",
            "Construction & Engineering": "ግንባታና ምህንድስና",
            "Logistics & Warehouse": "ሎጂስቲክስና መጋዘን",
            "Government & Public-Interest": "መንግሥትና የሕዝብ ጥቅም",
            "Maintenance & Repair": "ጥገናና ጥገና ሥራ",
            "Logistics": "ሎጂስቲክስ",
            "Transportation": "ትራንስፖርት",
            "Healthcare": "ጤና",
            "Education": "ትምህርት",
            "Manufacturing": "ምርት",
            "Government & Public Sector": "መንግሥትና የሕዝብ ዘርፍ"
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
    let welcomeModalShown = false;

    function setLangCookie(lang) {
        try {
            document.cookie = 'preferred_language=' + lang + ';path=/;max-age=31536000;SameSite=Lax';
        } catch (e) {}
    }

    function getLangCookie() {
        try {
            const m = document.cookie.match(/(?:^|;\s*)preferred_language=([^;]+)/);
            return m ? decodeURIComponent(m[1]) : '';
        } catch (e) { return ''; }
    }

    function syncUserLanguage(lang) {
        // Guests keep their preference locally; authenticated members persist
        // it to Frappe's tabUser.language so every device/session agrees.
        try {
            const user = (window.frappe && frappe.session && frappe.session.user) || '';
            if (!user || user === 'Guest') return;
            const token = (window.frappe && (frappe.csrf_token || (frappe.boot && frappe.boot.csrf_token))) || '';
            fetch('/api/method/bismillah_ethiobiz.api.set_user_language', {
                method: 'POST',
                credentials: 'same-origin',
                headers: { 'Content-Type': 'application/json', 'X-Frappe-CSRF-Token': token },
                body: JSON.stringify({ lang: lang })
            }).catch(function () {});
        } catch (e) {}
    }

    function applyLanguageState(lang) {
        currentLang = (lang === 'am') ? 'am' : 'en';
        document.documentElement.lang = currentLang;
        applyTranslations();
        updateToggleButtons();
    }

    function setLanguage(lang, opts) {
        opts = opts || {};
        applyLanguageState(lang);

        if (opts.persist !== false) {
            try {
                localStorage.setItem('ethiobiz_lang', currentLang);
                if (opts.userInitiated) localStorage.setItem('ethiobiz_lang_chosen', 'true');
            } catch (e) {}
            setLangCookie(currentLang);
        }

        if (opts.userInitiated) syncUserLanguage(currentLang);

        if (opts.silent) return;

        // Dispatch events for all page scripts (home has its own dictionary and
        // listens for this event so both engines stay in lock-step).
        window.dispatchEvent(new CustomEvent('ethiobiz-lang-changed', { detail: { lang: currentLang } }));
        window.dispatchEvent(new CustomEvent('ethiobiz:lang_changed', { detail: { lang: currentLang } }));
        document.dispatchEvent(new CustomEvent('ethiobiz-lang-changed', { detail: { lang: currentLang } }));
    }

    // React to language changes fired by page-level engines (e.g. home.html)
    // without echoing the event back and creating a loop.
    window.addEventListener('ethiobiz-lang-changed', function (e) {
        const lang = e && e.detail && e.detail.lang;
        if ((lang === 'am' || lang === 'en') && lang !== currentLang) {
            setLanguage(lang, { silent: true, persist: false });
        }
    });

    function closeWelcomeLanguageModal() {
        const overlay = document.getElementById('ethiobiz-welcome-lang-modal');
        if (!overlay) return;
        overlay.classList.add('is-closing');
        setTimeout(function () { overlay.remove(); }, 260);
    }

    function checkWelcomeLanguageModal() {
        if (welcomeModalShown) return;
        if (document.getElementById('ethiobiz-welcome-lang-modal')) return;

        // Respect an existing choice from either store, and never interrupt
        // transactional flows where a modal would be harmful.
        try {
            if (localStorage.getItem('ethiobiz_lang_chosen') === 'true') return;
        } catch (e) {}
        if (getLangCookie()) return;
        const path = (location.pathname || '').toLowerCase();
        if (/\/(cart|checkout|login|payment|dobiz-payment|magala-payment)/.test(path)) return;

        welcomeModalShown = true;

        if (!document.getElementById('ethiobiz-welcome-lang-style')) {
            const style = document.createElement('style');
            style.id = 'ethiobiz-welcome-lang-style';
            style.textContent = `
                #ethiobiz-welcome-lang-modal{position:fixed;inset:0;z-index:100000;display:flex;align-items:center;justify-content:center;padding:20px;background:rgba(4,20,24,.62);backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px);opacity:1;transition:opacity .25s ease;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Noto Sans Ethiopic",sans-serif}
                #ethiobiz-welcome-lang-modal.is-closing{opacity:0}
                #ethiobiz-welcome-lang-modal .ewlm-card{width:min(520px,100%);background:linear-gradient(150deg,#0b2b2f,#062024);border:1px solid rgba(94,234,212,.35);border-radius:22px;box-shadow:0 28px 80px rgba(0,0,0,.55);padding:30px 26px;text-align:center;color:#e8fffb}
                #ethiobiz-welcome-lang-modal .ewlm-globe{font-size:38px;line-height:1}
                #ethiobiz-welcome-lang-modal h2{margin:12px 0 4px;font-size:20px;font-weight:800;color:#fff}
                #ethiobiz-welcome-lang-modal p{margin:0 0 20px;font-size:13.5px;color:#9fd8cf;line-height:1.55}
                #ethiobiz-welcome-lang-modal .ewlm-options{display:grid;grid-template-columns:1fr 1fr;gap:14px}
                #ethiobiz-welcome-lang-modal .ewlm-option{cursor:pointer;border:1.5px solid rgba(94,234,212,.3);background:rgba(255,255,255,.06);border-radius:16px;padding:18px 10px;color:#eafffb;transition:all .18s ease;font:inherit}
                #ethiobiz-welcome-lang-modal .ewlm-option:hover,#ethiobiz-welcome-lang-modal .ewlm-option:focus-visible{border-color:#5eead4;background:rgba(94,234,212,.16);transform:translateY(-2px);outline:none}
                #ethiobiz-welcome-lang-modal .ewlm-flag{font-size:30px;display:block;margin-bottom:8px}
                #ethiobiz-welcome-lang-modal .ewlm-name{display:block;font-size:15px;font-weight:800}
                #ethiobiz-welcome-lang-modal .ewlm-native{display:block;font-size:12px;color:#7fc9c0;margin-top:3px}
                #ethiobiz-welcome-lang-modal .ewlm-skip{margin-top:18px;background:none;border:none;color:#8fbbb5;font-size:12px;cursor:pointer;text-decoration:underline}
                @media(max-width:420px){#ethiobiz-welcome-lang-modal .ewlm-options{grid-template-columns:1fr}}
            `;
            document.head.appendChild(style);
        }

        const overlay = document.createElement('div');
        overlay.id = 'ethiobiz-welcome-lang-modal';
        overlay.setAttribute('role', 'dialog');
        overlay.setAttribute('aria-modal', 'true');
        overlay.setAttribute('aria-label', 'Choose your language / ቋንቋ ይምረጡ');
        overlay.innerHTML = `
            <div class="ewlm-card">
                <div class="ewlm-globe" aria-hidden="true">🌐</div>
                <h2>Welcome to EthioBiz</h2>
                <p>እንኳን ወደ ኢትዮቢዝ በደህና መጡ<br>Please choose your preferred language · እባክዎ የሚመርጡትን ቋንቋ ይምረጡ</p>
                <div class="ewlm-options">
                    <button type="button" class="ewlm-option" data-ewlm-lang="en">
                        <span class="ewlm-flag" aria-hidden="true">🇬🇧</span>
                        <span class="ewlm-name">English</span>
                        <span class="ewlm-native">Continue in English</span>
                    </button>
                    <button type="button" class="ewlm-option" data-ewlm-lang="am">
                        <span class="ewlm-flag" aria-hidden="true">🇪🇹</span>
                        <span class="ewlm-name">አማርኛ</span>
                        <span class="ewlm-native">በአማርኛ ይቀጥሉ</span>
                    </button>
                </div>
                <button type="button" class="ewlm-skip" id="ewlm-skip">Continue with English</button>
            </div>
        `;
        document.body.appendChild(overlay);

        overlay.querySelectorAll('[data-ewlm-lang]').forEach(function (btn) {
            btn.addEventListener('click', function () {
                const lang = btn.getAttribute('data-ewlm-lang');
                try { localStorage.setItem('ethiobiz_lang_chosen', 'true'); } catch (e) {}
                setLanguage(lang, { userInitiated: true });
                closeWelcomeLanguageModal();
            });
        });
        const skip = overlay.querySelector('#ewlm-skip');
        if (skip) skip.addEventListener('click', function () {
            try { localStorage.setItem('ethiobiz_lang_chosen', 'true'); } catch (e) {}
            setLanguage('en', { userInitiated: true });
            closeWelcomeLanguageModal();
        });
        overlay.addEventListener('click', function (e) {
            if (e.target === overlay) {
                try { localStorage.setItem('ethiobiz_lang_chosen', 'true'); } catch (e) {}
                closeWelcomeLanguageModal();
            }
        });
    }


    let lowerMap = null;
    let applyingTranslations = false;
    let lastApplyAt = 0;

    function getLowerMap() {
        if (!lowerMap) {
            lowerMap = {};
            const am = DICTIONARY.am || {};
            Object.keys(am).forEach(function (k) {
                const lower = k.toLowerCase();
                if (!(lower in lowerMap)) lowerMap[lower] = am[k];
            });
        }
        return lowerMap;
    }

    // Strip emoji, arrows, bullets and decorative punctuation so the same
    // dictionary entry matches "Get Started", "GET STARTED →" and "🛍️ Get Started".
    function cleanKey(text) {
        if (!text) return '';
        let t = String(text).replace(/\u00a0/g, ' ');
        try {
            t = t.replace(/[\u{1F000}-\u{1FAFF}\u{2190}-\u{21FF}\u{2300}-\u{27BF}\u{2B00}-\u{2BFF}\u{FE0F}\u{200D}\u{20E3}]/gu, ' ');
        } catch (e) {
            t = t.replace(/[\u2190-\u21FF\u2300-\u27BF\u2B00-\u2BFF]/g, ' ');
        }
        t = t.replace(/[•·|►▶➔→←↗↘»«]/g, ' ')
             .replace(/\s+/g, ' ')
             .trim();
        t = t.replace(/^[\s\-–—:;,.]+/, '').replace(/[\s\-–—:;,]+$/, '');
        return t;
    }

    function lookupTranslation(text) {
        const dict = DICTIONARY.am || {};
        const lower = getLowerMap();
        const raw = String(text || '').replace(/\s+/g, ' ').trim();
        if (!raw) return '';

        if (dict[raw]) return dict[raw];
        const clean = cleanKey(raw);
        if (dict[clean]) return dict[clean];

        const rawLower = raw.toLowerCase();
        const cleanLower = clean.toLowerCase();
        if (lower[rawLower]) return lower[rawLower];
        if (lower[cleanLower]) return lower[cleanLower];

        const noDots = clean.replace(/[.…]+$/, '').trim();
        if (dict[noDots]) return dict[noDots];
        if (lower[noDots.toLowerCase()]) return lower[noDots.toLowerCase()];
        return '';
    }

    // Icons, SVGs and line breaks are decoration; keep them while replacing
    // only the human-readable label next to them.
    function isDecorativeNode(node) {
        if (!node || node.nodeType !== 1) return false;
        if (node.tagName === 'BR' || node.tagName === 'SVG') return true;
        return node.tagName === 'SPAN' && /icon/i.test(node.className || '');
    }

    function setTextPreservingDecor(el, text) {
        const keep = [];
        Array.prototype.forEach.call(el.childNodes, function (node) {
            if (isDecorativeNode(node)) keep.push(node);
        });
        el.textContent = '';
        keep.forEach(function (node) { el.appendChild(node); });
        if (text) {
            if (keep.length) el.appendChild(document.createTextNode(' ' + text));
            else el.textContent = text;
        }
    }

    function applyTranslations() {
        // Home owns a larger key-based dictionary (window.ethioBizTranslations).
        // Let home apply its own copy so the two dictionaries never fight over
        // the same elements; this engine still drives the navbar pill + modal.
        if (window.ethioBizTranslations) return;
        if (applyingTranslations) return;
        applyingTranslations = true;

        try {
            if (currentLang === 'en') {
                document.querySelectorAll('[data-i18n-orig]').forEach(el => {
                    if (el.hasAttribute('data-i18n-ph-orig')) return;
                    setTextPreservingDecor(el, el.getAttribute('data-i18n-orig'));
                });
                document.querySelectorAll('[data-i18n-ph-orig]').forEach(el => {
                    el.setAttribute('placeholder', el.getAttribute('data-i18n-ph-orig'));
                });
                if (document.documentElement.hasAttribute('data-i18n-title-orig')) {
                    document.title = document.documentElement.getAttribute('data-i18n-title-orig');
                }
                return;
            }

            const dict = DICTIONARY[currentLang] || {};

            // 1. Explicit data-i18n keys (page authors can opt in precisely).
            document.querySelectorAll('[data-i18n]').forEach(el => {
                const key = el.getAttribute('data-i18n');
                if (!el.hasAttribute('data-i18n-orig')) {
                    el.setAttribute('data-i18n-orig', (el.textContent || '').trim());
                }
                if (dict[key]) {
                    setTextPreservingDecor(el, dict[key]);
                }
            });

            // 2. Exact-text matching across all leaf UI elements. Because only
            //    exact dictionary keys translate, free-form body copy is never
            //    touched by accident.
            const selector = [
                'button', 'a', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
                'p', 'li', 'label', 'option', 'th', 'td', 'figcaption', 'blockquote',
                'dt', 'dd', 'strong', 'small',
                'span.stream-card-badge', '.stream-card-link', '.map-cat-chip',
                '.btn-geo-action', '.map-tool-btn', '.btn-card-booking',
                '.card-title', '.section-title', '.eyebrow', '.badge', '.btn',
                '.dob-ind-btn', '.dob-pkg-module', '.dob-pkg-users', '.dob-pkg-name',
                '.dob-pkg-price', '.dob-pkg-price span', '.dob-step-title',
                '.dob-summary-label', '.dob-summary-value'
            ].join(',');

            document.querySelectorAll(selector).forEach(el => {
                if (el.hasAttribute('data-i18n')) return;
                if (el.closest('#ethiobiz-navbar-lang-pill, #ethiobiz-welcome-lang-modal')) return;
                if (el.tagName === 'SCRIPT' || el.tagName === 'STYLE') return;

                if (el.children && el.children.length > 0) {
                    const onlyDecor = Array.prototype.every.call(el.children, isDecorativeNode);
                    if (!onlyDecor) return;
                }

                const orig = el.getAttribute('data-i18n-orig');
                const source = orig || (el.textContent || '').trim();
                const translated = lookupTranslation(source);
                if (!translated) return;
                if (!orig) el.setAttribute('data-i18n-orig', (el.textContent || '').trim());
                setTextPreservingDecor(el, translated);
            });

            // 3. Inputs / textareas placeholders
            document.querySelectorAll('input[placeholder], textarea[placeholder]').forEach(el => {
                const ph = el.getAttribute('data-i18n-ph-orig') || el.getAttribute('placeholder');
                const translated = lookupTranslation(ph);
                if (!translated) return;
                if (!el.hasAttribute('data-i18n-ph-orig')) {
                    el.setAttribute('data-i18n-ph-orig', ph);
                }
                el.setAttribute('placeholder', translated);
            });

            // 4. Document title (best effort)
            const titleTranslation = lookupTranslation(document.title);
            if (titleTranslation && !document.documentElement.hasAttribute('data-i18n-title-orig')) {
                document.documentElement.setAttribute('data-i18n-title-orig', document.title);
                document.title = titleTranslation;
            }
        } finally {
            lastApplyAt = Date.now();
            applyingTranslations = false;
        }
    }

    function observeDynamicContent() {
        if (!('MutationObserver' in window) || !document.body) return;
        const observer = new MutationObserver(function (mutations) {
            if (currentLang !== 'am') return;
            if (Date.now() - lastApplyAt < 300) return;
            let relevant = false;
            for (let i = 0; i < mutations.length; i++) {
                if (mutations[i].type === 'childList' && mutations[i].addedNodes.length) {
                    relevant = true;
                    break;
                }
            }
            if (!relevant) return;
            clearTimeout(observeDynamicContent._timer);
            observeDynamicContent._timer = setTimeout(applyTranslations, 120);
        });
        observer.observe(document.body, { childList: true, subtree: true });
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
                setLanguage(l, { userInitiated: true });
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
            const saved = localStorage.getItem('ethiobiz_lang') || getLangCookie();
            if (saved === 'am' || saved === 'en') {
                currentLang = saved;
            }
        } catch(e) {}

        injectNavbarLangToggle();
        applyLanguageState(currentLang);
        observeDynamicContent();

        // First visit: offer the bilingual welcome choice once.
        setTimeout(checkWelcomeLanguageModal, 900);
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
