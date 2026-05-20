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
        },
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
