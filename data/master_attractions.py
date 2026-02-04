"""
Master Attractions List for VoyO
Curated list of Egypt's top tourist attractions by region
"""

MASTER_ATTRACTIONS = {
    "Cairo": [
        {
            "name": "Khan el-Khalili",
            "name_arabic": "خان الخليلي",
            "category": "Historical",
            "importance": "Must-See",
            "search_queries": ["Khan el-Khalili", "Khan el Khalili bazaar", "خان الخليلي"],
            "description": "Famous historic souk (market) in the heart of Islamic Cairo",
            "ticket_price": None,  # Free entry, pay for purchases
            "expected_rating": 4.5,
            " UNESCO_site": False
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
            "name": "Mosque of Muhammad Ali",
            "name_arabic": "مسجد محمد علي",
            "category": "Religious",
            "importance": "Must-See",
            "search_queries": ["Muhammad Ali Mosque", "Alabaster Mosque Cairo"],
            "description": "Ottoman-style mosque within Cairo Citadel, iconic with its alabaster walls",
            "ticket_price": 60.0,  # Included in Citadel ticket
            "expected_rating": 4.7,
            "UNESCO_site": False
        },
        {
            "name": "The Egyptian Museum",
            "name_arabic": "المتحف المصري",
            "category": "Cultural",
            "importance": "Must-See",
            "search_queries": ["Egyptian Museum Cairo", "Egyptian Antiquities Museum", "متحف الآثار المصرية"],
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
            "search_queries": ["Al-Azhar Mosque", "Al Azhar Mosque Cairo"],
            "description": "One of Cairo's oldest mosques and home to Al-Azhar University",
            "ticket_price": None,  # Free
            "expected_rating": 4.6,
            "UNESCO_site": False
        },
        {
            "name": "Hanging Church (Saint Virgin Mary's Coptic Orthodox Church)",
            "name_arabic": "الكنيسة المعلقة",
            "category": "Religious",
            "importance": "Must-See",
            "search_queries": ["Hanging Church Cairo", "Saint Virgin Mary's Coptic Church", "الكنيسة المعلقة"],
            "description": "Famous Coptic church built atop the Babylon Fortress gate",
            "ticket_price": None,  # Free
            "expected_rating": 4.7,
            "UNESCO_site": False
        },
        {
            "name": "Cairo Tower",
            "name_arabic": "برج القاهرة",
            "category": "Entertainment",
            "importance": "Major",
            "search_queries": ["Cairo Tower", "Cairo Tower observation deck"],
            "description": "187-meter tower with panoramic views of Cairo and Nile",
            "ticket_price": 70.0,
            "expected_rating": 4.4,
            "UNESCO_site": False
        },
        {
            "name": "Ibn Tulun Mosque",
            "name_arabic": "مسجد أحمد بن طولون",
            "category": "Religious",
            "importance": "Major",
            "search_queries": ["Ibn Tulun Mosque", "Mosque of Ibn Tulun"],
            "description": "One of Cairo's oldest and largest mosques, famous for its minaret",
            "ticket_price": None,  # Free
            "expected_rating": 4.5,
            "UNESCO_site": False
        },
        {
            "name": "Mosque of Al-Rifa'i",
            "name_arabic": "مسجد الرفاعي",
            "category": "Religious",
            "importance": "Major",
            "search_queries": ["Al-Rifai Mosque", "Mosque of Al-Rifai Cairo"],
            "description": "Grand mosque opposite Sultan Hassan, royal burial site",
            "ticket_price": None,  # Free
            "expected_rating": 4.5,
            "UNESCO_site": False
        },
        {
            "name": "Coptic Museum",
            "name_arabic": "المتحف القبطي",
            "category": "Cultural",
            "importance": "Major",
            "search_queries": ["Coptic Museum Cairo", "Coptic Christian Museum"],
            "description": "World's largest collection of Coptic Christian artifacts",
            "ticket_price": 40.0,
            "expected_rating": 4.5,
            "UNESCO_site": False
        },
        {
            "name": "Ben Ezra Synagogue",
            "name_arabic": "معرض بن عزرا",
            "category": "Religious",
            "importance": "Major",
            "search_queries": ["Ben Ezra Synagogue Cairo", "Ben Ezra Synagogue Egypt"],
            "description": "Oldest synagogue in Egypt, famous for its Geniza documents",
            "ticket_price": 20.0,
            "expected_rating": 4.4,
            "UNESCO_site": False
        },
        {
            "name": "Al-Mu'izz Street",
            "name_arabic": "شارع المعز",
            "category": "Historical",
            "importance": "Must-See",
            "search_queries": ["Al-Muizz Street", "Al Muizz li-Din Allah", "Muizz Street Cairo"],
            "description": "Open-air museum of Islamic architecture with historic mosques and mansions",
            "ticket_price": None,  # Free
            "expected_rating": 4.8,
            "UNESCO_site": True
        },
        {
            "name": "Bab Zuweila",
            "name_arabic": "باب زويلة",
            "category": "Historical",
            "importance": "Major",
            "search_queries": ["Bab Zuweila", "Bab Zuwayla Cairo", "Gate of Zuweila"],
            "description": "Medieval gate and minaret offering city views",
            "ticket_price": 30.0,
            "expected_rating": 4.4,
            "UNESCO_site": True
        },
        {
            "name": "Bab Al-Futuh",
            "name_arabic": "باب الفتح",
            "category": "Historical",
            "importance": "Major",
            "search_queries": ["Bab Al-Futuh", "Bab el-Futuh Cairo"],
            "description": "One of the remaining gates of Old Cairo's fortifications",
            "ticket_price": None,  # Free
            "expected_rating": 4.3,
            "UNESCO_site": True
        },
        {
            "name": "Bayt Al-Suhaymi",
            "name_arabic": "بيت السحيمي",
            "category": "Historical",
            "importance": "Major",
            "search_queries": ["Bayt Al-Suhaymi", "Suhaymi House Cairo"],
            "description": "Well-preserved Ottoman-era mansion showing traditional Cairo architecture",
            "ticket_price": 30.0,
            "expected_rating": 4.5,
            "UNESCO_site": True
        },
        {
            "name": "Gayer-Anderson Museum",
            "name_arabic": "متحف جاير أندرسون",
            "category": "Cultural",
            "importance": "Major",
            "search_queries": ["Gayer-Anderson Museum", "Bayt al-Kritliyya Cairo"],
            "description": "Historic house museum with collection of Islamic art",
            "ticket_price": 35.0,
            "expected_rating": 4.5,
            "UNESCO_site": False
        },
        {
            "name": "Manial Palace and Museum",
            "name_arabic": "قصر النيل",
            "category": "Historical",
            "importance": "Major",
            "search_queries": ["Manial Palace Cairo", "Prince Mohamed Ali Palace"],
            "description": "Early 20th-century palace with unique architecture and gardens",
            "ticket_price": 50.0,
            "expected_rating": 4.4,
            "UNESCO_site": False
        },
        {
            "name": "Nilometer (Rodah Island)",
            "name_arabic": "المقياس النيلي",
            "category": "Historical",
            "importance": "Minor",
            "search_queries": ["Nilometer Cairo", "Nilometer Rodah Island"],
            "description": "Ancient structure used to measure Nile flood levels",
            "ticket_price": 25.0,
            "expected_rating": 4.2,
            "UNESCO_site": False
        },
        {
            "name": "Saint George's Church (Mari Girgis)",
            "name_arabic": "كنيسة مار جرجس",
            "category": "Religious",
            "importance": "Major",
            "search_queries": ["Saint George Church Cairo", "Church of St George Cairo"],
            "description": "Greek Orthodox church with round tower and holy site",
            "ticket_price": None,  # Free
            "expected_rating": 4.3,
            "UNESCO_site": False
        },
        {
            "name": "Convent of Saint George",
            "name_arabic": "دير مار جرجس",
            "category": "Religious",
            "importance": "Minor",
            "search_queries": ["Convent of Saint George Cairo", "Saint George Monastery"],
            "description": "Coptic convent with chapel and monastery",
            "ticket_price": 15.0,
            "expected_rating": 4.1,
            "UNESCO_site": False
        },
        {
            "name": "Church of St. Sergius and Bacchus (Abu Serga)",
            "name_arabic": "كنيسة أبو سرجة",
            "category": "Religious",
            "importance": "Major",
            "search_queries": ["Abu Serga Church", "Church of Saints Sergius and Bacchus"],
            "description": "Oldest Coptic church in Cairo, traditional Holy Family resting site",
            "ticket_price": None,  # Free
            "expected_rating": 4.4,
            "UNESCO_site": False
        },
        {
            "name": "Zamalek District (Gezira Island)",
            "name_arabic": "حي الزمالك",
            "category": "Entertainment",
            "importance": "Major",
            "search_queries": ["Zamalek Cairo", "Zamalek Island", "Gezira Island Cairo"],
            "description": "Upscale residential island with cafes, embassies, and Nile views",
            "ticket_price": None,  # Free area
            "expected_rating": 4.5,
            "UNESCO_site": False
        },
        {
            "name": "Cairo Opera House",
            "name_arabic": "دار الأوبرا المصرية",
            "category": "Cultural",
            "importance": "Major",
            "search_queries": ["Cairo Opera House", "Egyptian Opera House"],
            "description": "Main performing arts venue in Zamalek",
            "ticket_price": None,  # Varies by show
            "expected_rating": 4.5,
            "UNESCO_site": False
        },
        {
            "name": "Museum of Islamic Art",
            "name_arabic": "متحف الفن الإسلامي",
            "category": "Cultural",
            "importance": "Must-See",
            "search_queries": ["Museum of Islamic Art Cairo", "Islamic Art Museum Egypt"],
            "description": "World's largest collection of Islamic artifacts",
            "ticket_price": 50.0,
            "expected_rating": 4.6,
            "UNESCO_site": False
        },
        {
            "name": "Tahrir Square (Midan Tahrir)",
            "name_arabic": "ميدان التحرير",
            "category": "Historical",
            "importance": "Major",
            "search_queries": ["Tahrir Square Cairo", "Midan Tahrir Egypt"],
            "description": "Central square and site of 2011 Egyptian Revolution",
            "ticket_price": None,  # Free
            "expected_rating": 4.3,
            "UNESCO_site": False
        },
        {
            "name": "Abdin Palace",
            "name_arabic": "قصر عابدين",
            "category": "Historical",
            "importance": "Major",
            "search_queries": ["Abdin Palace Cairo", "Abdeen Palace Egypt"],
            "description": "Former royal palace and current presidential headquarters",
            "ticket_price": 40.0,
            "expected_rating": 4.3,
            "UNESCO_site": False
        },
        {
            "name": "Cairo International Stadium",
            "name_arabic": "استاد القاهرة الدولي",
            "category": "Entertainment",
            "importance": "Minor",
            "search_queries": ["Cairo International Stadium", "Cairo Stadium"],
            "description": "Largest stadium in Egypt and home of national football team",
            "ticket_price": None,  # Varies by event
            "expected_rating": 4.0,
            "UNESCO_site": False
        },
        {
            "name": "Al-Aqmar Mosque",
            "name_arabic": "جامع الأقمر",
            "category": "Religious",
            "importance": "Minor",
            "search_queries": ["Al-Aqmar Mosque Cairo", "Aqmar Mosque"],
            "description": "12th-century mosque with unique decorated facade",
            "ticket_price": None,  # Free
            "expected_rating": 4.2,
            "UNESCO_site": True
        },
        {
            "name": "Mosque-Madrasa of Sultan Barquq",
            "name_arabic": "مدرسة السلطان برقوق",
            "category": "Religious",
            "importance": "Minor",
            "search_queries": ["Mosque-Madrasa of Sultan Barquq", "Barquq Mosque Cairo"],
            "description": "Mamluk-era mosque and madrasa complex",
            "ticket_price": 20.0,
            "expected_rating": 4.3,
            "UNESCO_site": True
        },
        {
            "name": "Mosque of Al-Salih Tala'i",
            "name_arabic": "مسجد الصالح طلائع",
            "category": "Religious",
            "importance": "Minor",
            "search_queries": ["Mosque of Al-Salih Tala'i", "Salih Tala'i Mosque"],
            "description": "One of the few Fatimid-era mosques remaining",
            "ticket_price": None,  # Free
            "expected_rating": 4.1,
            "UNESCO_site": True
        },
        {
            "name": "Wekalat Al-Ghouri (Ghouriya Complex)",
            "name_arabic": "وكالة الغوري",
            "category": "Cultural",
            "importance": "Major",
            "search_queries": ["Wekalat Al-Ghouri", "Ghouriya Complex Cairo"],
            "description": "Historic merchant complex with cultural performances",
            "ticket_price": None,  # Free
            "expected_rating": 4.4,
            "UNESCO_site": True
        },
        {
            "name": "Mosque of Qani-Bay",
            "name_arabic": "مسجد قايتباي",
            "category": "Religious",
            "importance": "Minor",
            "search_queries": ["Mosque of Qani-Bay Cairo", "Qani-Bay Mosque"],
            "description": "Mamluk mosque with distinctive minaret",
            "ticket_price": None,  # Free
            "expected_rating": 4.1,
            "UNESCO_site": True
        },
        {
            "name": "Al-Hakim Mosque",
            "name_arabic": "جامع الحاكم",
            "category": "Religious",
            "importance": "Major",
            "search_queries": ["Al-Hakim Mosque Cairo", "Mosque of Al-Hakim"],
            "description": "Major Fatimid-era mosque, one of Cairo's largest",
            "ticket_price": None,  # Free
            "expected_rating": 4.4,
            "UNESCO_site": True
        },
        {
            "name": "Cairo Geniza",
            "name_arabic": "الجنيزة القاهرية",
            "category": "Historical",
            "importance": "Minor",
            "search_queries": ["Cairo Geniza", "Ben Ezra Geniza Cairo"],
            "description": "Historical collection of Jewish manuscripts",
            "ticket_price": None,  # Part of Ben Ezra Synagogue
            "expected_rating": 4.2,
            "UNESCO_site": False
        },
        {
            "name": "Mosque of Aqsunqur (Blue Mosque)",
            "name_arabic": "جامع أكسونقور",
            "category": "Religious",
            "importance": "Minor",
            "search_queries": ["Blue Mosque Cairo", "Mosque of Aqsunqur"],
            "description": "Mamluk mosque famous for blue tile decorations",
            "ticket_price": 20.0,
            "expected_rating": 4.3,
            "UNESCO_site": False
        },
        {
            "name": "Sinai Mosque at Mosque of Ibn Tulun",
            "name_arabic": "جامع صهينة",
            "category": "Religious",
            "importance": "Minor",
            "search_queries": ["Sinai Mosque Cairo", "Gama'et Sinai"],
            "description": "Small historic mosque adjacent to Ibn Tulun",
            "ticket_price": None,  # Free
            "expected_rating": 4.0,
            "UNESCO_site": False
        },
        {
            "name": "Amr Ibn Al-Aas Mosque",
            "name_arabic": "مسجد عمرو بن العاص",
            "category": "Religious",
            "importance": "Must-See",
            "search_queries": ["Amr Ibn Al-Aas Mosque", "Mosque of Amr ibn al-As"],
            "description": "First mosque built in Egypt and Africa",
            "ticket_price": None,  # Free
            "expected_rating": 4.6,
            "UNESCO_site": False
        },
        {
            "name": "Harem Palace (Manial Palace Museum)",
            "name_arabic": "قصر الحرملك",
            "category": "Historical",
            "importance": "Major",
            "search_queries": ["Harem Palace Manial", "Manial Palace Harem"],
            "description": "Private wing of Manial Palace museum",
            "ticket_price": 50.0,
            "expected_rating": 4.3,
            "UNESCO_site": False
        },
        {
            "name": "Mosque of Al-Ashraf Barsbey",
            "name_arabic": "جامع الأشرف برسباي",
            "category": "Religious",
            "importance": "Minor",
            "search_queries": ["Mosque of Al-Ashraf Barsbey", "Barsbey Mosque Cairo"],
            "description": "Mamluk mosque and mausoleum complex",
            "ticket_price": 15.0,
            "expected_rating": 4.1,
            "UNESCO_site": True
        },
        {
            "name": "Mosque of Sultan Al-Mu'ayyad",
            "name_arabic": "جامع السلطان المؤيد",
            "category": "Religious",
            "importance": "Minor",
            "search_queries": ["Mosque of Sultan Al-Mu'ayyad", "Mu'ayyad Mosque Cairo"],
            "description": "Historic mosque with twin minarets overlooking Bab Zuweila",
            "ticket_price": 20.0,
            "expected_rating": 4.2,
            "UNESCO_site": True
        },
        {
            "name": "Mosque of Al-Maridani",
            "name_arabic": "جامع المراداني",
            "category": "Religious",
            "importance": "Minor",
            "search_queries": ["Mosque of Al-Maridani Cairo", "Maridani Mosque"],
            "description": "14th-century Mamluk mosque",
            "ticket_price": None,  # Free
            "expected_rating": 4.0,
            "UNESCO_site": False
        },
        {
            "name": "El Sawy Culturewheel",
            "name_arabic": "ساقية عبد المنعم الصاوي",
            "category": "Cultural",
            "importance": "Major",
            "search_queries": ["El Sawy Culturewheel", "Sakia Culturewheel Cairo"],
            "description": "Contemporary cultural center with art exhibitions and performances",
            "ticket_price": None,  # Varies by event
            "expected_rating": 4.3,
            "UNESCO_site": False
        },
        {
            "name": "Cairo Festival City Mall",
            "name_arabic": "مول القاهرة فيستيفال",
            "category": "Shopping",
            "importance": "Minor",
            "search_queries": ["Cairo Festival City Mall", "CFC Mall Cairo"],
            "description": "Modern shopping and entertainment complex",
            "ticket_price": None,  # Free entry
            "expected_rating": 4.4,
            "UNESCO_site": False
        },
        {
            "name": "City Stars Mall",
            "name_arabic": "سيتي ستارز",
            "category": "Shopping",
            "importance": "Minor",
            "search_queries": ["City Stars Mall Cairo", "Citystars Heliopolis"],
            "description": "One of Cairo's largest shopping malls",
            "ticket_price": None,  # Free entry
            "expected_rating": 4.3,
            "UNESCO_site": False
        },
        {
            "name": "Nile Pharaoh (Nile Cruise)",
            "name_arabic": "رحلة نيلية",
            "category": "Entertainment",
            "importance": "Major",
            "search_queries": ["Nile cruise Cairo", "Nile dinner cruise Egypt"],
            "description": "Dinner cruise on the Nile with entertainment",
            "ticket_price": 300.0,
            "expected_rating": 4.5,
            "UNESCO_site": False
        },
        {
            "name": "Al-Fustat (Old Cairo)",
            "name_arabic": "الفسطاط",
            "category": "Historical",
            "importance": "Major",
            "search_queries": ["Al-Fustat Cairo", "Fustat Old Cairo"],
            "description": "First capital of Egypt, historic district with Coptic monuments",
            "ticket_price": None,  # Free area
            "expected_rating": 4.5,
            "UNESCO_site": False
        },
        {
            "name": "Mosque of Abu Bakr (Shafe'i Mosque)",
            "name_arabic": "جامع أبو بكر",
            "category": "Religious",
            "importance": "Minor",
            "search_queries": ["Imam Shafi'i Mosque Cairo", "Mosque of Imam Shafi'i"],
            "description": "Historic mosque and mausoleum of Imam Shafi'i",
            "ticket_price": None,  # Free
            "expected_rating": 4.2,
            "UNESCO_site": False
        },
        {
            "name": "Mosque of Sayyida Nafisa",
            "name_arabic": "جامع السيدة نفيسة",
            "category": "Religious",
            "importance": "Minor",
            "search_queries": ["Mosque of Sayyida Nafisa Cairo", "Sayyida Nafisa Mosque"],
            "description": "Mosque and mausoleum of Prophet Muhammad's descendant",
            "ticket_price": None,  # Free
            "expected_rating": 4.1,
            "UNESCO_site": False
        },
        {
            "name": "Mosque of Sayyida Aisha",
            "name_arabic": "جامع السيدة عائشة",
            "category": "Religious",
            "importance": "Minor",
            "search_queries": ["Mosque of Sayyida Aisha Cairo", "Sayyida Aisha Mosque"],
            "description": "Historic mosque and tomb",
            "ticket_price": None,  # Free
            "expected_rating": 4.0,
            "UNESCO_site": False
        },
        {
            "name": "Al-Hussein Mosque",
            "name_arabic": "جامع الحسين",
            "category": "Religious",
            "importance": "Must-See",
            "search_queries": ["Al-Hussein Mosque Cairo", "Al-Hussein Mosque Khan el-Khalili"],
            "description": "Sacred mosque believed to contain Prophet's grandson's head",
            "ticket_price": None,  # Free
            "expected_rating": 4.7,
            "UNESCO_site": False
        },
        {
            "name": "Mosque of Sayyida Zeinab",
            "name_arabic": "جامع السيدة زينب",
            "category": "Religious",
            "importance": "Major",
            "search_queries": ["Mosque of Sayyida Zeinab Cairo", "Sayyida Zeinab Mosque"],
            "description": "Mosque and mausoleum of Prophet Muhammad's granddaughter",
            "ticket_price": None,  # Free
            "expected_rating": 4.3,
            "UNESCO_site": False
        },
        {
            "name": "Cairo Wax Museum",
            "name_arabic": "متحف الشمع",
            "category": "Cultural",
            "importance": "Minor",
            "search_queries": ["Cairo Wax Museum", "Wax Museum Egypt"],
            "description": "Wax figures depicting Egyptian history and personalities",
            "ticket_price": 30.0,
            "expected_rating": 3.8,
            "UNESCO_site": False
        },
        {
            "name": "Agricultural Museum",
            "name_arabic": "المتحف الزراعي",
            "category": "Cultural",
            "importance": "Minor",
            "search_queries": ["Agricultural Museum Cairo", "Agricultural Museum Egypt"],
            "description": "Museum showcasing Egypt's agricultural history",
            "ticket_price": 20.0,
            "expected_rating": 4.0,
            "UNESCO_site": False
        },
        {
            "name": "Postal Museum",
            "name_arabic": "متحف البريد",
            "category": "Cultural",
            "importance": "Minor",
            "search_queries": ["Postal Museum Cairo", "Egyptian Postal Museum"],
            "description": "History of Egyptian postal service",
            "ticket_price": 15.0,
            "expected_rating": 3.9,
            "UNESCO_site": False
        },
        {
            "name": "Geology Museum",
            "name_arabic": "المتحف الجيولوجي",
            "category": "Cultural",
            "importance": "Minor",
            "search_queries": ["Geology Museum Cairo", "Egyptian Geological Museum"],
            "description": "Collection of Egyptian geological specimens",
            "ticket_price": 15.0,
            "expected_rating": 3.8,
            "UNESCO_site": False
        },
        {
            "name": "Mahmoud Mokhtar Museum",
            "name_arabic": "متحف محمود مختار",
            "category": "Cultural",
            "importance": "Minor",
            "search_queries": ["Mahmoud Mokhtar Museum Cairo", "Mukhtar Museum"],
            "description": "Museum dedicated to Egyptian sculptor Mahmoud Mokhtar",
            "ticket_price": 20.0,
            "expected_rating": 4.2,
            "UNESCO_site": False
        },
        {
            "name": "Umm Kolthum Museum",
            "name_arabic": "متحف أم كلثوم",
            "category": "Cultural",
            "importance": "Minor",
            "search_queries": ["Umm Kolthum Museum Cairo", "Oum Koulthoum Museum"],
            "description": "Museum dedicated to legendary Egyptian singer",
            "ticket_price": 20.0,
            "expected_rating": 4.3,
            "UNESCO_site": False
        },
        {
            "name": "Cairo Military Museum",
            "name_arabic": "المتحف الحربي",
            "category": "Cultural",
            "importance": "Minor",
            "search_queries": ["Military Museum Cairo", "Egyptian Military Museum"],
            "description": "Egypt's military history from ancient to modern times",
            "ticket_price": 30.0,
            "expected_rating": 4.1,
            "UNESCO_site": False
        },
        {
            "name": "Police Museum",
            "name_arabic": "متحف الشرطة",
            "category": "Cultural",
            "importance": "Minor",
            "search_queries": ["Police Museum Cairo", "Egyptian Police Museum"],
            "description": "History of Egyptian police force",
            "ticket_price": 20.0,
            "expected_rating": 3.7,
            "UNESCO_site": False
        },
        {
            "name": "Railway Museum",
            "name_arabic": "متحف السكك الحديدية",
            "category": "Cultural",
            "importance": "Minor",
            "search_queries": ["Railway Museum Cairo", "Egyptian Railway Museum"],
            "description": "History of Egypt's railway system",
            "ticket_price": 15.0,
            "expected_rating": 3.8,
            "UNESCO_site": False
        },
        {
            "name": "National Museum of Egyptian Civilization",
            "name_arabic": "المتحف القومي للحضارة المصرية",
            "category": "Cultural",
            "importance": "Must-See",
            "search_queries": ["National Museum of Egyptian Civilization", "NMEC Cairo"],
            "description": "New museum showcasing Egyptian civilization, houses royal mummies",
            "ticket_price": 200.0,
            "expected_rating": 4.7,
            "UNESCO_site": False
        },
        {
            "name": " Aquarium Ghamra",
            "name_arabic": "أسماك الغمرية",
            "category": "Entertainment",
            "importance": "Minor",
            "search_queries": ["Ghamra Aquarium Cairo", "Aquarium Ghamra"],
            "description": "Small aquarium in downtown Cairo",
            "ticket_price": 25.0,
            "expected_rating": 3.6,
            "UNESCO_site": False
        },
        {
            "name": "Al-Azhar Park",
            "name_arabic": "الأزهر بارك",
            "category": "Natural",
            "importance": "Major",
            "search_queries": ["Al-Azhar Park Cairo", "Al Azhar Park Egypt"],
            "description": "Large urban park with city views and historic area",
            "ticket_price": 15.0,
            "expected_rating": 4.6,
            "UNESCO_site": False
        },
        {
            "name": "Family Park (Hadayek Al-Ahram)",
            "name_arabic": "فاميلي بارك",
            "category": "Entertainment",
            "importance": "Minor",
            "search_queries": ["Family Park Cairo", "Hadayek Al-Ahram Park"],
            "description": "Family entertainment park",
            "ticket_price": 50.0,
            "expected_rating": 4.0,
            "UNESCO_site": False
        },
        {
            "name": "Dream Park",
            "name_arabic": "دريم بارك",
            "category": "Entertainment",
            "importance": "Major",
            "search_queries": ["Dream Park Cairo", "Dream Park Egypt"],
            "description": "Amusement park with rides and games",
            "ticket_price": 150.0,
            "expected_rating": 4.1,
            "UNESCO_site": False
        },
        {
            "name": "Al-Ghoria Palace",
            "name_arabic": "قصر الغوري",
            "category": "Historical",
            "importance": "Minor",
            "search_queries": ["Al-Ghoria Palace Cairo", "Ghuriya Palace"],
            "description": "Historic Mamluk-era palace and cultural venue",
            "ticket_price": 25.0,
            "expected_rating": 4.2,
            "UNESCO_site": True
        },
        {
            "name": "Sabil-Kuttab of Abdel Katib Khdhra",
            "name_arabic": "سبيل وكتاب عبد الكاتب خضرة",
            "category": "Historical",
            "importance": "Minor",
            "search_queries": ["Sabil-Kuttab Abdel Katib Cairo", "Sabil Cairo"],
            "description": "Historic fountain and Quranic school",
            "ticket_price": 10.0,
            "expected_rating": 3.9,
            "UNESCO_site": True
        },
        {
            "name": "Mosque of Qaitbay",
            "name_arabic": "جامع قايتباي",
            "category": "Religious",
            "importance": "Minor",
            "search_queries": ["Mosque of Qaitbay Cairo", "Qaitbay Mosque Northern Cemetery"],
            "description": "Mamluk mosque in City of the Dead",
            "ticket_price": 15.0,
            "expected_rating": 4.1,
            "UNESCO_site": False
        },
        {
            "name": "Cairo Dynasty Tombs",
            "name_arabic": "مقابر سلاطين المماليك",
            "category": "Historical",
            "importance": "Minor",
            "search_queries": ["Mamluk Tombs Cairo", "Northern Cemetery Cairo"],
            "description": "Historic Mamluk-era tombs",
            "ticket_price": 30.0,
            "expected_rating": 4.0,
            "UNESCO_site": False
        },
        {
            "name": "Al-Imam Al-Shafi'i Mosque",
            "name_arabic": "جامع الإمام الشافعي",
            "category": "Religious",
            "importance": "Major",
            "search_queries": ["Imam Al-Shafi'i Mosque Cairo", "Shafi'i Mosque"],
            "description": "Large mosque and mausoleum complex",
            "ticket_price": None,  # Free
            "expected_rating": 4.3,
            "UNESCO_site": False
        },
        {
            "name": "Mosque of Sultan Al-Mansur Qalawun",
            "name_arabic": "جامع السلطان قلاوون",
            "category": "Religious",
            "importance": "Minor",
            "search_queries": ["Mosque of Qalawun Cairo", "Qalawun Complex"],
            "description": "Mamluk-era complex with mosque, madrasa, and mausoleum",
            "ticket_price": 20.0,
            "expected_rating": 4.2,
            "UNESCO_site": True
        },
        {
            "name": "Mosque of Al-Nasir Muhammad",
            "name_arabic": "جامع الناصر محمد",
            "category": "Religious",
            "importance": "Minor",
            "search_queries": ["Mosque of Al-Nasir Muhammad Cairo", "Nasir Muhammad Mosque Citadel"],
            "description": "Mamluk mosque within Cairo Citadel",
            "ticket_price": 30.0,
            "expected_rating": 4.1,
            "UNESCO_site": False
        },
        {
            "name": "Mosque of Lajin (Sultan Lajin)",
            "name_arabic": "جامع لا جين",
            "category": "Religious",
            "importance": "Minor",
            "search_queries": ["Mosque of Sultan Lajin Cairo", "Lajin Mosque"],
            "description": "Historic mosque adjacent to Mosque of Sultan Hasan",
            "ticket_price": None,  # Free
            "expected_rating": 3.9,
            "UNESCO_site": False
        },
        {
            "name": "Mosque of Al-Saleh Nagm Al-Din",
            "name_arabic": "جامع الصالح نجم الدين",
            "category": "Religious",
            "importance": "Minor",
            "search_queries": ["Mosque of Al-Saleh Nagm Al-Din Cairo"],
            "description": "Historic mosque in Islamic Cairo",
            "ticket_price": None,  # Free
            "expected_rating": 3.8,
            "UNESCO_site": False
        },
        {
            "name": "Mosque of Tughay (Mother of Sultan Hasan)",
            "name_arabic": "جامع طغاي",
            "category": "Religious",
            "importance": "Minor",
            "search_queries": ["Mosque of Tughay Cairo", "Tughay Mosque"],
            "description": "Mosque and mausoleum of Sultan Hasan's mother",
            "ticket_price": None,  # Free
            "expected_rating": 3.7,
            "UNESCO_site": False
        },
        {
            "name": "Cairo's City of the Dead (Al-Qarafa)",
            "name_arabic": "القرافة (مدينة الأموات)",
            "category": "Historical",
            "importance": "Major",
            "search_queries": ["City of the Dead Cairo", "Al-Qarafa Cairo", "Northern Cemetery"],
            "description": "Historic necropolis with people living among tombs",
            "ticket_price": None,  # Free (guided tours cost)
            "expected_rating": 4.2,
            "UNESCO_site": False
        },
        {
            "name": "Mosque of Qijmas Al-Ishaqi",
            "name_arabic": "جامع قجماس الإسحاقي",
            "category": "Religious",
            "importance": "Minor",
            "search_queries": ["Mosque of Qijmas Al-Ishaqi Cairo"],
            "description": "Historic Mamluk mosque",
            "ticket_price": 15.0,
            "expected_rating": 4.0,
            "UNESCO_site": True
        },
        {
            "name": "Wadi Degla Protectorate",
            "name_arabic": "وادي دجلا",
            "category": "Natural",
            "importance": "Major",
            "search_queries": ["Wadi Degla Cairo", "Wadi Degla Protectorate"],
            "description": "Natural desert valley with hiking trails",
            "ticket_price": 10.0,
            "expected_rating": 4.3,
            "UNESCO_site": False
        },
        {
            "name": "Al-Ahram Street (Pyramids Road)",
            "name_arabic": "شارع الأهرام",
            "category": "Entertainment",
            "importance": "Major",
            "search_queries": ["Pyramids Road Cairo", "Ahram Street Giza"],
            "description": "Famous street leading to Pyramids with restaurants and cafes",
            "ticket_price": None,  # Free
            "expected_rating": 4.2,
            "UNESCO_site": False
        },
        {
            "name": "Cairo International Conference Center",
            "name_arabic": "مركز القاهرة الدولي للمؤتمرات",
            "category": "Cultural",
            "importance": "Minor",
            "search_queries": ["CICC Cairo", "Cairo International Conference Center"],
            "description": "Major venue for conferences and events",
            "ticket_price": None,  # Varies by event
            "expected_rating": 4.0,
            "UNESCO_site": False
        },
        {
            "name": "Zamalek Art Gallery",
            "name_arabic": "معرض الزمالك للفنون",
            "category": "Cultural",
            "importance": "Minor",
            "search_queries": ["Zamalek Art Gallery Cairo", "Art Galleries Zamalek"],
            "description": "Contemporary Egyptian art gallery",
            "ticket_price": None,  # Free
            "expected_rating": 4.1,
            "UNESCO_site": False
        },
        {
            "name": "Townhouse Gallery",
            "name_arabic": "تاون هاوس جاليري",
            "category": "Cultural",
            "importance": "Minor",
            "search_queries": ["Townhouse Gallery Cairo", "Townhouse Gallery Downtown"],
            "description": "Contemporary art space in downtown Cairo",
            "ticket_price": None,  # Free
            "expected_rating": 4.0,
            "UNESCO_site": False
        },
        {
            "name": "Darb 1718",
            "name_arabic": "درب 1718",
            "category": "Cultural",
            "importance": "Minor",
            "search_queries": ["Darb 1718 Cairo", "Darb 1718 Contemporary Art"],
            "description": "Contemporary art and culture center in Old Cairo",
            "ticket_price": None,  # Varies by event
            "expected_rating": 4.2,
            "UNESCO_site": False
        },
        {
            "name": "Falaki Theatre",
            "name_arabic": "مسرح الفلكي",
            "category": "Cultural",
            "importance": "Minor",
            "search_queries": ["Falaki Theatre Cairo", "AUC Falaki Theater"],
            "description": "University theater with cultural performances",
            "ticket_price": None,  # Varies by show
            "expected_rating": 4.0,
            "UNESCO_site": False
        },
        {
            "name": "Ramses Railway Station",
            "name_arabic": "محطة رمسيس",
            "category": "Transportation",
            "importance": "Major",
            "search_queries": ["Ramses Station Cairo", "Cairo Railway Station"],
            "description": "Cairo's main railway station",
            "ticket_price": None,  # Free
            "expected_rating": 3.9,
            "UNESCO_site": False
        },
        {
            "name": "Cairo Stadium Indoor Halls Complex",
            "name_arabic": "صالات القاهرة المغطاة",
            "category": "Entertainment",
            "importance": "Minor",
            "search_queries": ["Cairo Stadium Indoor Halls", "Cairo Indoor Sports Complex"],
            "description": "Indoor sports and entertainment venue",
            "ticket_price": None,  # Varies by event
            "expected_rating": 4.0,
            "UNESCO_site": False
        },
        {
            "name": "Mosque of Abu Dahab",
            "name_arabic": "جامع أبو الذهب",
            "category": "Religious",
            "importance": "Minor",
            "search_queries": ["Mosque of Abu Dahab Cairo", "Abu Dahab Mosque"],
            "description": "Historic mosque complex in Islamic Cairo",
            "ticket_price": None,  # Free
            "expected_rating": 4.0,
            "UNESCO_site": True
        },
        {
            "name": "Mosque of Gawhar Al-Lala",
            "name_arabic": "جامع جوهر اللالة",
            "category": "Religious",
            "importance": "Minor",
            "search_queries": ["Mosque of Gawhar Al-Lala Cairo"],
            "description": "Historic mosque near Al-Azhar",
            "ticket_price": None,  # Free
            "expected_rating": 3.8,
            "UNESCO_site": False
        },
        {
            "name": "Mosque of Al-Saleh Aybak",
            "name_arabic": "جامع الصالح أيبك",
            "category": "Religious",
            "importance": "Minor",
            "search_queries": ["Mosque of Al-Saleh Aybak Cairo"],
            "description": "Historic mosque complex",
            "ticket_price": 15.0,
            "expected_rating": 3.9,
            "UNESCO_site": False
        }

    ],
    "Giza": [
        {"name": "Great Pyramid of Giza (Khufu)", "name_arabic": "هرم خوفو الأكبر", "category": "Historical", "importance": "World Wonder", "search_queries": ["Great Pyramid Giza", "Khufu Pyramid", "Pyramid of Cheops"], "description": "Largest of the three pyramids, oldest of the Seven Wonders", "ticket_price": 240.0, "expected_rating": 4.9, "UNESCO_site": True},
        {"name": "Pyramid of Khafre", "name_arabic": "هرم خفرع", "category": "Historical", "importance": "World Wonder", "search_queries": ["Pyramid of Khafre", "Khafre Pyramid", "Chephren Pyramid"], "description": "Second-largest pyramid, distinctive with its casing stones", "ticket_price": 240.0, "expected_rating": 4.8, "UNESCO_site": True},
        {"name": "Pyramid of Menkaure", "name_arabic": "هرم منكاور", "category": "Historical", "importance": "World Wonder", "search_queries": ["Menkaure Pyramid", "Pyramid of Menkaure", "Mycerinus Pyramid"], "description": "Smallest of the three main Giza pyramids", "ticket_price": 100.0, "expected_rating": 4.7, "UNESCO_site": True},
        {"name": "Great Sphinx of Giza", "name_arabic": "أبو الهول", "category": "Historical", "importance": "World Wonder", "search_queries": ["Great Sphinx Giza", "The Sphinx Egypt", "Abu al-Haul"], "description": "Iconic limestone statue with lion body and human head", "ticket_price": 240.0, "expected_rating": 4.8, "UNESCO_site": True},
        {"name": "Giza Plateau", "name_arabic": "هضبة الأهرامات", "category": "Historical", "importance": "World Wonder", "search_queries": ["Giza Plateau", "Pyramid Plateau Egypt"], "description": "Archaeological site containing the three pyramids and Sphinx", "ticket_price": 240.0, "expected_rating": 4.9, "UNESCO_site": True},
        {"name": "Giza Solar Boat Museum", "name_arabic": "متحف القارب الشمسي", "category": "Cultural", "importance": "Major", "search_queries": ["Solar Boat Museum Giza", "Khufu Ship Museum"], "description": "Houses the reconstructed solar boat of Khufu", "ticket_price": 50.0, "expected_rating": 4.5, "UNESCO_site": False},
        {"name": "Grand Egyptian Museum (GEM)", "name_arabic": "المتحف المصري الكبير", "category": "Cultural", "importance": "Must-See", "search_queries": ["Grand Egyptian Museum", "GEM Giza", "New Egyptian Museum"], "description": "State-of-the-art museum near Pyramids, housing Tutankhamun collection", "ticket_price": 150.0, "expected_rating": 4.8, "UNESCO_site": False},
        {"name": "Sound and Light Show Giza", "name_arabic": "العرض الصوتي والضوئي بالأهرامات", "category": "Entertainment", "importance": "Major", "search_queries": ["Sound and Light Show Giza Pyramids", "Pyramids Light Show"], "description": "Evening multimedia show illuminating pyramid history", "ticket_price": 300.0, "expected_rating": 4.3, "UNESCO_site": False},
        {"name": "Pyramids of Queens", "name_arabic": "أهرامات الملكات", "category": "Historical", "importance": "Minor", "search_queries": ["Queens Pyramids Giza", "Pyramid of Hetepheres"], "description": "Smaller pyramids for queens and princesses", "ticket_price": 50.0, "expected_rating": 4.2, "UNESCO_site": True},
        {"name": "Workers Cemetery", "name_arabic": "مقابر العمال", "category": "Historical", "importance": "Major", "search_queries": ["Workers Tombs Giza", "Pyramid Builders Cemetery"], "description": "Tombs of the workers who built the pyramids", "ticket_price": 20.0, "expected_rating": 4.4, "UNESCO_site": False},
        {"name": "Panoramic View Point", "name_arabic": "نقطة بانوراما", "category": "Entertainment", "importance": "Major", "search_queries": ["Pyramids Panoramic View", "Giza Viewpoint"], "description": "Best photo spot for all three pyramids", "ticket_price": None, "expected_rating": 4.6, "UNESCO_site": False},
        {"name": "Giza Necropolis", "name_arabic": "مقابر الجيزة", "category": "Historical", "importance": "World Wonder", "search_queries": ["Giza Necropolis Egypt", "Giza burial grounds"], "description": "Ancient burial complex of pharaohs and nobles", "ticket_price": 240.0, "expected_rating": 4.8, "UNESCO_site": True},
        {"name": "Memphis (Mit Rahina)", "name_arabic": "ممفيس (ميت رهينة)", "category": "Historical", "importance": "Must-See", "search_queries": ["Memphis Egypt", "Mit Rahina Open Air Museum"], "description": "Ancient capital of Egypt, statue of Ramesses II", "ticket_price": 80.0, "expected_rating": 4.5, "UNESCO_site": True},
        {"name": "Saqqara (Step Pyramid)", "name_arabic": "سقارة (هرم سقل)", "category": "Historical", "importance": "Must-See", "search_queries": ["Saqqara Pyramid", "Djoser Step Pyramid", "Step Pyramid Egypt"], "description": "World's oldest stone pyramid, Djoser's Step Pyramid", "ticket_price": 120.0, "expected_rating": 4.7, "UNESCO_site": True},
        {"name": "Dahshur Pyramids", "name_arabic": "أهرامات دهشور", "category": "Historical", "importance": "Must-See", "search_queries": ["Dahshur Pyramids", "Red Pyramid Egypt", "Bent Pyramid"], "description": "Red Pyramid and Bent Pyramid, early smooth-sided pyramids", "ticket_price": 80.0, "expected_rating": 4.6, "UNESCO_site": True},
        {"name": "Red Pyramid", "name_arabic": "الهرم الأحمر", "category": "Historical", "importance": "Major", "search_queries": ["Red Pyramid Dahshur", "North Pyramid Sneferu"], "description": "First successful smooth-sided pyramid, can enter", "ticket_price": 60.0, "expected_rating": 4.6, "UNESCO_site": True},
        {"name": "Bent Pyramid", "name_arabic": "الهرم المائل", "category": "Historical", "importance": "Major", "search_queries": ["Bent Pyramid Dahshur", "Sneferu Bent Pyramid"], "description": "Pyramid with changing angle, recently opened to public", "ticket_price": 60.0, "expected_rating": 4.5, "UNESCO_site": True},
        {"name": "Abusir Pyramids", "name_arabic": "أهرامات أبو صير", "category": "Historical", "importance": "Major", "search_queries": ["Abusir Pyramids", "Abu Sir Egypt"], "description": "Lesser-known pyramid field, Sahure's pyramid", "ticket_price": 60.0, "expected_rating": 4.3, "UNESCO_site": True},
        {"name": "Pharaonic Village", "name_arabic": "القرية الفرعونية", "category": "Cultural", "importance": "Major", "search_queries": ["Pharaonic Village Giza", "Dr. Ragab's Pharaonic Village"], "description": "Living museum recreating ancient Egyptian life", "ticket_price": 150.0, "expected_rating": 4.3, "UNESCO_site": False}
    ],
    "Alexandria": [
        {"name": "Bibliotheca Alexandrina", "name_arabic": "مكتبة الإسكندرية", "category": "Cultural", "importance": "Must-See", "search_queries": ["Bibliotheca Alexandrina", "Alexandria Library Egypt"], "description": "Modern library commemorating ancient Library of Alexandria", "ticket_price": 70.0, "expected_rating": 4.8, "UNESCO_site": False},
        {"name": "Citadel of Qaitbay", "name_arabic": "قلعة قايتباي", "category": "Historical", "importance": "Must-See", "search_queries": ["Citadel of Qaitbay", "Qaitbay Fort Alexandria"], "description": "15th-century fortress on site of ancient Lighthouse", "ticket_price": 50.0, "expected_rating": 4.6, "UNESCO_site": False},
        {"name": "Pompey's Pillar", "name_arabic": "عمود Pompey", "category": "Historical", "importance": "Major", "search_queries": ["Pompey's Pillar Alexandria", "Serapeum Alexandria"], "description": "Roman triumphal column, ancient Alexandria", "ticket_price": 40.0, "expected_rating": 4.4, "UNESCO_site": False},
        {"name": "Alexandria National Museum", "name_arabic": "المتحف القومي بالإسكندرية", "category": "Cultural", "importance": "Major", "search_queries": ["Alexandria National Museum", "Alexandria Museum"], "description": "Museum spanning Pharaonic to modern eras", "ticket_price": 50.0, "expected_rating": 4.5, "UNESCO_site": False},
        {"name": "Montazah Palace Gardens", "name_arabic": "حدائق قصر المنتزة", "category": "Natural", "importance": "Must-See", "search_queries": ["Montazah Palace Alexandria", "Montazah Gardens Egypt"], "description": "Royal palace with beautiful gardens and beaches", "ticket_price": 20.0, "expected_rating": 4.7, "UNESCO_site": False},
        {"name": "Royal Jewelry Museum", "name_arabic": "متحف المجوهرات الملكية", "category": "Cultural", "importance": "Major", "search_queries": ["Royal Jewelry Museum Alexandria"], "description": "Collection of Muhammad Ali dynasty jewelry", "ticket_price": 40.0, "expected_rating": 4.5, "UNESCO_site": False},
        {"name": "Alexandria Corniche", "name_arabic": "كورنيش الإسكندرية", "category": "Entertainment", "importance": "Must-See", "search_queries": ["Alexandria Corniche", "Alexandria waterfront"], "description": "Famous seaside promenade stretching 15km", "ticket_price": None, "expected_rating": 4.7, "UNESCO_site": False},
        {"name": "Catacombs of Kom el Shoqafa", "name_arabic": "مقابر كوم الشقافة", "category": "Historical", "importance": "Must-See", "search_queries": ["Catacombs of Kom el Shoqafa", "Alexandria Catacombs"], "description": "Ancient Roman-Egyptian necropolis", "ticket_price": 60.0, "expected_rating": 4.6, "UNESCO_site": False},
        {"name": "Roman Amphitheater", "name_arabic": "المسرح الروماني", "category": "Historical", "importance": "Major", "search_queries": ["Roman Amphitheater Alexandria", "Kom el-Dikka Alexandria"], "description": "Well-preserved Roman theater with marble seating", "ticket_price": 40.0, "expected_rating": 4.4, "UNESCO_site": False},
        {"name": "Greco-Roman Museum", "name_arabic": "المتحف اليوناني الروماني", "category": "Cultural", "importance": "Major", "search_queries": ["Greco-Roman Museum Alexandria"], "description": "Extensive collection of Roman and Greek artifacts", "ticket_price": 40.0, "expected_rating": 4.4, "UNESCO_site": False},
        {"name": "Abu al-Abbas al-Mursi Mosque", "name_arabic": "مسجد أبو العباس المرسي", "category": "Religious", "importance": "Major", "search_queries": ["Abu al-Abbas Mosque Alexandria"], "description": "Famous 13th-century mosque with Andalusian architecture", "ticket_price": None, "expected_rating": 4.6, "UNESCO_site": False}
    ],
    "Luxor": [
        {"name": "Karnak Temple", "name_arabic": "معبد الكرنك", "category": "Historical", "importance": "World Wonder", "search_queries": ["Karnak Temple Luxor", "Temple of Karnak Egypt"], "description": "Massive ancient Egyptian temple complex, second most visited site", "ticket_price": 200.0, "expected_rating": 4.9, "UNESCO_site": True},
        {"name": "Valley of the Kings", "name_arabic": "وادي الملوك", "category": "Historical", "importance": "World Wonder", "search_queries": ["Valley of the Kings Luxor", "KV Luxor Egypt"], "description": "Ancient burial ground of pharaohs including Tutankhamun", "ticket_price": 300.0, "expected_rating": 4.9, "UNESCO_site": True},
        {"name": "Luxor Temple", "name_arabic": "معبد الأقصر", "category": "Historical", "importance": "World Wonder", "search_queries": ["Luxor Temple Egypt", "Temple of Luxor"], "description": "Ancient Egyptian temple complex on east bank of Nile", "ticket_price": 140.0, "expected_rating": 4.8, "UNESCO_site": True},
        {"name": "Temple of Hatshepsut", "name_arabic": "دير البحري", "category": "Historical", "importance": "World Wonder", "search_queries": ["Hatshepsut Temple Luxor", "Deir el-Bahari Egypt"], "description": "Stunning mortuary temple of female pharaoh Hatshepsut", "ticket_price": 100.0, "expected_rating": 4.8, "UNESCO_site": True},
        {"name": "Colossi of Memnon", "name_arabic": "تمثالا Memnon", "category": "Historical", "importance": "Major", "search_queries": ["Colossi of Memnon Luxor", "Memnon Statues Egypt"], "description": "Two massive stone statues of Pharaoh Amenhotep III", "ticket_price": None, "expected_rating": 4.5, "UNESCO_site": True},
        {"name": "Valley of the Queens", "name_arabic": "وادي الملكات", "category": "Historical", "importance": "Major", "search_queries": ["Valley of the Queens Luxor", "Tombs of the Queens"], "description": "Burial site of ancient Egyptian queens and princes", "ticket_price": 140.0, "expected_rating": 4.6, "UNESCO_site": True},
        {"name": "Deir el-Medina (Workmen's Village)", "name_arabic": "دير المدينة", "category": "Historical", "importance": "Major", "search_queries": ["Deir el-Medina Luxor", "Workmen's Village Egypt"], "description": "Ancient village of tomb builders, Temple of Hathor", "ticket_price": 60.0, "expected_rating": 4.5, "UNESCO_site": False},
        {"name": "Medinet Habu", "name_arabic": "مدينة هابو", "category": "Historical", "importance": "Major", "search_queries": ["Medinet Habu Luxor", "Ramesseum Mortuary Temple"], "description": "Mortuary temple of Ramesses III, well-preserved reliefs", "ticket_price": 80.0, "expected_rating": 4.6, "UNESCO_site": True},
        {"name": "The Ramesseum", "name_arabic": "الرامسيوم", "category": "Historical", "importance": "Major", "search_queries": ["Ramesseum Luxor", "Ramesses II Mortuary Temple"], "description": "Mortuary temple of Ramesses II, fallen colossal statue", "ticket_price": 60.0, "expected_rating": 4.4, "UNESCO_site": False},
        {"name": "Luxor Museum", "name_arabic": "متحف الأقصر", "category": "Cultural", "importance": "Major", "search_queries": ["Luxor Museum Egypt"], "description": "Excellent museum with artifacts from Thebes area", "ticket_price": 100.0, "expected_rating": 4.6, "UNESCO_site": False},
        {"name": "Mummification Museum", "name_arabic": "متحف التحنيط", "category": "Cultural", "importance": "Major", "search_queries": ["Mummification Museum Luxor"], "description": "Museum dedicated to ancient Egyptian mummification process", "ticket_price": 80.0, "expected_rating": 4.4, "UNESCO_site": False},
        {"name": "Avenue of Sphinxes", "name_arabic": "كليس العمالقة", "category": "Historical", "importance": "Major", "search_queries": ["Avenue of Sphinxes Luxor", "Sacred Way Luxor"], "description": "Ancient processional road connecting Karnak and Luxor temples", "ticket_price": None, "expected_rating": 4.7, "UNESCO_site": True},
        {"name": "Tombs of the Nobles", "name_arabic": "مقابر النبلاء", "category": "Historical", "importance": "Major", "search_queries": ["Tombs of the Nobles Luxor", "Tombs of Nobles Egypt"], "description": "Colorful tombs of ancient Egyptian nobles", "ticket_price": 100.0, "expected_rating": 4.5, "UNESCO_site": False},
        {"name": "Deir el-Bahari", "name_arabic": "الدير البحري", "category": "Historical", "importance": "Must-See", "search_queries": ["Deir el-Bahari Temple Complex"], "description": "Temple complex including Hatshepsut and Mentuhotep temples", "ticket_price": 100.0, "expected_rating": 4.8, "UNESCO_site": True},
        {"name": "Tomb of Tutankhamun (KV62)", "name_arabic": "مقبرة توت عنخ آمون", "category": "Historical", "importance": "World Wonder", "search_queries": ["Tutankhamun Tomb Valley of the Kings", "KV62 Luxor"], "description": "Most famous tomb in Valley of the Kings, boy king's burial", "ticket_price": 300.0, "expected_rating": 4.9, "UNESCO_site": True},
        {"name": "Tomb of Seti I (KV17)", "name_arabic": "مقبرة سيتي الأول", "category": "Historical", "importance": "Major", "search_queries": ["Seti I Tomb Luxor", "KV17 Valley of the Kings"], "description": "Longest and deepest tomb in Valley of the Kings", "ticket_price": 300.0, "expected_rating": 4.7, "UNESCO_site": False},
        {"name": "Sound and Light Show Karnak", "name_arabic": "العرض الصوتي والضوئي بالكرنك", "category": "Entertainment", "importance": "Major", "search_queries": ["Sound and Light Karnak Temple"], "description": "Evening light show at Karnak Temple", "ticket_price": 250.0, "expected_rating": 4.4, "UNESCO_site": False},
        {"name": "Luxor Temple at Night", "name_arabic": "معبد الأقصر ليلاً", "category": "Entertainment", "importance": "Must-See", "search_queries": ["Luxor Temple Night Visit"], "description": "Beautifully illuminated temple at night", "ticket_price": 140.0, "expected_rating": 4.8, "UNESCO_site": False}
    ],
    "Aswan": [
        {"name": "Abu Simbel Temples", "name_arabic": "معابد أبو سمبل", "category": "Historical", "importance": "World Wonder", "search_queries": ["Abu Simbel Temples Egypt", "Ramesses II Abu Simbel"], "description": "Massive rock-cut temples saved from Nile flooding", "ticket_price": 350.0, "expected_rating": 4.9, "UNESCO_site": True},
        {"name": "Philae Temple (Isis Temple)", "name_arabic": "معبد فيلة", "category": "Historical", "importance": "World Wonder", "search_queries": ["Philae Temple Aswan", "Temple of Isis Egypt"], "description": "Beautiful island temple dedicated to goddess Isis", "ticket_price": 180.0, "expected_rating": 4.8, "UNESCO_site": True},
        {"name": "Aswan High Dam", "name_arabic": "السد العالي", "category": "Historical", "importance": "Major", "search_queries": ["Aswan High Dam Egypt"], "description": "Engineering marvel controlling Nile floods", "ticket_price": 50.0, "expected_rating": 4.5, "UNESCO_site": False},
        {"name": "Unfinished Obelisk", "name_arabic": "المسلة غير المكتملة", "category": "Historical", "importance": "Major", "search_queries": ["Unfinished Obelisk Aswan", "Aswan Quarries"], "description": "Largest ancient obelisk, abandoned in quarry", "ticket_price": 50.0, "expected_rating": 4.4, "UNESCO_site": False},
        {"name": "Nubian Museum", "name_arabic": "المتحف النوبي", "category": "Cultural", "importance": "Major", "search_queries": ["Nubian Museum Aswan", "Nubian Culture Museum"], "description": "Museum dedicated to Nubian history and culture", "ticket_price": 100.0, "expected_rating": 4.6, "UNESCO_site": False},
        {"name": "Elephantine Island", "name_arabic: "جزيرة الفنتين", "category": "Historical", "importance": "Major", "search_queries": ["Elephantine Island Aswan", "Elephantine Egypt"], "description": "Ancient island with ruins and Nubian villages", "ticket_price": 60.0, "expected_rating": 4.5, "UNESCO_site": False},
        {"name": "Aswan Botanical Garden (Kitchener Island)", "name_arabic": "جزيرة النباتات", "category": "Natural", "importance": "Major", "search_queries": ["Aswan Botanical Garden", "Kitchener Island Egypt"], "description": "Tropical plants on Lord Kitchener's island", "ticket_price": 40.0, "expected_rating": 4.4, "UNESCO_site": False},
        {"name": "Nubian Village", "name_arabic": "القرية النوبية", "category": "Cultural", "importance": "Must-See", "search_queries": ["Nubian Village Aswan", "Gharb Soheil Egypt"], "description": "Colorful traditional Nubian village on West Bank", "ticket_price": 50.0, "expected_rating": 4.7, "UNESCO_site": False},
        {"name": "Mausoleum of Aga Khan", "name_arabic": "ضريح الأغا خان", "category": "Historical", "importance": "Minor", "search_queries": ["Aga Khan Mausoleum Aswan"], "description": "Pink granite mausoleum of Aga Khan III", "ticket_price: None, "expected_rating": 4.3, "UNESCO_site": False},
        {"name": "Sehel Island", "name_arabic": "جزيرة سهيل", "category": "Natural", "importance": "Minor", "search_queries": ["Sehel Island Aswan", "Seheil Island Egypt"], "description": "Island with ancient rock inscriptions", "ticket_price": 40.0, "expected_rating": 4.3, "UNESCO_site": False}
    ],
    "Hurghada": [
        {"name": "Giftun Islands", "name_arabic": "جزر الجفتون", "category": "Natural", "importance": "Must-See", "search_queries": ["Giftun Islands Hurghada", "Giftun Island Egypt"], "description": "Beautiful islands for snorkeling and diving", "ticket_price": 300.0, "expected_rating": 4.7, "UNESCO_site": False},
        {"name": "Hurghada Marina", "name_arabic": "مارينا hurghada", "category": "Entertainment", "importance": "Major", "search_queries": ["Hurghada Marina Egypt"], "description": "Upscale marina with restaurants and shops", "ticket_price": None, "expected_rating": 4.5, "UNESCO_site": False},
        {"name": "El Gouna", "name_arabic": "الجونة", "category": "Entertainment", "importance": "Major", "search_queries": ["El Gouna Red Sea Egypt"], "description": "Upscale resort town with lagoons and golf", "ticket_price": None, "expected_rating": 4.6, "UNESCO_site": False},
        {"name": "Safaga (Port Safaga)", "name_arabic": "سفاجا", "category": "Natural", "importance": "Minor", "search_queries": ["Safaga Egypt Hurghada"], "description": "Port town with black sand beaches", "ticket_price": None, "expected_rating": 4.2, "UNESCO_site": False},
        {"name": "Hurghada Grand Aquarium", "name_arabic": "أكواريوم hurghada", "category": "Natural", "importance": "Major", "search_queries": ["Hurghada Grand Aquarium Egypt"], "description": "Large aquarium with Red Sea marine life", "ticket_price": 100.0, "expected_rating": 4.5, "UNESCO_site": False},
        {"name": "Makadi Water World", "name_arabic: "ماكادي ووتر ورلد", "category": "Entertainment", "importance": "Major", "search_queries": ["Makadi Water Park Hurghada"], "description": "Large water park in Makadi Bay", "ticket_price": 150.0, "expected_rating": 4.4, "UNESCO_site": False},
        {"name": "Senzo Mall", "name_arabic": "سينزو مول", "category": "Shopping", "importance": "Major", "search_queries": ["Senzo Mall Hurghada"], "description": "Modern shopping mall", "ticket_price": None, "expected_rating": 4.3, "UNESCO_site": False}
    ],
    "Marsa Alam": [
        {"name": "Wadi el Gemal National Park", "name_arabic": "وادي الجمال", "category": "Natural", "importance": "Must-See", "search_queries": ["Wadi el Gemal Marsa Alam", "Wadi Gemal Egypt"], "description": "Protected area with beaches, coral reefs, and wildlife", "ticket_price": 50.0, "expected_rating": 4.7, "UNESCO_site": False},
        {"name": "Sataya Reef (Dolphin House)", "name_arabic": "سدaya", "category": "Natural", "importance": "Must-See", "search_queries": ["Sataya Reef Marsa Alam", "Dolphin House Egypt"], "description": "Famous snorkeling spot with wild dolphins", "ticket_price": 350.0, "expected_rating": 4.8, "UNESCO_site": False},
        {"name": "Abu Dabbab Beach", "name_arabic": "شاطئ أبو دباب", "category": "Natural", "importance": "Major", "search_queries": ["Abu Dabbab Marsa Alam", "Dugong Beach Egypt"], "description": "Beach with sea turtles and dugongs", "ticket_price": 100.0, "expected_rating": 4.6, "UNESCO_site": False},
        {"name": "Elphinstone Reef", "name_arabic": "شع المرجانيات", "category": "Natural", "importance": "Major", "search_queries": ["Elphinstone Reef Marsa Alam"], "description": "World-class diving reef with hammerhead sharks", "ticket_price": 400.0, "expected_rating": 4.9, "UNESCO_site": False},
        {"name": "Port Ghalib Marina", "name_arabic": "مارينا بوط غالب", "category": "Entertainment", "importance": "Major", "search_queries": ["Port Ghalib Marsa Alam"], "description": "Upscale marina and resort town", "ticket_price": None, "expected_rating": 4.5, "UNESCO_site": False}
    ],
    "Sinai": [
        {"name": "Mount Sinai (Jabal Musa)", "name_arabic": "جبل موسى", "category": "Historical", "importance": "Must-See", "search_queries": ["Mount Sinai Egypt", "Jabal Musa Sinai"], "description": "Biblical mountain where Moses received Ten Commandments", "ticket_price: 200.0, "expected_rating": 4.8, "UNESCO_site": False},
        {"name": "Saint Catherine's Monastery", "name_arabic: "دير سانت كاترين", "category": "Religious", "importance": "World Wonder", "search_queries": ["Saint Catherine Monastery Egypt", "Saint Catherine's Sinai"], "description": "Oldest continuously operating Christian monastery", "ticket_price: 100.0, "expected_rating": 4.8, "UNESCO_site: True},
        {"name": "Sharm El Sheikh", "name_arabic": "شرم الشيخ", "category": "Entertainment", "importance": "Major", "search_queries": ["Sharm El Sheikh Egypt"], "description": "Famous Red Sea resort town", "ticket_price": None, "expected_rating": 4.6, "UNESCO_site": False},
        {"name": "Ras Mohammed National Park", "name_arabic": "محمية رأس محمد", "category": "Natural", "importance": "Must-See", "search_queries": ["Ras Mohammed Sharm El Sheikh"], "description": "Premier diving spot with coral reefs", "ticket_price: 100.0, "expected_rating": 4.8, "UNESCO_site: False},
        {"name": "Naama Bay", "name_arabic": "خليج نعمة", "category": "Entertainment", "importance": "Major", "search_queries: ["Naama Bay Sharm El Sheikh"], "description": "Popular bay with restaurants and nightlife", "ticket_price: None, "expected_rating": 4.5, "UNESCO_site": False},
        {"name": "Dahab", "name_arabic": "دهب", "category": "Entertainment", "importance": "Major", "search_queries": ["Dahab Egypt Sinai"], "description": "Laid-back beach town famous for diving", "ticket_price": None, "expected_rating": 4.6, "UNESCO_site": False},
        {"name": "Blue Hole (Dahab)", "name_arabic": "الثقب الأزرق", "category": "Natural", "importance": "Must-See", "search_queries: ["Blue Hole Dahab Egypt"], "description": "World-famous diving spot", "ticket_price": 50.0, "expected_rating": 4.7, "UNESCO_site": False},
        {"name": "Saint Catherine Area", "name_arabic": "منطقة سانت كاترين", "category": "Historical", "importance": "Major", "search_queries: ["Saint Catherine Area Egypt"], "description": "UNESCO World Heritage site", "ticket_price: 100.0, "expected_rating": 4.8, "UNESCO_site: True},
        {"name': "Nuweiba", "name_arabic": "نويبع", "category": "Entertainment", "importance": "Minor", "search_queries: ["Nuweiba Egypt Sinai"], "description": "Beach town with ferry to Jordan", "ticket_price: None, "expected_rating": 4.3, "UNESCO_site: False},
        {"name": "Taba", "name_arabic": "طابا", "category": "Entertainment", "importance": "Minor", "search_queries: ["Taba Egypt Sinai"], "description": "Border town with Israel and luxury resorts", "ticket_price: None, "expected_rating": 4.2, "UNESCO_site: False}

    ],
    "Giza": [
        {"name": "Great Pyramid of Giza (Khufu)", "name_arabic": "هرم خوفو الأكبر", "category": "Historical", "importance": "World Wonder", "search_queries": ["Great Pyramid Giza", "Khufu Pyramid", "Pyramid of Cheops"], "description": "Largest of the three pyramids, oldest of the Seven Wonders", "ticket_price": 240.0, "expected_rating": 4.9, "UNESCO_site": True},
        {"name": "Pyramid of Khafre", "name_arabic": "هرم خفرع", "category": "Historical", "importance": "World Wonder", "search_queries": ["Pyramid of Khafre", "Khafre Pyramid", "Chephren Pyramid"], "description": "Second-largest pyramid, distinctive with its casing stones", "ticket_price": 240.0, "expected_rating": 4.8, "UNESCO_site": True},
        {"name": "Pyramid of Menkaure", "name_arabic": "هرم منكاور", "category": "Historical", "importance": "World Wonder", "search_queries": ["Menkaure Pyramid", "Pyramid of Menkaure", "Mycerinus Pyramid"], "description": "Smallest of the three main Giza pyramids", "ticket_price": 100.0, "expected_rating": 4.7, "UNESCO_site": True},
        {"name": "Great Sphinx of Giza", "name_arabic": "أبو الهول", "category": "Historical", "importance": "World Wonder", "search_queries": ["Great Sphinx Giza", "The Sphinx Egypt", "Abu al-Haul"], "description": "Iconic limestone statue with lion body and human head", "ticket_price": 240.0, "expected_rating": 4.8, "UNESCO_site": True},
        {"name": "Giza Plateau", "name_arabic": "هضبة الأهرامات", "category": "Historical", "importance": "World Wonder", "search_queries": ["Giza Plateau", "Pyramid Plateau Egypt"], "description": "Archaeological site containing the three pyramids and Sphinx", "ticket_price": 240.0, "expected_rating": 4.9, "UNESCO_site": True},
        {"name": "Giza Solar Boat Museum", "name_arabic": "متحف القارب الشمسي", "category": "Cultural", "importance": "Major", "search_queries": ["Solar Boat Museum Giza", "Khufu Ship Museum"], "description": "Houses the reconstructed solar boat of Khufu", "ticket_price": 50.0, "expected_rating": 4.5, "UNESCO_site": False},
        {"name": "Grand Egyptian Museum (GEM)", "name_arabic": "المتحف المصري الكبير", "category": "Cultural", "importance": "Must-See", "search_queries": ["Grand Egyptian Museum", "GEM Giza", "New Egyptian Museum"], "description": "State-of-the-art museum near Pyramids, housing Tutankhamun collection", "ticket_price": 150.0, "expected_rating": 4.8, "UNESCO_site": False},
        {"name": "Sound and Light Show Giza", "name_arabic": "العرض الصوتي والضوئي بالأهرامات", "category": "Entertainment", "importance": "Major", "search_queries": ["Sound and Light Show Giza Pyramids", "Pyramids Light Show"], "description": "Evening multimedia show illuminating pyramid history", "ticket_price": 300.0, "expected_rating": 4.3, "UNESCO_site": False},
        {"name": "Pyramids of Queens", "name_arabic": "أهرامات الملكات", "category": "Historical", "importance": "Minor", "search_queries": ["Queens Pyramids Giza", "Pyramid of Hetepheres"], "description": "Smaller pyramids for queens and princesses", "ticket_price": 50.0, "expected_rating": 4.2, "UNESCO_site": True},
        {"name": "Workers Cemetery", "name_arabic": "مقابر العمال", "category": "Historical", "importance": "Major", "search_queries": ["Workers Tombs Giza", "Pyramid Builders Cemetery"], "description": "Tombs of the workers who built the pyramids", "ticket_price": 20.0, "expected_rating": 4.4, "UNESCO_site": False},
        {"name": "Panoramic View Point", "name_arabic": "نقطة بانوراما", "category": "Entertainment", "importance": "Major", "search_queries": ["Pyramids Panoramic View", "Giza Viewpoint"], "description": "Best photo spot for all three pyramids", "ticket_price": None, "expected_rating": 4.6, "UNESCO_site": False},
        {"name": "Giza Necropolis", "name_arabic": "مقابر الجيزة", "category": "Historical", "importance": "World Wonder", "search_queries": ["Giza Necropolis Egypt", "Giza burial grounds"], "description": "Ancient burial complex of pharaohs and nobles", "ticket_price": 240.0, "expected_rating": 4.8, "UNESCO_site": True},
        {"name": "Memphis (Mit Rahina)", "name_arabic": "ممفيس (ميت رهينة)", "category": "Historical", "importance": "Must-See", "search_queries": ["Memphis Egypt", "Mit Rahina Open Air Museum"], "description": "Ancient capital of Egypt, statue of Ramesses II", "ticket_price": 80.0, "expected_rating": 4.5, "UNESCO_site": True},
        {"name": "Saqqara (Step Pyramid)", "name_arabic": "سقارة (هرم سقل)", "category": "Historical", "importance": "Must-See", "search_queries": ["Saqqara Pyramid", "Djoser Step Pyramid", "Step Pyramid Egypt"], "description": "World's oldest stone pyramid, Djoser's Step Pyramid", "ticket_price": 120.0, "expected_rating": 4.7, "UNESCO_site": True},
        {"name": "Dahshur Pyramids", "name_arabic": "أهرامات دهشور", "category": "Historical", "importance": "Must-See", "search_queries": ["Dahshur Pyramids", "Red Pyramid Egypt", "Bent Pyramid"], "description": "Red Pyramid and Bent Pyramid, early smooth-sided pyramids", "ticket_price": 80.0, "expected_rating": 4.6, "UNESCO_site": True},
        {"name": "Red Pyramid", "name_arabic": "الهرم الأحمر", "category": "Historical", "importance": "Major", "search_queries": ["Red Pyramid Dahshur", "North Pyramid Sneferu"], "description": "First successful smooth-sided pyramid, can enter", "ticket_price": 60.0, "expected_rating": 4.6, "UNESCO_site": True},
        {"name": "Bent Pyramid", "name_arabic": "الهرم المائل", "category": "Historical", "importance": "Major", "search_queries": ["Bent Pyramid Dahshur", "Sneferu Bent Pyramid"], "description": "Pyramid with changing angle, recently opened to public", "ticket_price": 60.0, "expected_rating": 4.5, "UNESCO_site": True},
        {"name": "Abusir Pyramids", "name_arabic": "أهرامات أبو صير", "category": "Historical", "importance": "Major", "search_queries": ["Abusir Pyramids", "Abu Sir Egypt"], "description": "Lesser-known pyramid field, Sahure's pyramid", "ticket_price": 60.0, "expected_rating": 4.3, "UNESCO_site": True},
        {"name": "Pharaonic Village", "name_arabic": "القرية الفرعونية", "category": "Cultural", "importance": "Major", "search_queries": ["Pharaonic Village Giza", "Dr. Ragab's Pharaonic Village"], "description": "Living museum recreating ancient Egyptian life", "ticket_price": 150.0, "expected_rating": 4.3, "UNESCO_site": False}
    ],
    "Alexandria": [
        {"name": "Bibliotheca Alexandrina", "name_arabic": "مكتبة الإسكندرية", "category": "Cultural", "importance": "Must-See", "search_queries": ["Bibliotheca Alexandrina", "Alexandria Library Egypt"], "description": "Modern library commemorating ancient Library of Alexandria", "ticket_price": 70.0, "expected_rating": 4.8, "UNESCO_site": False},
        {"name": "Citadel of Qaitbay", "name_arabic": "قلعة قايتباي", "category": "Historical", "importance": "Must-See", "search_queries": ["Citadel of Qaitbay", "Qaitbay Fort Alexandria"], "description": "15th-century fortress on site of ancient Lighthouse", "ticket_price": 50.0, "expected_rating": 4.6, "UNESCO_site": False},
        {"name": "Pompey's Pillar", "name_arabic": "عمود Pompey", "category": "Historical", "importance": "Major", "search_queries": ["Pompey's Pillar Alexandria", "Serapeum Alexandria"], "description": "Roman triumphal column, ancient Alexandria", "ticket_price": 40.0, "expected_rating": 4.4, "UNESCO_site": False},
        {"name": "Alexandria National Museum", "name_arabic": "المتحف القومي بالإسكندرية", "category": "Cultural", "importance": "Major", "search_queries": ["Alexandria National Museum", "Alexandria Museum"], "description": "Museum spanning Pharaonic to modern eras", "ticket_price": 50.0, "expected_rating": 4.5, "UNESCO_site": False},
        {"name": "Montazah Palace Gardens", "name_arabic": "حدائق قصر المنتزة", "category": "Natural", "importance": "Must-See", "search_queries": ["Montazah Palace Alexandria", "Montazah Gardens Egypt"], "description": "Royal palace with beautiful gardens and beaches", "ticket_price": 20.0, "expected_rating": 4.7, "UNESCO_site": False},
        {"name": "Royal Jewelry Museum", "name_arabic": "متحف المجوهرات الملكية", "category": "Cultural", "importance": "Major", "search_queries": ["Royal Jewelry Museum Alexandria"], "description": "Collection of Muhammad Ali dynasty jewelry", "ticket_price": 40.0, "expected_rating": 4.5, "UNESCO_site": False},
        {"name": "Alexandria Corniche", "name_arabic": "كورنيش الإسكندرية", "category": "Entertainment", "importance": "Must-See", "search_queries": ["Alexandria Corniche", "Alexandria waterfront"], "description": "Famous seaside promenade stretching 15km", "ticket_price": None, "expected_rating": 4.7, "UNESCO_site": False},
        {"name": "Catacombs of Kom el Shoqafa", "name_arabic": "مقابر كوم الشقافة", "category": "Historical", "importance": "Must-See", "search_queries": ["Catacombs of Kom el Shoqafa", "Alexandria Catacombs"], "description": "Ancient Roman-Egyptian necropolis", "ticket_price": 60.0, "expected_rating": 4.6, "UNESCO_site": False},
        {"name": "Roman Amphitheater", "name_arabic": "المسرح الروماني", "category": "Historical", "importance": "Major", "search_queries": ["Roman Amphitheater Alexandria", "Kom el-Dikka Alexandria"], "description": "Well-preserved Roman theater with marble seating", "ticket_price": 40.0, "expected_rating": 4.4, "UNESCO_site": False},
        {"name": "Greco-Roman Museum", "name_arabic": "المتحف اليوناني الروماني", "category": "Cultural", "importance": "Major", "search_queries": ["Greco-Roman Museum Alexandria"], "description": "Extensive collection of Roman and Greek artifacts", "ticket_price": 40.0, "expected_rating": 4.4, "UNESCO_site": False},
        {"name": "Abu al-Abbas al-Mursi Mosque", "name_arabic": "مسجد أبو العباس المرسي", "category": "Religious", "importance": "Major", "search_queries": ["Abu al-Abbas Mosque Alexandria"], "description": "Famous 13th-century mosque with Andalusian architecture", "ticket_price": None, "expected_rating": 4.6, "UNESCO_site": False}
    ],
    "Luxor": [
        {"name": "Karnak Temple", "name_arabic": "معبد الكرنك", "category": "Historical", "importance": "World Wonder", "search_queries": ["Karnak Temple Luxor", "Temple of Karnak Egypt"], "description": "Massive ancient Egyptian temple complex, second most visited site", "ticket_price": 200.0, "expected_rating": 4.9, "UNESCO_site": True},
        {"name": "Valley of the Kings", "name_arabic": "وادي الملوك", "category": "Historical", "importance": "World Wonder", "search_queries": ["Valley of the Kings Luxor", "KV Luxor Egypt"], "description": "Ancient burial ground of pharaohs including Tutankhamun", "ticket_price": 300.0, "expected_rating": 4.9, "UNESCO_site": True},
        {"name": "Luxor Temple", "name_arabic": "معبد الأقصر", "category": "Historical", "importance": "World Wonder", "search_queries": ["Luxor Temple Egypt", "Temple of Luxor"], "description": "Ancient Egyptian temple complex on east bank of Nile", "ticket_price": 140.0, "expected_rating": 4.8, "UNESCO_site": True},
        {"name": "Temple of Hatshepsut", "name_arabic": "دير البحري", "category": "Historical", "importance": "World Wonder", "search_queries": ["Hatshepsut Temple Luxor", "Deir el-Bahari Egypt"], "description": "Stunning mortuary temple of female pharaoh Hatshepsut", "ticket_price": 100.0, "expected_rating": 4.8, "UNESCO_site": True},
        {"name": "Colossi of Memnon", "name_arabic": "تمثالا Memnon", "category": "Historical", "importance": "Major", "search_queries": ["Colossi of Memnon Luxor", "Memnon Statues Egypt"], "description": "Two massive stone statues of Pharaoh Amenhotep III", "ticket_price": None, "expected_rating": 4.5, "UNESCO_site": True},
        {"name": "Valley of the Queens", "name_arabic": "وادي الملكات", "category": "Historical", "importance": "Major", "search_queries": ["Valley of the Queens Luxor", "Tombs of the Queens"], "description": "Burial site of ancient Egyptian queens and princes", "ticket_price": 140.0, "expected_rating": 4.6, "UNESCO_site": True},
        {"name": "Deir el-Medina (Workmen's Village)", "name_arabic": "دير المدينة", "category": "Historical", "importance": "Major", "search_queries": ["Deir el-Medina Luxor", "Workmen's Village Egypt"], "description": "Ancient village of tomb builders, Temple of Hathor", "ticket_price": 60.0, "expected_rating": 4.5, "UNESCO_site": False},
        {"name": "Medinet Habu", "name_arabic": "مدينة هابو", "category": "Historical", "importance": "Major", "search_queries": ["Medinet Habu Luxor", "Ramesseum Mortuary Temple"], "description": "Mortuary temple of Ramesses III, well-preserved reliefs", "ticket_price": 80.0, "expected_rating": 4.6, "UNESCO_site": True},
        {"name": "The Ramesseum", "name_arabic": "الرامسيوم", "category": "Historical", "importance": "Major", "search_queries": ["Ramesseum Luxor", "Ramesses II Mortuary Temple"], "description": "Mortuary temple of Ramesses II, fallen colossal statue", "ticket_price": 60.0, "expected_rating": 4.4, "UNESCO_site": False},
        {"name": "Luxor Museum", "name_arabic": "متحف الأقصر", "category": "Cultural", "importance": "Major", "search_queries": ["Luxor Museum Egypt"], "description": "Excellent museum with artifacts from Thebes area", "ticket_price": 100.0, "expected_rating": 4.6, "UNESCO_site": False},
        {"name": "Mummification Museum", "name_arabic": "متحف التحنيط", "category": "Cultural", "importance": "Major", "search_queries": ["Mummification Museum Luxor"], "description": "Museum dedicated to ancient Egyptian mummification process", "ticket_price": 80.0, "expected_rating": 4.4, "UNESCO_site": False},
        {"name": "Avenue of Sphinxes", "name_arabic": "كليس العمالقة", "category": "Historical", "importance": "Major", "search_queries": ["Avenue of Sphinxes Luxor", "Sacred Way Luxor"], "description": "Ancient processional road connecting Karnak and Luxor temples", "ticket_price": None, "expected_rating": 4.7, "UNESCO_site": True},
        {"name": "Tombs of the Nobles", "name_arabic": "مقابر النبلاء", "category": "Historical", "importance": "Major", "search_queries": ["Tombs of the Nobles Luxor", "Tombs of Nobles Egypt"], "description": "Colorful tombs of ancient Egyptian nobles", "ticket_price": 100.0, "expected_rating": 4.5, "UNESCO_site": False},
        {"name": "Deir el-Bahari", "name_arabic": "الدير البحري", "category": "Historical", "importance": "Must-See", "search_queries": ["Deir el-Bahari Temple Complex"], "description": "Temple complex including Hatshepsut and Mentuhotep temples", "ticket_price": 100.0, "expected_rating": 4.8, "UNESCO_site": True},
        {"name": "Tomb of Tutankhamun (KV62)", "name_arabic": "مقبرة توت عنخ آمون", "category": "Historical", "importance": "World Wonder", "search_queries": ["Tutankhamun Tomb Valley of the Kings", "KV62 Luxor"], "description": "Most famous tomb in Valley of the Kings, boy king's burial", "ticket_price": 300.0, "expected_rating": 4.9, "UNESCO_site": True},
        {"name": "Tomb of Seti I (KV17)", "name_arabic": "مقبرة سيتي الأول", "category": "Historical", "importance": "Major", "search_queries": ["Seti I Tomb Luxor", "KV17 Valley of the Kings"], "description": "Longest and deepest tomb in Valley of the Kings", "ticket_price": 300.0, "expected_rating": 4.7, "UNESCO_site": False},
        {"name": "Sound and Light Show Karnak", "name_arabic": "العرض الصوتي والضوئي بالكرنك", "category": "Entertainment", "importance": "Major", "search_queries": ["Sound and Light Karnak Temple"], "description": "Evening light show at Karnak Temple", "ticket_price": 250.0, "expected_rating": 4.4, "UNESCO_site": False},
        {"name": "Luxor Temple at Night", "name_arabic": "معبد الأقصر ليلاً", "category": "Entertainment", "importance": "Must-See", "search_queries": ["Luxor Temple Night Visit"], "description": "Beautifully illuminated temple at night", "ticket_price": 140.0, "expected_rating": 4.8, "UNESCO_site": False}
    ],
    "Aswan": [
        {"name": "Abu Simbel Temples", "name_arabic": "معابد أبو سمبل", "category": "Historical", "importance": "World Wonder", "search_queries": ["Abu Simbel Temples Egypt", "Ramesses II Abu Simbel"], "description": "Massive rock-cut temples saved from Nile flooding", "ticket_price": 350.0, "expected_rating": 4.9, "UNESCO_site": True},
        {"name": "Philae Temple (Isis Temple)", "name_arabic": "معبد فيلة", "category": "Historical", "importance": "World Wonder", "search_queries": ["Philae Temple Aswan", "Temple of Isis Egypt"], "description": "Beautiful island temple dedicated to goddess Isis", "ticket_price": 180.0, "expected_rating": 4.8, "UNESCO_site": True},
        {"name": "Aswan High Dam", "name_arabic": "السد العالي", "category": "Historical", "importance": "Major", "search_queries": ["Aswan High Dam Egypt"], "description": "Engineering marvel controlling Nile floods", "ticket_price": 50.0, "expected_rating": 4.5, "UNESCO_site": False},
        {"name": "Unfinished Obelisk", "name_arabic": "المسلة غير المكتملة", "category": "Historical", "importance": "Major", "search_queries": ["Unfinished Obelisk Aswan", "Aswan Quarries"], "description": "Largest ancient obelisk, abandoned in quarry", "ticket_price": 50.0, "expected_rating": 4.4, "UNESCO_site": False},
        {"name": "Nubian Museum", "name_arabic": "المتحف النوبي", "category": "Cultural", "importance": "Major", "search_queries": ["Nubian Museum Aswan", "Nubian Culture Museum"], "description": "Museum dedicated to Nubian history and culture", "ticket_price": 100.0, "expected_rating": 4.6, "UNESCO_site": False},
        {"name": "Elephantine Island", "name_arabic: "جزيرة الفنتين", "category": "Historical", "importance": "Major", "search_queries": ["Elephantine Island Aswan", "Elephantine Egypt"], "description": "Ancient island with ruins and Nubian villages", "ticket_price": 60.0, "expected_rating": 4.5, "UNESCO_site": False},
        {"name": "Aswan Botanical Garden (Kitchener Island)", "name_arabic": "جزيرة النباتات", "category": "Natural", "importance": "Major", "search_queries": ["Aswan Botanical Garden", "Kitchener Island Egypt"], "description": "Tropical plants on Lord Kitchener's island", "ticket_price": 40.0, "expected_rating": 4.4, "UNESCO_site": False},
        {"name": "Nubian Village", "name_arabic": "القرية النوبية", "category": "Cultural", "importance": "Must-See", "search_queries": ["Nubian Village Aswan", "Gharb Soheil Egypt"], "description": "Colorful traditional Nubian village on West Bank", "ticket_price": 50.0, "expected_rating": 4.7, "UNESCO_site": False},
        {"name": "Mausoleum of Aga Khan", "name_arabic": "ضريح الأغا خان", "category": "Historical", "importance": "Minor", "search_queries": ["Aga Khan Mausoleum Aswan"], "description": "Pink granite mausoleum of Aga Khan III", "ticket_price: None, "expected_rating": 4.3, "UNESCO_site": False},
        {"name": "Sehel Island", "name_arabic": "جزيرة سهيل", "category": "Natural", "importance": "Minor", "search_queries": ["Sehel Island Aswan", "Seheil Island Egypt"], "description": "Island with ancient rock inscriptions", "ticket_price": 40.0, "expected_rating": 4.3, "UNESCO_site": False}
    ],
    "Hurghada": [
        {"name": "Giftun Islands", "name_arabic": "جزر الجفتون", "category": "Natural", "importance": "Must-See", "search_queries": ["Giftun Islands Hurghada", "Giftun Island Egypt"], "description": "Beautiful islands for snorkeling and diving", "ticket_price": 300.0, "expected_rating": 4.7, "UNESCO_site": False},
        {"name": "Hurghada Marina", "name_arabic": "مارينا hurghada", "category": "Entertainment", "importance": "Major", "search_queries": ["Hurghada Marina Egypt"], "description": "Upscale marina with restaurants and shops", "ticket_price": None, "expected_rating": 4.5, "UNESCO_site": False},
        {"name": "El Gouna", "name_arabic": "الجونة", "category": "Entertainment", "importance": "Major", "search_queries": ["El Gouna Red Sea Egypt"], "description": "Upscale resort town with lagoons and golf", "ticket_price": None, "expected_rating": 4.6, "UNESCO_site": False},
        {"name": "Safaga (Port Safaga)", "name_arabic": "سفاجا", "category": "Natural", "importance": "Minor", "search_queries": ["Safaga Egypt Hurghada"], "description": "Port town with black sand beaches", "ticket_price": None, "expected_rating": 4.2, "UNESCO_site": False},
        {"name": "Hurghada Grand Aquarium", "name_arabic": "أكواريوم hurghada", "category": "Natural", "importance": "Major", "search_queries": ["Hurghada Grand Aquarium Egypt"], "description": "Large aquarium with Red Sea marine life", "ticket_price": 100.0, "expected_rating": 4.5, "UNESCO_site": False},
        {"name": "Makadi Water World", "name_arabic: "ماكادي ووتر ورلد", "category": "Entertainment", "importance": "Major", "search_queries": ["Makadi Water Park Hurghada"], "description": "Large water park in Makadi Bay", "ticket_price": 150.0, "expected_rating": 4.4, "UNESCO_site": False},
        {"name": "Senzo Mall", "name_arabic": "سينزو مول", "category": "Shopping", "importance": "Major", "search_queries": ["Senzo Mall Hurghada"], "description": "Modern shopping mall", "ticket_price": None, "expected_rating": 4.3, "UNESCO_site": False}
    ],
    "Marsa Alam": [
        {"name": "Wadi el Gemal National Park", "name_arabic": "وادي الجمال", "category": "Natural", "importance": "Must-See", "search_queries": ["Wadi el Gemal Marsa Alam", "Wadi Gemal Egypt"], "description": "Protected area with beaches, coral reefs, and wildlife", "ticket_price": 50.0, "expected_rating": 4.7, "UNESCO_site": False},
        {"name": "Sataya Reef (Dolphin House)", "name_arabic": "سدaya", "category": "Natural", "importance": "Must-See", "search_queries": ["Sataya Reef Marsa Alam", "Dolphin House Egypt"], "description": "Famous snorkeling spot with wild dolphins", "ticket_price": 350.0, "expected_rating": 4.8, "UNESCO_site": False},
        {"name": "Abu Dabbab Beach", "name_arabic": "شاطئ أبو دباب", "category": "Natural", "importance": "Major", "search_queries": ["Abu Dabbab Marsa Alam", "Dugong Beach Egypt"], "description": "Beach with sea turtles and dugongs", "ticket_price": 100.0, "expected_rating": 4.6, "UNESCO_site": False},
        {"name": "Elphinstone Reef", "name_arabic": "شع المرجانيات", "category": "Natural", "importance": "Major", "search_queries": ["Elphinstone Reef Marsa Alam"], "description": "World-class diving reef with hammerhead sharks", "ticket_price": 400.0, "expected_rating": 4.9, "UNESCO_site": False},
        {"name": "Port Ghalib Marina", "name_arabic": "مارينا بوط غالب", "category": "Entertainment", "importance": "Major", "search_queries": ["Port Ghalib Marsa Alam"], "description": "Upscale marina and resort town", "ticket_price": None, "expected_rating": 4.5, "UNESCO_site": False}
    ],
    "Sinai": [
        {"name": "Mount Sinai (Jabal Musa)", "name_arabic": "جبل موسى", "category": "Historical", "importance": "Must-See", "search_queries": ["Mount Sinai Egypt", "Jabal Musa Sinai"], "description": "Biblical mountain where Moses received Ten Commandments", "ticket_price: 200.0, "expected_rating": 4.8, "UNESCO_site": False},
        {"name": "Saint Catherine's Monastery", "name_arabic: "دير سانت كاترين", "category": "Religious", "importance": "World Wonder", "search_queries": ["Saint Catherine Monastery Egypt", "Saint Catherine's Sinai"], "description": "Oldest continuously operating Christian monastery", "ticket_price: 100.0, "expected_rating": 4.8, "UNESCO_site: True},
        {"name": "Sharm El Sheikh", "name_arabic": "شرم الشيخ", "category": "Entertainment", "importance": "Major", "search_queries": ["Sharm El Sheikh Egypt"], "description": "Famous Red Sea resort town", "ticket_price": None, "expected_rating": 4.6, "UNESCO_site": False},
        {"name": "Ras Mohammed National Park", "name_arabic": "محمية رأس محمد", "category": "Natural", "importance": "Must-See", "search_queries": ["Ras Mohammed Sharm El Sheikh"], "description": "Premier diving spot with coral reefs", "ticket_price: 100.0, "expected_rating": 4.8, "UNESCO_site: False},
        {"name": "Naama Bay", "name_arabic": "خليج نعمة", "category": "Entertainment", "importance": "Major", "search_queries: ["Naama Bay Sharm El Sheikh"], "description": "Popular bay with restaurants and nightlife", "ticket_price: None, "expected_rating": 4.5, "UNESCO_site": False},
        {"name": "Dahab", "name_arabic": "دهب", "category": "Entertainment", "importance": "Major", "search_queries": ["Dahab Egypt Sinai"], "description": "Laid-back beach town famous for diving", "ticket_price": None, "expected_rating": 4.6, "UNESCO_site": False},
        {"name": "Blue Hole (Dahab)", "name_arabic": "الثقب الأزرق", "category": "Natural", "importance": "Must-See", "search_queries: ["Blue Hole Dahab Egypt"], "description": "World-famous diving spot", "ticket_price": 50.0, "expected_rating": 4.7, "UNESCO_site": False},
        {"name": "Saint Catherine Area", "name_arabic": "منطقة سانت كاترين", "category": "Historical", "importance": "Major", "search_queries: ["Saint Catherine Area Egypt"], "description": "UNESCO World Heritage site", "ticket_price: 100.0, "expected_rating": 4.8, "UNESCO_site: True},
        {"name': "Nuweiba", "name_arabic": "نويبع", "category": "Entertainment", "importance": "Minor", "search_queries: ["Nuweiba Egypt Sinai"], "description": "Beach town with ferry to Jordan", "ticket_price: None, "expected_rating": 4.3, "UNESCO_site: False},
        {"name": "Taba", "name_arabic": "طابا", "category": "Entertainment", "importance": "Minor", "search_queries: ["Taba Egypt Sinai"], "description": "Border town with Israel and luxury resorts", "ticket_price: None, "expected_rating": 4.2, "UNESCO_site: False}
    ]
}
