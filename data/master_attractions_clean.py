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

    "Alexandria": [
        {
            "name": "Bibliotheca Alexandrina",
            "name_arabic": "مكتبة الإسكندرية",
            "category": "Cultural",
            "importance": "Must-See",
            "search_queries": ["Bibliotheca Alexandrina", "Alexandria Library"],
            "description": "Modern library commemorating ancient Library of Alexandria",
            "ticket_price": 70.0,
            "expected_rating": 4.8,
            "UNESCO_site": False
        },
        {
            "name": "Citadel of Qaitbay",
            "name_arabic": "قلعة قايتباي",
            "category": "Historical",
            "importance": "Must-See",
            "search_queries": ["Citadel of Qaitbay"],
            "description": "15th-century fortress on site of ancient Lighthouse",
            "ticket_price": 50.0,
            "expected_rating": 4.6,
            "UNESCO_site": False
        },
        {
            "name": "Catacombs of Kom el Shoqafa",
            "name_arabic": "مقابر كوم الشقافة",
            "category": "Historical",
            "importance": "Must-See",
            "search_queries": ["Catacombs of Kom el Shoqafa"],
            "description": "Ancient Roman-Egyptian necropolis",
            "ticket_price": 60.0,
            "expected_rating": 4.6,
            "UNESCO_site": False
        },
        {
            "name": "Montazah Palace Gardens",
            "name_arabic": "حدائق قصر المنتزة",
            "category": "Natural",
            "importance": "Must-See",
            "search_queries": ["Montazah Palace Alexandria"],
            "description": "Royal palace with beautiful gardens and beaches",
            "ticket_price": 20.0,
            "expected_rating": 4.7,
            "UNESCO_site": False
        },
        {
            "name": "Alexandria Corniche",
            "name_arabic": "كورنيش الإسكندرية",
            "category": "Entertainment",
            "importance": "Must-See",
            "search_queries": ["Alexandria Corniche"],
            "description": "Famous seaside promenade stretching 15km",
            "ticket_price": None,
            "expected_rating": 4.7,
            "UNESCO_site": False
        },
        {
            "name": "Alexandria National Museum",
            "name_arabic": "المتحف القومي بالإسكندرية",
            "category": "Cultural",
            "importance": "Major",
            "search_queries": ["Alexandria National Museum"],
            "description": "Museum spanning Pharaonic to modern eras",
            "ticket_price": 50.0,
            "expected_rating": 4.5,
            "UNESCO_site": False
        },
        {
            "name": "Pompey's Pillar",
            "name_arabic": "عمود Pompey",
            "category": "Historical",
            "importance": "Major",
            "search_queries": ["Pompey's Pillar Alexandria"],
            "description": "Roman triumphal column, ancient Alexandria",
            "ticket_price": 40.0,
            "expected_rating": 4.4,
            "UNESCO_site": False
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
        {
            "name": "Mount Sinai (Jabal Musa)",
            "name_arabic": "جبل موسى",
            "category": "Historical",
            "importance": "Must-See",
            "search_queries": ["Mount Sinai Egypt"],
            "description": "Biblical mountain where Moses received Ten Commandments",
            "ticket_price": 200.0,
            "expected_rating": 4.8,
            "UNESCO_site": False
        },
        {
            "name": "Saint Catherine's Monastery",
            "name_arabic": "دير سانت كاترين",
            "category": "Religious",
            "importance": "World Wonder",
            "search_queries": ["Saint Catherine Monastery Egypt"],
            "description": "Oldest continuously operating Christian monastery",
            "ticket_price": 100.0,
            "expected_rating": 4.8,
            "UNESCO_site": True
        },
        {
            "name": "Ras Mohammed National Park",
            "name_arabic": "محمية رأس محمد",
            "category": "Natural",
            "importance": "Must-See",
            "search_queries": ["Ras Mohammed Sharm El Sheikh"],
            "description": "Premier diving spot with coral reefs",
            "ticket_price": 100.0,
            "expected_rating": 4.8,
            "UNESCO_site": False
        },
        {
            "name": "Dahab",
            "name_arabic": "دهب",
            "category": "Entertainment",
            "importance": "Major",
            "search_queries": ["Dahab Egypt Sinai"],
            "description": "Laid-back beach town famous for diving",
            "ticket_price": None,
            "expected_rating": 4.6,
            "UNESCO_site": False
        },
        {
            "name": "Blue Hole (Dahab)",
            "name_arabic": "الثقب الأزرق",
            "category": "Natural",
            "importance": "Must-See",
            "search_queries": ["Blue Hole Dahab Egypt"],
            "description": "World-famous diving spot",
            "ticket_price": 50.0,
            "expected_rating": 4.7,
            "UNESCO_site": False
        }
    ]
}
