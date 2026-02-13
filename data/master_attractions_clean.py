"""
Master Attractions List for VoyO
Curated list of Egypt's top tourist attractions by region

Cleaned version - no malls, focus on real cultural/historical attractions
"""

MASTER_ATTRACTIONS = {
    "Cairo": [
        {
            "name": "Khan el-Khalili",
            "name_arabic": "خان الخليلي",
            "category": "Historical",
            "importance": "Must-See",
            "search_queries": ["Khan el-Khalili", "Khan el Khalili bazaar"],
            "description": "Famous historic souk (market) in the heart of Islamic Cairo",
            "ticket_price": None,
            "expected_rating": 4.5,
            "UNESCO_site": True
        },
        {
            "name": "Mosque of Sultan Hassan",
            "name_arabic": "مسجد ومدرسة السلطان حسن",
            "category": "Religious",
            "importance": "Must-See",
            "search_queries": ["Sultan Hassan Mosque", "Mosque-Madrasa of Sultan Hassan"],
            "description": "Masterpiece of Mamluk architecture, one of Cairo's largest mosques",
            "ticket_price": 40.0,
            "expected_rating": 4.8,
            "UNESCO_site": False
        },
        {
            "name": "Citadel of Cairo (Saladin Citadel)",
            "name_arabic": "قلعة صلاح الدين الأيوبي",
            "category": "Historical",
            "importance": "Must-See",
            "search_queries": ["Cairo Citadel", "Saladin Citadel", "Citadel of Muhammad Ali"],
            "description": "Medieval Islamic-era fortress with mosques and museums",
            "ticket_price": 60.0,
            "expected_rating": 4.7,
            "UNESCO_site": False
        },
        {
            "name": "The Egyptian Museum",
            "name_arabic": "المتحف المصري",
            "category": "Cultural",
            "importance": "Must-See",
            "search_queries": ["Egyptian Museum Cairo", "Egyptian Antiquities Museum"],
            "description": "World's largest collection of ancient Egyptian antiquities including Tutankhamun's treasures",
            "ticket_price": 200.0,
            "expected_rating": 4.6,
            "UNESCO_site": False
        },
        {
            "name": "Al-Azhar Mosque",
            "name_arabic": "جامع الأزهر",
            "category": "Religious",
            "importance": "Must-See",
            "search_queries": ["Al-Azhar Mosque"],
            "description": "One of Cairo's oldest mosques and home to Al-Azhar University",
            "ticket_price": None,
            "expected_rating": 4.6,
            "UNESCO_site": False
        },
        {
            "name": "Hanging Church",
            "name_arabic": "الكنيسة المعلقة",
            "category": "Religious",
            "importance": "Must-See",
            "search_queries": ["Hanging Church Cairo", "Saint Virgin Mary's Coptic Church"],
            "description": "Famous Coptic church built atop the Babylon Fortress gate",
            "ticket_price": None,
            "expected_rating": 4.7,
            "UNESCO_site": False
        },
        {
            "name": "Cairo Tower",
            "name_arabic": "برج القاهرة",
            "category": "Entertainment",
            "importance": "Major",
            "search_queries": ["Cairo Tower"],
            "description": "187-meter tower with panoramic views of Cairo and Nile",
            "ticket_price": 70.0,
            "expected_rating": 4.4,
            "UNESCO_site": False
        },
        {
            "name": "Al-Mu'izz Street",
            "name_arabic": "شارع المعز",
            "category": "Historical",
            "importance": "Must-See",
            "search_queries": ["Al-Muizz Street", "Muizz Street Cairo"],
            "description": "Open-air museum of Islamic architecture with historic mosques and mansions",
            "ticket_price": None,
            "expected_rating": 4.8,
            "UNESCO_site": True
        },
        {
            "name": "Ibn Tulun Mosque",
            "name_arabic": "مسجد أحمد بن طولون",
            "category": "Religious",
            "importance": "Major",
            "search_queries": ["Ibn Tulun Mosque"],
            "description": "One of Cairo's oldest and largest mosques, famous for its minaret",
            "ticket_price": None,
            "expected_rating": 4.5,
            "UNESCO_site": False
        },
        {
            "name": "Coptic Museum",
            "name_arabic": "المتحف القبطي",
            "category": "Cultural",
            "importance": "Major",
            "search_queries": ["Coptic Museum Cairo"],
            "description": "World's largest collection of Coptic Christian artifacts",
            "ticket_price": 40.0,
            "expected_rating": 4.5,
            "UNESCO_site": False
        }
    ],

    "Giza": [
        {
            "name": "Great Pyramid of Giza (Khufu)",
            "name_arabic": "هرم خوفو الأكبر",
            "category": "Historical",
            "importance": "World Wonder",
            "search_queries": ["Great Pyramid Giza", "Khufu Pyramid"],
            "description": "Largest of the three pyramids, oldest of the Seven Wonders",
            "ticket_price": 240.0,
            "expected_rating": 4.9,
            "UNESCO_site": True
        },
        {
            "name": "Great Sphinx of Giza",
            "name_arabic": "أبو الهول",
            "category": "Historical",
            "importance": "World Wonder",
            "search_queries": ["Great Sphinx Giza", "The Sphinx Egypt"],
            "description": "Iconic limestone statue with lion body and human head",
            "ticket_price": 240.0,
            "expected_rating": 4.8,
            "UNESCO_site": True
        },
        {
            "name": "Pyramid of Khafre",
            "name_arabic": "هرم خفرع",
            "category": "Historical",
            "importance": "World Wonder",
            "search_queries": ["Pyramid of Khafre", "Khafre Pyramid"],
            "description": "Second-largest pyramid, distinctive with its casing stones",
            "ticket_price": 240.0,
            "expected_rating": 4.8,
            "UNESCO_site": True
        },
        {
            "name": "Pyramid of Menkaure",
            "name_arabic": "هرم منكاور",
            "category": "Historical",
            "importance": "World Wonder",
            "search_queries": ["Menkaure Pyramid"],
            "description": "Smallest of the three main Giza pyramids",
            "ticket_price": 100.0,
            "expected_rating": 4.7,
            "UNESCO_site": True
        },
        {
            "name": "Giza Plateau",
            "name_arabic": "هضبة الأهرامات",
            "category": "Historical",
            "importance": "World Wonder",
            "search_queries": ["Giza Plateau"],
            "description": "Archaeological site containing the three pyramids and Sphinx",
            "ticket_price": 240.0,
            "expected_rating": 4.9,
            "UNESCO_site": True
        },
        {
            "name": "Grand Egyptian Museum (GEM)",
            "name_arabic": "المتحف المصري الكبير",
            "category": "Cultural",
            "importance": "Must-See",
            "search_queries": ["Grand Egyptian Museum", "GEM Giza"],
            "description": "State-of-the-art museum near Pyramids, housing Tutankhamun collection",
            "ticket_price": 150.0,
            "expected_rating": 4.8,
            "UNESCO_site": False
        },
        {
            "name": "Saqqara (Step Pyramid)",
            "name_arabic": "سقارة",
            "category": "Historical",
            "importance": "Must-See",
            "search_queries": ["Saqqara Pyramid", "Djoser Step Pyramid"],
            "description": "World's oldest stone pyramid, Djoser's Step Pyramid",
            "ticket_price": 120.0,
            "expected_rating": 4.7,
            "UNESCO_site": True
        },
        {
            "name": "Memphis (Mit Rahina)",
            "name_arabic": "ممفيس",
            "category": "Historical",
            "importance": "Must-See",
            "search_queries": ["Memphis Egypt", "Mit Rahina"],
            "description": "Ancient capital of Egypt, statue of Ramesses II",
            "ticket_price": 80.0,
            "expected_rating": 4.5,
            "UNESCO_site": True
        },
        {
            "name": "Dahshur Pyramids",
            "name_arabic": "أهرامات دهشور",
            "category": "Historical",
            "importance": "Must-See",
            "search_queries": ["Dahshur Pyramids", "Red Pyramid"],
            "description": "Red Pyramid and Bent Pyramid, early smooth-sided pyramids",
            "ticket_price": 80.0,
            "expected_rating": 4.6,
            "UNESCO_site": True
        }
    ],

    "Luxor": [
        {
            "name": "Karnak Temple",
            "name_arabic": "معبد الكرنك",
            "category": "Historical",
            "importance": "World Wonder",
            "search_queries": ["Karnak Temple Luxor"],
            "description": "Massive ancient Egyptian temple complex",
            "ticket_price": 200.0,
            "expected_rating": 4.9,
            "UNESCO_site": True
        },
        {
            "name": "Valley of the Kings",
            "name_arabic": "وادي الملوك",
            "category": "Historical",
            "importance": "World Wonder",
            "search_queries": ["Valley of the Kings Luxor"],
            "description": "Ancient burial ground of pharaohs including Tutankhamun",
            "ticket_price": 300.0,
            "expected_rating": 4.9,
            "UNESCO_site": True
        },
        {
            "name": "Luxor Temple",
            "name_arabic": "معبد الأقصر",
            "category": "Historical",
            "importance": "World Wonder",
            "search_queries": ["Luxor Temple Egypt"],
            "description": "Ancient Egyptian temple complex on east bank of Nile",
            "ticket_price": 140.0,
            "expected_rating": 4.8,
            "UNESCO_site": True
        },
        {
            "name": "Temple of Hatshepsut",
            "name_arabic": "دير البحري",
            "category": "Historical",
            "importance": "World Wonder",
            "search_queries": ["Hatshepsut Temple Luxor"],
            "description": "Stunning mortuary temple of female pharaoh Hatshepsut",
            "ticket_price": 100.0,
            "expected_rating": 4.8,
            "UNESCO_site": True
        },
        {
            "name": "Colossi of Memnon",
            "name_arabic": "تمثالا Memnon",
            "category": "Historical",
            "importance": "Major",
            "search_queries": ["Colossi of Memnon Luxor"],
            "description": "Two massive stone statues of Pharaoh Amenhotep III",
            "ticket_price": None,
            "expected_rating": 4.5,
            "UNESCO_site": True
        }
    ],

    "Aswan": [
        {
            "name": "Abu Simbel Temples",
            "name_arabic": "معابد أبو سمبل",
            "category": "Historical",
            "importance": "World Wonder",
            "search_queries": ["Abu Simbel Temples Egypt"],
            "description": "Massive rock-cut temples saved from Nile flooding",
            "ticket_price": 350.0,
            "expected_rating": 4.9,
            "UNESCO_site": True
        },
        {
            "name": "Philae Temple (Isis Temple)",
            "name_arabic": "معبد فيلة",
            "category": "Historical",
            "importance": "World Wonder",
            "search_queries": ["Philae Temple Aswan"],
            "description": "Beautiful island temple dedicated to goddess Isis",
            "ticket_price": 180.0,
            "expected_rating": 4.8,
            "UNESCO_site": True
        },
        {
            "name": "Aswan High Dam",
            "name_arabic": "السد العالي",
            "category": "Historical",
            "importance": "Major",
            "search_queries": ["Aswan High Dam Egypt"],
            "description": "Engineering marvel controlling Nile floods",
            "ticket_price": 50.0,
            "expected_rating": 4.5,
            "UNESCO_site": False
        },
        {
            "name": "Nubian Village",
            "name_arabic": "القرية النوبية",
            "category": "Cultural",
            "importance": "Must-See",
            "search_queries": ["Nubian Village Aswan"],
            "description": "Colorful traditional Nubian village on West Bank",
            "ticket_price": 50.0,
            "expected_rating": 4.7,
            "UNESCO_site": False
        }
    ],

    "Hurghada": [
        {
            "name": "Giftun Islands",
            "name_arabic": "جزر الجفتون",
            "category": "Natural",
            "importance": "Must-See",
            "search_queries": ["Giftun Islands Hurghada"],
            "description": "Beautiful islands for snorkeling and diving",
            "ticket_price": 300.0,
            "expected_rating": 4.7,
            "UNESCO_site": False
        },
        {
            "name": "Hurghada Marina",
            "name_arabic": "مارينا Hurghada",
            "category": "Entertainment",
            "importance": "Major",
            "search_queries": ["Hurghada Marina Egypt"],
            "description": "Upscale marina with restaurants and shops",
            "ticket_price": None,
            "expected_rating": 4.5,
            "UNESCO_site": False
        },
        {
            "name": "El Gouna",
            "name_arabic": "الجونة",
            "category": "Entertainment",
            "importance": "Major",
            "search_queries": ["El Gouna Red Sea Egypt"],
            "description": "Upscale resort town with lagoons and golf",
            "ticket_price": None,
            "expected_rating": 4.6,
            "UNESCO_site": False
        }
    ],

    "Marsa Alam": [
        {
            "name": "Wadi el Gemal National Park",
            "name_arabic": "وادي الجمال",
            "category": "Natural",
            "importance": "Must-See",
            "search_queries": ["Wadi el Gemal Marsa Alam"],
            "description": "Protected area with beaches, coral reefs, and wildlife",
            "ticket_price": 50.0,
            "expected_rating": 4.7,
            "UNESCO_site": False
        },
        {
            "name": "Sataya Reef (Dolphin House)",
            "name_arabic": "سدaya",
            "category": "Natural",
            "importance": "Must-See",
            "search_queries": ["Sataya Reef Marsa Alam"],
            "description": "Famous snorkeling spot with wild dolphins",
            "ticket_price": 350.0,
            "expected_rating": 4.8,
            "UNESCO_site": False
        }
    ],

    "Sinai": [
        # --- HISTORICAL & RELIGIOUS ---
        {"name": "Saint Catherine's Monastery", "name_arabic": "دير سانت كاترين", "category": "Religious", "importance": "Must-See", "search_queries": ["St Catherine's Monastery"], "description": "The world's oldest working Christian monastery.", "ticket_price": None, "expected_rating": 4.9, "UNESCO_site": True},
        {"name": "Mount Sinai", "name_arabic": "جبل موسى", "category": "Religious", "importance": "Must-See", "search_queries": ["Mount Sinai hike"], "description": "The peak where Moses is believed to have received the Commandments.", "ticket_price": None, "expected_rating": 4.8, "UNESCO_site": True},
        {"name": "Pharaoh's Island", "name_arabic": "جزيرة فرعون", "category": "Historical", "importance": "Major", "search_queries": ["Pharaoh's Island Citadel"], "description": "Home to a restored medieval fortress built by Saladin near Taba.", "ticket_price": 50.0, "expected_rating": 4.5, "UNESCO_site": True},
        {"name": "Serabit el-Khadim", "name_arabic": "سرابيط الخادم", "category": "Historical", "importance": "Major", "search_queries": ["Serabit el Khadim temple"], "description": "Site of ancient turquoise mines and a temple for the goddess Hathor.", "ticket_price": 40.0, "expected_rating": 4.6, "UNESCO_site": False},
        {"name": "Al-Sahaba Mosque", "name_arabic": "مسجد الصحابة", "category": "Religious", "importance": "Must-See", "search_queries": ["Sahaba Mosque Sharm"], "description": "Architectural masterpiece in Sharm El Sheikh blending Ottoman and Fatimid styles.", "ticket_price": None, "expected_rating": 4.9, "UNESCO_site": False},
        {"name": "Moses Springs", "name_arabic": "عيون موسى", "category": "Religious", "importance": "Major", "search_queries": ["Oyun Musa Sinai"], "description": "Oasis with several natural springs mentioned in biblical accounts.", "ticket_price": 20.0, "expected_rating": 4.1, "UNESCO_site": False},
        {"name": "Burning Bush", "name_arabic": "العليقة المقدسة", "category": "Religious", "importance": "Must-See", "search_queries": ["The Burning Bush Sinai"], "description": "The specific plant species mentioned in the Bible, located in the Monastery.", "ticket_price": None, "expected_rating": 4.9, "UNESCO_site": True},
        {"name": "Al-Gundi Citadel", "name_arabic": "قلعة الجندي", "category": "Historical", "importance": "Minor", "search_queries": ["Al-Gundi Citadel"], "description": "Strategic fortress built by Saladin to protect the pilgrimage route.", "ticket_price": None, "expected_rating": 4.0, "UNESCO_site": False},
        {"name": "Wadi Feiran Oasis", "name_arabic": "واحة فيران", "category": "Religious", "importance": "Major", "search_queries": ["Wadi Feiran Sinai"], "description": "The 'Pearl of Sinai,' featuring a beautiful convent and date palms.", "ticket_price": None, "expected_rating": 4.5, "UNESCO_site": False},
        {"name": "Monastery of the Seven Nuns", "name_arabic": "دير السبع بنات", "category": "Religious", "importance": "Major", "search_queries": ["Monastery of Seven Nuns"], "description": "Historic convent in the middle of the Feiran Oasis mountains.", "ticket_price": None, "expected_rating": 4.4, "UNESCO_site": False},
        {"name": "Nuweiba Fortress", "name_arabic": "قلعة نويبع", "category": "Historical", "importance": "Minor", "search_queries": ["Nuweiba Castle"], "description": "Small 19th-century fort used by the Egyptian police during the Ottoman era.", "ticket_price": None, "expected_rating": 3.7, "UNESCO_site": False},
        {"name": "Nakhl Fortress", "name_arabic": "قلعة نخل", "category": "Historical", "importance": "Minor", "search_queries": ["Nakhl Fortress Sinai"], "description": "Central Sinai fort that served as a rest stop for Hajj pilgrims.", "ticket_price": None, "expected_rating": 3.8, "UNESCO_site": False},

        # --- NATURE & WILDLIFE ---
        {"name": "Ras Mohammed", "name_arabic": "رأس محمد", "category": "Nature", "importance": "Must-See", "search_queries": ["Ras Mohammed diving"], "description": "World-famous national park with spectacular coral reefs.", "ticket_price": 150.0, "expected_rating": 4.9, "UNESCO_site": False},
        {"name": "Nabq Protectorate", "name_arabic": "محمية نبق", "category": "Nature", "importance": "Major", "search_queries": ["Nabq Protected Area"], "description": "Features mangroves, diverse birdlife, and coastal desert beauty.", "ticket_price": 80.0, "expected_rating": 4.4, "UNESCO_site": False},
        {"name": "Colored Canyon", "name_arabic": "الوادي الملون", "category": "Nature", "importance": "Must-See", "search_queries": ["Colored Canyon tour"], "description": "Vibrant rock formations created by millions of years of erosion.", "ticket_price": None, "expected_rating": 4.7, "UNESCO_site": False},
        {"name": "Blue Hole", "name_arabic": "البلو هول", "category": "Nature", "importance": "Must-See", "search_queries": ["Blue Hole Dahab"], "description": "Legendary submarine sinkhole, a top destination for divers.", "ticket_price": 100.0, "expected_rating": 4.8, "UNESCO_site": False},
        {"name": "Wadi Wishwashi", "name_arabic": "وادي الوشواشي", "category": "Nature", "importance": "Major", "search_queries": ["Wadi Wishwashi Nuweiba"], "description": "Hidden rainwater pool in a granite canyon, perfect for swimming.", "ticket_price": None, "expected_rating": 4.8, "UNESCO_site": False},
        {"name": "Ain Khudra", "name_arabic": "عين خضرة", "category": "Nature", "importance": "Major", "search_queries": ["Ain Khudra Oasis"], "description": "Lush oasis surrounded by golden desert sands.", "ticket_price": None, "expected_rating": 4.6, "UNESCO_site": False},
        {"name": "Mount Catherine", "name_arabic": "جبل كاترين", "category": "Nature", "importance": "Major", "search_queries": ["Mount Catherine hike"], "description": "Egypt's highest peak, offering unmatched views of the Sinai peninsula.", "ticket_price": None, "expected_rating": 4.9, "UNESCO_site": True},
        {"name": "White Canyon", "name_arabic": "الوايت كانيون", "category": "Nature", "importance": "Major", "search_queries": ["White Canyon Sinai"], "description": "Beautiful sandstone canyon known for its stark white walls.", "ticket_price": None, "expected_rating": 4.5, "UNESCO_site": False},
        {"name": "Blue Lagoon", "name_arabic": "البلو لاجون", "category": "Nature", "importance": "Major", "search_queries": ["Blue Lagoon Dahab"], "description": "Remote turquoise lagoon near Dahab, perfect for kitesurfing.", "ticket_price": None, "expected_rating": 4.9, "UNESCO_site": False},
        {"name": "Ras Abu Galum", "name_arabic": "رأس أبو جالوم", "category": "Nature", "importance": "Major", "search_queries": ["Abu Galum protectorate"], "description": "Pristine nature reserve accessible by camel or boat from Dahab.", "ticket_price": None, "expected_rating": 4.8, "UNESCO_site": False},
        {"name": "Tiran Island", "name_arabic": "جزيرة تيران", "category": "Nature", "importance": "Major", "search_queries": ["Tiran Island snorkeling"], "description": "Crystal-clear waters popular for boat trips and diving.", "ticket_price": None, "expected_rating": 4.6, "UNESCO_site": False},
        {"name": "Blue Desert", "name_arabic": "الصحراء الزرقاء", "category": "Nature", "importance": "Minor", "search_queries": ["Blue Desert Sinai"], "description": "Large boulders painted blue as a peace monument.", "ticket_price": None, "expected_rating": 4.2, "UNESCO_site": False},
        {"name": "Wadi Gnai", "name_arabic": "وادي جناي", "category": "Nature", "importance": "Major", "search_queries": ["Wadi Gnai climbing"], "description": "Famous spot for rock climbing and desert hiking.", "ticket_price": None, "expected_rating": 4.7, "UNESCO_site": False},

        # --- ENTERTAINMENT & MODERN ---
        {"name": "Naama Bay", "name_arabic": "خليج نعمة", "category": "Entertainment", "importance": "Must-See", "search_queries": ["Naama Bay Sharm"], "description": "The social hub of Sharm with hotels, cafes, and nightlife.", "ticket_price": None, "expected_rating": 4.3, "UNESCO_site": False},
        {"name": "SOHO Square", "name_arabic": "سوهو سكوير", "category": "Entertainment", "importance": "Must-See", "search_queries": ["SOHO Square Sharm"], "description": "Upscale entertainment area with a musical fountain and ice rink.", "ticket_price": None, "expected_rating": 4.6, "UNESCO_site": False},
        {"name": "Farsha Mountain Lounge", "name_arabic": "فرشة", "category": "Entertainment", "importance": "Major", "search_queries": ["Farsha Café Sharm"], "description": "Iconic clifftop lounge with a bohemian vibe and sea views.", "ticket_price": None, "expected_rating": 4.8, "UNESCO_site": False},
        {"name": "Old Market", "name_arabic": "السوق القديم", "category": "Cultural", "importance": "Must-See", "search_queries": ["Old Market Sharm"], "description": "Traditional bazaar perfect for souvenirs and local food.", "ticket_price": None, "expected_rating": 4.6, "UNESCO_site": False},
        {"name": "Hollywood Sharm", "name_arabic": "هوليود شرم الشيخ", "category": "Entertainment", "importance": "Major", "search_queries": ["Hollywood Sharm"], "description": "Entertainment park with dancing fountains and dinosaur statues.", "ticket_price": 50.0, "expected_rating": 4.0, "UNESCO_site": False},
        {"name": "Cleo Park", "name_arabic": "كليو بارك", "category": "Entertainment", "importance": "Major", "search_queries": ["Cleo Park Sharm"], "description": "Pharaonic-themed water park for family fun.", "ticket_price": 400.0, "expected_rating": 4.1, "UNESCO_site": False},
        {"name": "Aqua Blue Water Park", "name_arabic": "أكوا بلو", "category": "Entertainment", "importance": "Major", "search_queries": ["Aqua Blue Sharm"], "description": "One of the largest water parks in the Middle East.", "ticket_price": 500.0, "expected_rating": 4.5, "UNESCO_site": False},
        {"name": "Dahab Promenade", "name_arabic": "ممشي دهب", "category": "Entertainment", "importance": "Must-See", "search_queries": ["Dahab Promenade"], "description": "Walkway along the sea lined with diverse restaurants and shops.", "ticket_price": None, "expected_rating": 4.8, "UNESCO_site": False},
        {"name": "Genena City", "name_arabic": "جنينة سيتي", "category": "Entertainment", "importance": "Major", "search_queries": ["Genena City Mall"], "description": "A huge shopping and entertainment mall on top of a hill in Naama Bay.", "ticket_price": None, "expected_rating": 4.2, "UNESCO_site": False},
        {"name": "Shark's Bay", "name_arabic": "شاركس باي", "category": "Entertainment", "importance": "Major", "search_queries": ["Shark's Bay Sharm"], "description": "Beach area known for great shore snorkeling and dining.", "ticket_price": None, "expected_rating": 4.5, "UNESCO_site": False},
        {"name": "Al-Fanar Lighthouse", "name_arabic": "منارة الفنار", "category": "Modern", "importance": "Major", "search_queries": ["Al Fanar Sharm"], "description": "Scenic lighthouse area with a memorial and great reefs.", "ticket_price": None, "expected_rating": 4.7, "UNESCO_site": False},
        {"name": "Taba Heights", "name_arabic": "طابا هايتس", "category": "Modern", "importance": "Major", "search_queries": ["Taba Heights resort"], "description": "Luxury resort town featuring golf courses and salt caves.", "ticket_price": None, "expected_rating": 4.4, "UNESCO_site": False},
        {"name": "Lighthouse Reef", "name_arabic": "اللايت هاوس", "category": "Entertainment", "importance": "Major", "search_queries": ["Lighthouse Dahab"], "description": "The main snorkeling and diving entry point in Dahab.", "ticket_price": None, "expected_rating": 4.7, "UNESCO_site": False},

        # --- UNIQUE EXPERIENCES ---
        {"name": "Castle Zaman", "name_arabic": "كاسل زمان", "category": "Entertainment", "importance": "Major", "search_queries": ["Castle Zaman Nuweiba"], "description": "Slow-food restaurant in an eco-friendly castle overlooking the Gulf.", "ticket_price": 600.0, "expected_rating": 4.8, "UNESCO_site": False},
        {"name": "Ras El Shitan", "name_arabic": "رأس الشيطان", "category": "Nature", "importance": "Major", "search_queries": ["Ras Shetan Nuweiba"], "description": "Famous beach camps known for their 'Devil's Head' rock and relaxation.", "ticket_price": None, "expected_rating": 4.8, "UNESCO_site": False},
        {"name": "Musical Fountain", "name_arabic": "النافورة الراقصة", "category": "Entertainment", "importance": "Major", "search_queries": ["Sharm musical fountain"], "description": "Nightly light and water show in SOHO Square.", "ticket_price": None, "expected_rating": 4.5, "UNESCO_site": False},
        {"name": "Wadi El-Weshwash", "name_arabic": "وادي الوشواش", "category": "Nature", "importance": "Major", "search_queries": ["Weshwash pool"], "description": "High-altitude rainwater pool tucked in the Nuweiba mountains.", "ticket_price": None, "expected_rating": 4.7, "UNESCO_site": False},
        {"name": "Three Pools", "name_arabic": "الثلاث حمامات", "category": "Entertainment", "importance": "Major", "search_queries": ["Three Pools Dahab"], "description": "Snorkeling spot with three natural pools and beachfront cafes.", "ticket_price": None, "expected_rating": 4.4, "UNESCO_site": False},
        {"name": "Abbas Mountain", "name_arabic": "جبل عباس", "category": "Historical", "importance": "Minor", "search_queries": ["Abbas Basha Palace Sinai"], "description": "Ruins of a palace built for Abbas Pasha in the 19th century.", "ticket_price": None, "expected_rating": 4.5, "UNESCO_site": False},
        {"name": "Cave of St. John", "name_arabic": "كهف القديس يوحنا", "category": "Religious", "importance": "Minor", "search_queries": ["St John cave Sinai"], "description": "A secluded spiritual cave for hermits near St. Catherine.", "ticket_price": None, "expected_rating": 4.3, "UNESCO_site": False},
        {"name": "Bedouin Star", "name_arabic": "نجم البدو", "category": "Entertainment", "importance": "Minor", "search_queries": ["Bedouin Star camp"], "description": "Popular camp for stargazing and traditional Bedouin dinners.", "ticket_price": None, "expected_rating": 4.6, "UNESCO_site": False},
        {"name": "Straits of Tiran", "name_arabic": "مضيق تيران", "category": "Nature", "importance": "Major", "search_queries": ["Straits of Tiran diving"], "description": "Deep-water channel with world-class reefs like Jackson and Gordon.", "ticket_price": None, "expected_rating": 4.8, "UNESCO_site": False},
        {"name": "The Canyon (Dahab)", "name_arabic": "الكانون", "category": "Nature", "importance": "Major", "search_queries": ["The Canyon Dahab dive"], "description": "A deep fissure in the reef that creates a beautiful light effect for divers.", "ticket_price": None, "expected_rating": 4.7, "UNESCO_site": False},
        {"name": "Blue Desert Paintings", "name_arabic": "لوحات الصحراء الزرقاء", "category": "Cultural", "importance": "Minor", "search_queries": ["Jean Verame Blue Desert"], "description": "The specific art installation boulders painted by Jean Verame.", "ticket_price": None, "expected_rating": 4.2, "UNESCO_site": False},
        {"name": "Steps of Penitence", "name_arabic": "سلم التوبة", "category": "Religious", "importance": "Major", "search_queries": ["Steps of Penitence Mt Sinai"], "description": "The 3,750 stone steps carved by monks leading to the summit of Mt. Sinai.", "ticket_price": None, "expected_rating": 4.9, "UNESCO_site": True}
    ],

    "Alexandria": [
    # --- HISTORICAL & ARCHAEOLOGICAL ---
        {"name": "Citadel of Qaitbay", "name_arabic": "قلعة قايتباي", "category": "Historical", "importance": "Must-See", "search_queries": ["Citadel of Qaitbay"], "description": "15th-century fortress built on the ruins of the Lighthouse of Alexandria.", "ticket_price": 60.0,"expected_rating": 4.7,"UNESCO_site": False},
        {"name": "Catacombs of Kom El Shoqafa", "name_arabic": "مقابر كوم الشقافة", "category": "Historical", "importance": "Must-See", "search_queries": ["Catacombs Alexandria"], "description": "An underground wonder blending Pharaonic and Greco-Roman styles.", "ticket_price": 80.0, "expected_rating": 4.6, "UNESCO_site": False},
        {"name": "Pompey's Pillar", "name_arabic": "عمود السواري", "category": "Historical", "importance": "Must-See", "search_queries": ["Pompey's Pillar"], "description": "A massive Roman triumphal column, one of the largest of its kind.", "ticket_price": 80.0, "expected_rating": 4.3, "UNESCO_site": False},
        {"name": "Roman Amphitheatre", "name_arabic": "المسرح الروماني", "category": "Historical", "importance": "Must-See", "search_queries": ["Kom El Deka Alexandria"], "description": "Well-preserved 2nd-century theater with marble seating and mosaics.", "ticket_price": 80.0, "expected_rating": 4.5, "UNESCO_site": False},
        {"name": "Villa of the Birds", "name_arabic": "فيلا الطيور", "category": "Historical", "importance": "Major", "search_queries": ["Villa of the Birds"], "description": "Ancient Roman villa famous for its intricate floor mosaics of birds.", "ticket_price": 60.0, "expected_rating": 4.6, "UNESCO_site": False},
        {"name": "Ras El Tin Palace", "name_arabic": "قصر رأس التين", "category": "Historical", "importance": "Major", "search_queries": ["Ras El Tin Palace"], "description": "One of the oldest royal palaces in Egypt, overlooking the Mediterranean.", "ticket_price": None, "expected_rating": 4.4, "UNESCO_site": False},
        {"name": "Anfushi Tombs", "name_arabic": "مقابر الأنفوشي", "category": "Historical", "importance": "Minor", "search_queries": ["Anfushi Tombs"], "description": "Ptolemaic-era tombs featuring unique limestone decorations.", "ticket_price": 40.0, "expected_rating": 4.1, "UNESCO_site": False},
        {"name": "Serapeum of Alexandria", "name_arabic": "معبد السرابيوم", "category": "Historical", "importance": "Major", "search_queries": ["Serapeum Alexandria"], "description": "Ruins of the temple dedicated to Serapis, the protector of Alexandria.", "ticket_price": 80.0, "expected_rating": 4.2, "UNESCO_site": False},
        {"name": "Taposiris Magna", "name_arabic": "تابوزيريس ماجنا", "category": "Historical", "importance": "Major", "search_queries": ["Taposiris Magna Temple"], "description": "Ancient temple complex where archaeologists seek Cleopatra's tomb.", "ticket_price": 50.0, "expected_rating": 4.3, "UNESCO_site": False},
        {"name": "Mustafa Kamel Tombs", "name_arabic": "مقابر مصطفى كامل", "category": "Historical", "importance": "Minor", "search_queries": ["Mustafa Kamel Tombs"], "description": "Four 2nd-century BC tombs with distinctive color paintings.", "ticket_price": 40.0, "expected_rating": 4.0, "UNESCO_site": False},
        {"name": "Shatby Necropolis", "name_arabic": "جبانة الشاطبي", "category": "Historical", "importance": "Minor", "search_queries": ["Shatby Tombs"], "description": "The oldest Greco-Roman cemetery found in Alexandria.", "ticket_price": 40.0, "expected_rating": 3.8, "UNESCO_site": False},
        {"name": "El-Alamein War Cemetery", "name_arabic": "مقابر العلمين", "category": "Historical", "importance": "Major", "search_queries": ["El Alamein War Memorial"], "description": "Moving WWII memorial for the soldiers who fell in the desert battles.", "ticket_price": None, "expected_rating": 4.8, "UNESCO_site": False},
        {"name": "Sunken City (Abukir)", "name_arabic": "الآثار الغارقة", "category": "Historical", "importance": "Major", "search_queries": ["Heracleion underwater"], "description": "The lost city of Heracleion, now an underwater archaeological site.", "ticket_price": 500.0, "expected_rating": 4.9, "UNESCO_site": False},
        {"name": "Roman Baths (Kom El Deka)", "name_arabic": "الحمامات الرومانية", "category": "Historical", "importance": "Major", "search_queries": ["Roman Baths Alexandria"], "description": "A complex of brick-built thermal baths from the Roman era.", "ticket_price": 80.0, "expected_rating": 4.4, "UNESCO_site": False},
        {"name": "Nelson's Island", "name_arabic": "جزيرة نيلسون", "category": "Historical", "importance": "Minor", "search_queries": ["Nelson's Island Abukir"], "description": "Island in Abukir Bay containing archaeological finds from various eras.", "ticket_price": None, "expected_rating": 4.1, "UNESCO_site": False},

        # --- CULTURAL & MUSEUMS ---
        {"name": "Bibliotheca Alexandrina", "name_arabic": "مكتبة الإسكندرية", "category": "Cultural", "importance": "Must-See", "search_queries": ["Library of Alexandria"], "description": "A massive modern library and cultural center built to honor the ancient one.", "ticket_price": 70.0, "expected_rating": 4.8, "UNESCO_site": False},
        {"name": "Alexandria National Museum", "name_arabic": "متحف الإسكندرية القومي", "category": "Cultural", "importance": "Must-See", "search_queries": ["Alexandria National Museum"], "description": "Covers Alexandria's history from the Pharaohs to the modern day.", "ticket_price": 100.0, "expected_rating": 4.6, "UNESCO_site": False},
        {"name": "Royal Jewelry Museum", "name_arabic": "متحف المجوهرات الملكية", "category": "Cultural", "importance": "Must-See", "search_queries": ["Royal Jewelry Museum"], "description": "Houses the exquisite jewels of the Muhammad Ali dynasty.", "ticket_price": 100.0, "expected_rating": 4.9, "UNESCO_site": False},
        {"name": "Greco-Roman Museum", "name_arabic": "المتحف اليوناني الروماني", "category": "Cultural", "importance": "Must-See", "search_queries": ["Greco-Roman Museum"], "description": "Recently renovated museum with artifacts from 300 BC to 300 AD.", "ticket_price": 150.0, "expected_rating": 4.7, "UNESCO_site": False},
        {"name": "Cavafy Museum", "name_arabic": "متحف كفافيس", "category": "Cultural", "importance": "Major", "search_queries": ["Cavafy Museum"], "description": "The apartment of the famous Greek poet Constantine Cavafy.", "ticket_price": 30.0, "expected_rating": 4.5, "UNESCO_site": False},
        {"name": "Museum of Fine Arts", "name_arabic": "متحف الفنون الجميلة", "category": "Cultural", "importance": "Major", "search_queries": ["Alexandria Fine Arts Museum"], "description": "The first museum built specifically for fine arts in the Middle East.", "ticket_price": 20.0, "expected_rating": 4.4, "UNESCO_site": False},
        {"name": "Planetarium Science Center", "name_arabic": "مركز القبة السماوية", "category": "Cultural", "importance": "Major", "search_queries": ["Alexandria Planetarium"], "description": "State-of-the-art educational facility within the Bibliotheca Alexandrina.", "ticket_price": 50.0, "expected_rating": 4.6, "UNESCO_site": False},
        {"name": "Mahmoud Said Museum", "name_arabic": "متحف محمود سعيد", "category": "Cultural", "importance": "Major", "search_queries": ["Mahmoud Said Museum"], "description": "The former villa of Egypt’s most famous modern painter.", "ticket_price": 40.0, "expected_rating": 4.6, "UNESCO_site": False},
        {"name": "Alexandria Aquarium", "name_arabic": "متحف الأحياء المائية", "category": "Cultural", "importance": "Major", "search_queries": ["Alexandria Aquarium"], "description": "Small but historic aquarium showcasing Mediterranean and Red Sea fish.", "ticket_price": 20.0, "expected_rating": 3.5, "UNESCO_site": False},
        {"name": "Alexandria Opera House", "name_arabic": "دار أوبرا الإسكندرية", "category": "Cultural", "importance": "Major", "search_queries": ["Sayed Darwish Theater"], "description": "Also known as Sayed Darwish Theatre, a hub for performing arts.", "ticket_price": None, "expected_rating": 4.7, "UNESCO_site": False},
        {"name": "Manuscripts Museum", "name_arabic": "متحف المخطوطات", "category": "Cultural", "importance": "Major", "search_queries": ["Manuscripts Museum BA"], "description": "Displays rare ancient texts and maps inside the Library.", "ticket_price": 30.0, "expected_rating": 4.6, "UNESCO_site": False},
        {"name": "The Sadat Museum", "name_arabic": "متحف السادات", "category": "Cultural", "importance": "Minor", "search_queries": ["Sadat Museum Alexandria"], "description": "Dedicated to the life and belongings of President Anwar Sadat.", "ticket_price": 20.0, "expected_rating": 4.5, "UNESCO_site": False},

        # --- RELIGIOUS ---
        {"name": "Abu al-Abbas al-Mursi Mosque", "name_arabic": "جامع المرسي أبو العباس", "category": "Religious", "importance": "Must-See", "search_queries": ["Abu al-Abbas al-Mursi Mosque"], "description": "The city's largest and most iconic mosque, built in Andalusian style.", "ticket_price": None, "expected_rating": 4.8, "UNESCO_site": False},
        {"name": "Saint Mark's Coptic Cathedral", "name_arabic": "كاتدرائية القديس مرقس", "category": "Religious", "importance": "Must-See", "search_queries": ["St Mark's Cathedral Alexandria"], "description": "The historic seat of the Coptic Pope, where St. Mark was martyred.", "ticket_price": None, "expected_rating": 4.8, "UNESCO_site": False},
        {"name": "Eliahu Hanavi Synagogue", "name_arabic": "كنيس إلياهو النبي", "category": "Religious", "importance": "Major", "search_queries": ["Alexandria Synagogue"], "description": "A magnificent and recently restored synagogue on Nabi Daniel street.", "ticket_price": None, "expected_rating": 4.7, "UNESCO_site": False},
        {"name": "Saint Catherine Cathedral", "name_arabic": "كاتدرائية سانت كاترين", "category": "Religious", "importance": "Major", "search_queries": ["St Catherine Church Alexandria"], "description": "Grand Roman Catholic cathedral with an impressive Italian interior.", "ticket_price": None, "expected_rating": 4.6, "UNESCO_site": False},
        {"name": "Terbana Mosque", "name_arabic": "مسجد تربانة", "category": "Religious", "importance": "Minor", "search_queries": ["Terbana Mosque Alexandria"], "description": "The oldest mosque in Alexandria that still uses ancient columns.", "ticket_price": None, "expected_rating": 4.2, "UNESCO_site": False},
        {"name": "Attarine Mosque", "name_arabic": "جامع العطارين", "category": "Religious", "importance": "Major", "search_queries": ["Attarine Mosque"], "description": "Built on the site of a 4th-century church dedicated to St. Athanasius.", "ticket_price": None, "expected_rating": 4.5, "UNESCO_site": False},
        {"name": "Monastery of Abu Mina", "name_arabic": "دير مارمينا", "category": "Religious", "importance": "Major", "search_queries": ["Abu Mena Monastery"], "description": "UNESCO-listed pilgrimage site with ancient ruins and a modern monastery.", "ticket_price": None, "expected_rating": 4.8, "UNESCO_site": True},
        {"name": "Greek Orthodox Patriarchate", "name_arabic": "بطريركية الروم الأرثوذكس", "category": "Religious", "importance": "Major", "search_queries": ["Greek Orthodox Alexandria"], "description": "The spiritual center for the Greek community in Alexandria.", "ticket_price": None, "expected_rating": 4.7, "UNESCO_site": False},

        # --- NATURE, ENTERTAINMENT & MODERN ---
        {"name": "Montaza Palace Gardens", "name_arabic": "حدائق المنتزة", "category": "Nature", "importance": "Must-See", "search_queries": ["Montaza Gardens"], "description": "Royal gardens with diverse flora, palaces, and beach access.", "ticket_price": 25.0, "expected_rating": 4.5, "UNESCO_site": False},
        {"name": "Stanley Bridge", "name_arabic": "كوبري ستانلي", "category": "Modern", "importance": "Must-See", "search_queries": ["Stanley Bridge"], "description": "The most famous landmark for a walk and photo at sunset.", "ticket_price": None, "expected_rating": 4.7, "UNESCO_site": False},
        {"name": "Alexandria Corniche", "name_arabic": "كورنيش الإسكندرية", "category": "Nature", "importance": "Must-See", "search_queries": ["Alexandria Corniche walk"], "description": "A 10-mile long scenic waterfront promenade along the Mediterranean.", "ticket_price": None, "expected_rating": 4.5, "UNESCO_site": False},
        {"name": "Antoniadis Gardens", "name_arabic": "حدائق أنطونيادس", "category": "Nature", "importance": "Major", "search_queries": ["Antoniadis Gardens"], "description": "Vast botanical gardens containing Greco-Roman style statues.", "ticket_price": 20.0, "expected_rating": 4.2, "UNESCO_site": False},
        {"name": "Shallalat Gardens", "name_arabic": "حدائق الشلالات", "category": "Nature", "importance": "Major", "search_queries": ["Shallalat Park"], "description": "Features waterfalls and remains of the city’s Islamic walls.", "ticket_price": None, "expected_rating": 3.9, "UNESCO_site": False},
        {"name": "San Stefano Mall", "name_arabic": "سان ستيفانو", "category": "Entertainment", "importance": "Major", "search_queries": ["San Stefano Grand Plaza"], "description": "Upscale shopping and dining in the city's tallest building.", "ticket_price": None, "expected_rating": 4.5, "UNESCO_site": False},
        {"name": "Green Plaza Mall", "name_arabic": "جرين بلازا", "category": "Entertainment", "importance": "Major", "search_queries": ["Green Plaza Alexandria"], "description": "Open-air shopping mall with a cinema and international brands.", "ticket_price": None, "expected_rating": 4.3, "UNESCO_site": False},
        {"name": "Africano Park", "name_arabic": "أفريكانو بارك", "category": "Nature", "importance": "Major", "search_queries": ["Africano Safari Park"], "description": "Open-forest safari park located on the Cairo-Alex desert road.", "ticket_price": 400.0, "expected_rating": 4.6, "UNESCO_site": False},
        {"name": "Gleem Bay", "name_arabic": "جليم باي", "category": "Entertainment", "importance": "Major", "search_queries": ["Gleem Bay restaurants"], "description": "A modern hub for restaurants built directly over the sea.", "ticket_price": None, "expected_rating": 4.6, "UNESCO_site": False},
        {"name": "Maamoura Beach", "name_arabic": "شاطئ المعمورة", "category": "Nature", "importance": "Major", "search_queries": ["Maamoura Beach"], "description": "A high-end private residential and beach area.", "ticket_price": 50.0, "expected_rating": 4.2, "UNESCO_site": False},
        {"name": "Greek Club", "name_arabic": "النادي اليوناني", "category": "Entertainment", "importance": "Major", "search_queries": ["Greek Club Alexandria"], "description": "Famous for its balcony with the best view of the Eastern Harbor.", "ticket_price": None, "expected_rating": 4.6, "UNESCO_site": False},
        {"name": "Oryx Shark", "name_arabic": "أوريكس شارك", "category": "Entertainment", "importance": "Minor", "search_queries": ["Oryx Shark Alexandria"], "description": "Popular waterfront lounge and restaurant for local youth.", "ticket_price": None, "expected_rating": 4.3, "UNESCO_site": False},
        {"name": "Smouha Club", "name_arabic": "نادي سموحة", "category": "Entertainment", "importance": "Major", "search_queries": ["Smouha Sporting Club"], "description": "Massive social and sporting club in the heart of the city.", "ticket_price": None, "expected_rating": 4.7, "UNESCO_site": False},
        {"name": "Alexandria Zoo", "name_arabic": "حديقة حيوان الإسكندرية", "category": "Nature", "importance": "Minor", "search_queries": ["Alexandria Zoo"], "description": "The city's traditional zoo, located near the Antoniadis gardens.", "ticket_price": 5.0, "expected_rating": 3.2, "UNESCO_site": False},
        {"name": "International Park", "name_arabic": "الحديقة الدولية", "category": "Nature", "importance": "Minor", "search_queries": ["International Park Alexandria"], "description": "Large park used for exhibitions and leisure activities.", "ticket_price": 10.0, "expected_rating": 3.5, "UNESCO_site": False}
],


}
