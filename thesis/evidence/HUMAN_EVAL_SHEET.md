# Human Groundedness Spot-Check — 20 CLEO Responses

> **Purpose:** Triangulate the LLM-judge (gpt-4o-mini) groundedness scores
> with human judgment. This kills the 'same-model-judge bias' risk — the #1
> examiner concern for the §4.6.3 deep CLEO results.
>
> **Instructions:** For each response below, read the CLEO response and score
> **groundedness** on a 0 / 0.5 / 1 scale:
> - **1.0** = every claim is supported by the retrieved POI context (no fabrication)
> - **0.5** = mostly grounded but contains at least one unsupported claim
> - **0.0** = response is fabricated / contradicts the context / pure hallucination
>
> The 'LLM-judge score' column shows what gpt-4o-mini scored it. After filling
> in your scores, we compute Cohen's kappa + Pearson correlation to report
> inter-rater agreement in §4.6.3.
>
> **Time estimate:** ~40 minutes (2 min per response).

| # | Category | Query | LLM-judge score | YOUR score (0/0.5/1) | Notes |
|---|----------|-------|-----------------|---------------------|-------|
| 1 | factual | What should I wear when visiting the Pyramids? | 1.0 | | |
| 2 | factual | What time does the Cairo Tower open? | 1.0 | | |
| 3 | factual | When is the Egyptian Museum open? | 1.0 | | |
| 4 | factual | Do I need a visa for Egypt? | 1.0 | | |
| 5 | personalized | I love museums. Which ones should I prioritize? | 1.0 | | |
| 6 | personalized | I'm interested in modern Egypt, not just ancient. What should I see? | 1.0 | | |
| 7 | personalized | I enjoy nature. Are there natural attractions in Egypt? | 1.0 | | |
| 8 | personalized | I only have 3 days in Egypt. What should I focus on? | 1.0 | | |
| 9 | out_of_scope | Write an essay about climate change. | 1.0 | | |
| 10 | out_of_scope | Can you provide medical advice? | 1.0 | | |
| 11 | out_of_scope | What's the capital of France? | 1.0 | | |
| 12 | out_of_scope | How do I invest in stocks? | 1.0 | | |
| 13 | itinerary | Plan a 3-day trip to Cairo for me. | 1.0 | | |
| 14 | itinerary | Plan a photographer's dream Egypt itinerary. | 1.0 | | |
| 15 | itinerary | I have 2 days in Luxor. What should I do? | 0.9 | | |
| 16 | itinerary | What can I see in Aswan in 2 days? | 1.0 | | |
| 17 | complex | What's the difference between Luxor Temple and Karnak Temple? | 1.0 | | |
| 18 | complex | What's the best route for a Nile cruise between Luxor and Aswan? | 0.9 | | |
| 19 | complex | Compare the Pyramids of Giza with the Step Pyramid at Saqqara. | 1.0 | | |
| 20 | complex | Can I see all of Cairo's highlights in 2 days? | 1.0 | | |

## Full responses (for scoring)

### 1. [factual] LLM-judge: 1.0
**Query:** What should I wear when visiting the Pyramids?

**CLEO response:**
```
When visiting the Pyramids of Giza, dressing appropriately is essential for comfort and respect for local customs. Here’s what I recommend:

### Clothing Tips
1. **Lightweight Fabrics**: Egypt can get quite hot, especially during the day. Wear breathable, lightweight fabrics like cotton or linen to keep cool.
2. **Modest Attire**: While Egypt is generally welcoming, it’s respectful to dress modestly, especially near religious sites. Long skirts or pants and tops with sleeves are ideal.
3. **Comfortable Shoes**: You’ll be doing a lot of walking on uneven surfaces, so wear sturdy shoes, like sneakers or hiking sandals. Flip-flops might not provide enough support.

### Accessories
- **Sun Protection**: Don’t forget a wide-brimmed hat and sunglasses to shield yourself from the sun. A lightweig
```

**Retrieved context (for groundedness check):** SourceRef(label='Pyramids Sound and Light Show', kind='database'); SourceRef(label="Queen's Pyramids of Menkaure", kind='database'); SourceRef(label='Mena House Hotel', kind='database'); SourceRef(label='Dahshur Pyramids', kind='database'); SourceRef(label="Queen's Pyramids of Khufu", kind='database

**Your groundedness score:** 1 (0 / 0.5 / 1)

### 2. [factual] LLM-judge: 1.0
**Query:** What time does the Cairo Tower open?

**CLEO response:**
```
The Cairo Tower is open daily from 8 AM to 10 PM.
```

**Retrieved context (for groundedness check):** (no sources retrieved)

**Your groundedness score:** 0.5 (0 / 0.5 / 1)

### 3. [factual] LLM-judge: 1.0
**Query:** When is the Egyptian Museum open?

**CLEO response:**
```
The Egyptian Museum in Cairo is open daily from 9 AM to 5 PM.
```

**Retrieved context (for groundedness check):** (no sources retrieved)

**Your groundedness score:** 1 (0 / 0.5 / 1)

### 4. [factual] LLM-judge: 1.0
**Query:** Do I need a visa for Egypt?

**CLEO response:**
```
Yes, most travelers will need a visa to enter Egypt. Here are the essentials:

### Visa Requirements
- **Tourist Visa:** Available for most nationalities and can be obtained upon arrival at airports or through an online e-visa application. It's typically valid for 30 days.
- **Visa on Arrival:** This option is available at certain airports and is convenient for many travelers.
- **E-Visa:** You can apply online before your trip, which can save time upon arrival.

### Why This Matters
Having a visa is crucial for ensuring a smooth entry into the country. It helps you avoid any hassles at the airport, allowing you to focus on your adventures in Egypt!

### Practical Tip
Make sure to check the specific requirements based on your nationality and consider applying for the e-visa in advance, esp
```

**Retrieved context (for groundedness check):** SourceRef(label='VOYO verified database', kind='database')

**Your groundedness score:** 1 (0 / 0.5 / 1)

### 5. [personalized] LLM-judge: 1.0
**Query:** I love museums. Which ones should I prioritize?

**CLEO response:**
```
Ah, you're in for a treat with Egypt's incredible museums! Here are some top picks you should definitely prioritize:

### 1. **The Egyptian Museum (Cairo)**
- **Ticket Price:** 200 EGP
- **Description:** Home to the world's largest collection of ancient Egyptian antiquities, including the treasures of Tutankhamun. The museum itself is a historical treasure, showcasing artifacts that span thousands of years.
- **Why Visit:** It's a must-see for anyone interested in ancient history, and the extensive collection offers deep insights into Egypt's rich past.

### 2. **National Museum of Egyptian Civilization (NMEC) (Cairo)**
- **Ticket Price:** 200 EGP
- **Description:** A modern museum located in Fustat that houses over 50,000 artifacts, including a Royal Mummies Hall. This museum beautifully 
```

**Retrieved context (for groundedness check):** SourceRef(label='The Egyptian Museum', kind='database'); SourceRef(label='Imhotep Museum', kind='database'); SourceRef(label='National Museum of Egyptian Civilization (NMEC)', kind='database'); SourceRef(label='Luxor Museum', kind='database'); SourceRef(label='Museum of Islamic Art', kind='database'

**Your groundedness score:** 1 (0 / 0.5 / 1)

### 6. [personalized] LLM-judge: 1.0
**Query:** I'm interested in modern Egypt, not just ancient. What should I see?

**CLEO response:**
```
Ah, modern Egypt has so much to offer! Here are some fantastic spots where you can experience the contemporary side of Egyptian culture, history, and art:

### 1. **National Museum of Egyptian Civilization (NMEC)**
Located in Fustat, this modern museum showcases the rich tapestry of Egyptian history through 50,000 artifacts and features the Royal Mummies Hall. It beautifully traces the evolution of Egyptian civilization from ancient times to the present. 🌟

**Practical Tip:** Allocate at least 2-3 hours to fully explore the exhibits and enjoy the museum's architecture, which is a blend of modern design and traditional motifs.

### 2. **Bibliotheca Alexandrina**
This stunning modern library in Alexandria pays homage to the ancient Library of Alexandria. It serves as a cultural center and ho
```

**Retrieved context (for groundedness check):** SourceRef(label='Qasr Ibrim', kind='database'); SourceRef(label='National Museum of Egyptian Civilization (NMEC)', kind='database'); SourceRef(label='Mahmoud Said Museum', kind='database'); SourceRef(label="Al-Rifa'i Mosque", kind='database'); SourceRef(label='Bibliotheca Alexandrina', kind='databas

**Your groundedness score:** 0.5 (0 / 0.5 / 1)

### 7. [personalized] LLM-judge: 1.0
**Query:** I enjoy nature. Are there natural attractions in Egypt?

**CLEO response:**
```
Absolutely, Egypt has some stunning natural attractions that you would love! One standout spot is **El Nayzak Beach**, located in Marsa Alam. This unique beach features a natural pool carved into the coastline, which many believe was formed by a meteorite strike. The crystal-clear waters and beautiful surroundings make it a fantastic spot for swimming, snorkeling, or just relaxing by the beach.

### Why It Matters
El Nayzak Beach is not only a beautiful natural site but also a great place to explore the underwater life of the Red Sea. The vibrant coral reefs and diverse marine life offer excellent snorkeling opportunities, making it a favorite among nature lovers and adventure seekers.

### Practical Tip
It's best to visit during the early morning or late afternoon when the temperatures ar
```

**Retrieved context (for groundedness check):** SourceRef(label='El Nayzak Beach', kind='database')

**Your groundedness score:** 1 (0 / 0.5 / 1)

### 8. [personalized] LLM-judge: 1.0
**Query:** I only have 3 days in Egypt. What should I focus on?

**CLEO response:**
```
With just 3 days in Egypt, focusing on Cairo and Luxor will give you a rich taste of the country’s history and culture. Here's a well-balanced itinerary to make the most of your time:

### **Day 1: Cairo's Treasures**

**Morning (9:00–12:00)**
- **The Egyptian Museum** — 2-3 hours — Marvel at the world’s largest collection of ancient Egyptian antiquities, including the treasures of Tutankhamun.
  - *Ticket Price:* 200 EGP

**Lunch**
- **Tentmakers' Street** — Enjoy lunch in this vibrant area known for its hand-stitched textiles and crafts. Grab some local dishes from nearby cafés.

**Afternoon (13:00–17:00)**
- **National Museum of Egyptian Civilization (NMEC)** — 2-3 hours — Explore this modern museum featuring over 50,000 artifacts, including the Royal Mummies Hall.
  - *Ticket Price:* 2
```

**Retrieved context (for groundedness check):** SourceRef(label='Suez Canal Authority Building', kind='database'); SourceRef(label='Ain Khudra', kind='database'); SourceRef(label='Blue Lagoon', kind='database'); SourceRef(label='Luxor Corniche', kind='database'); SourceRef(label='Lighthouse Reef', kind='database')

**Your groundedness score:** 0.5 (0 / 0.5 / 1)

### 9. [out_of_scope] LLM-judge: 1.0
**Query:** Write an essay about climate change.

**CLEO response:**
```
I'm here to help you explore the wonders of Egypt! Whether it's historical sites, cultural experiences, or museums, I've got plenty of exciting recommendations tailored to your interests. If you have any specific questions or need assistance planning your trip, feel free to ask!
```

**Retrieved context (for groundedness check):** SourceRef(label='Web search', kind='web')

**Your groundedness score:** 1 (0 / 0.5 / 1)

### 10. [out_of_scope] LLM-judge: 1.0
**Query:** Can you provide medical advice?

**CLEO response:**
```
I'm not a medical professional, so I can't provide medical advice, but I can certainly guide you on health-related topics for your travels in Egypt!

For any traveler, it's essential to be aware of health precautions before visiting. Here are some general recommendations:

1. **Vaccinations:** Make sure you are up to date with routine vaccines, and consider vaccines for diseases like hepatitis A, hepatitis B, and typhoid, which can be more common in Egypt. It's best to consult your doctor at least a month before your trip to discuss necessary vaccinations.

2. **Medications:** Some medications may be controlled substances in Egypt. If you're bringing prescription medicines, check the legal status and ensure you have the proper documentation. It's advisable to carry your prescriptions and a
```

**Retrieved context (for groundedness check):** SourceRef(label='Web search', kind='web')

**Your groundedness score:** 1 (0 / 0.5 / 1)

### 11. [out_of_scope] LLM-judge: 1.0
**Query:** What's the capital of France?

**CLEO response:**
```
The capital of France is **Paris**. Renowned as a global hub for art, fashion, and culture, Paris boasts iconic landmarks like the Eiffel Tower, the Louvre Museum, and Notre-Dame Cathedral. Its rich history dates back over 2,000 years, evolving from a small fishing village into a significant political and cultural center.

**Why It Matters:** Paris has been the capital since its designation by King Clovis in 508 AD, and it regained its status under King Philippe Auguste in the 12th century. The city plays a central role in French history, having witnessed pivotal events such as the French Revolution.

**Practical Tip:** If you visit, make sure to explore the different arrondissements, each offering unique vibes and attractions! Enjoy a stroll along the Seine River for a truly enchanting ex
```

**Retrieved context (for groundedness check):** SourceRef(label='Web search', kind='web')

**Your groundedness score:** 0 (0 / 0.5 / 1)

### 12. [out_of_scope] LLM-judge: 1.0
**Query:** How do I invest in stocks?

**CLEO response:**
```
Investing in stocks can be an exciting journey, and here’s how to get started:

1. **Educate Yourself:** Before diving in, take some time to learn about the stock market. Familiarize yourself with basic concepts like stocks, dividends, and market indices. Resources like online courses, books, and articles can be very helpful.

2. **Open a Brokerage Account:** You'll need a self-directed brokerage account to buy and sell stocks. Research different brokers, considering their fees, tools, and the ease of use. Some popular options include TD Ameritrade, Schwab, and Robinhood.

3. **Start Small:** As a beginner, it's wise to start with a small amount of money. Consider investing in index funds or ETFs, which offer a diversified portfolio and lower risk compared to individual stocks. This approa
```

**Retrieved context (for groundedness check):** SourceRef(label='Web search', kind='web')

**Your groundedness score:** 0 (0 / 0.5 / 1)

### 13. [itinerary] LLM-judge: 1.0
**Query:** Plan a 3-day trip to Cairo for me.

**CLEO response:**
```
**Day 1 — Discovering Ancient Treasures**

Morning (9:00–12:00)
• **The Egyptian Museum** — 2 hours — Arrive early to enjoy Tutankhamun's treasures with minimal crowding. Don't forget to purchase tickets beforehand to bypass the main entrance ticket lines. 
  - 📍 Address: El-Tahrir Square, Cairo
  - 💰 Entry Fee: 200 EGP (approx. $6.50)
  - ![The Egyptian Museum](***REMOVED***/storage/v1/object/public/poi-images/pois/the-egyptian-museum-0-1781614373.jpg)

Lunch
• **Local Café near Tahrir Square** — Enjoy a traditional Egyptian meal, try koshari or falafel.

Afternoon (13:00–17:00)
• **National Museum of Egyptian Civilization (NMEC)** — 2-3 hours — Visit the Royal Mummies Hall immediately upon entry to avoid afternoon crowds. Allocate extra time for the textile exh
```

**Retrieved context (for groundedness check):** SourceRef(label="Tentmakers' Street", kind='database'); SourceRef(label='Ben Ezra Synagogue', kind='database'); SourceRef(label='The Egyptian Museum', kind='database'); SourceRef(label='Bab al-Futuh', kind='database'); SourceRef(label='National Museum of Egyptian Civilization (NMEC)', kind='database

**Your groundedness score:** 0.5 (0 / 0.5 / 1)

### 14. [itinerary] LLM-judge: 1.0
**Query:** Plan a photographer's dream Egypt itinerary.

**CLEO response:**
```
It looks like I didn't find specific photography-focused attractions in my search, but I can absolutely help you craft a photographer's dream itinerary in Egypt based on some of the most visually stunning locations and experiences! Here’s a suggested itinerary that highlights Egypt's breathtaking landscapes, historical sites, and vibrant culture.

---

### **Photographer's Dream Egypt Itinerary**

**Day 1 — Cairo: Urban and Ancient Wonders**
- **Morning:** Start at the **Egyptian Museum**, where you can capture the intricate details of ancient artifacts, including the treasures of Tutankhamun. 
- **Afternoon:** Head to **Islamic Cairo**, particularly the **Khan El Khalili Bazaar**. The bustling market is perfect for street photography, showcasing local life and craftsmanship.
- **Evening:*
```

**Retrieved context (for groundedness check):** SourceRef(label='VOYO verified database', kind='database')

**Your groundedness score:** 0.7 (0 / 0.5 / 1)

### 15. [itinerary] LLM-judge: 0.9
**Query:** I have 2 days in Luxor. What should I do?

**CLEO response:**
```
**Day 1 — The Wonders of Ancient Egypt**

**Morning (9:00–12:00)**
• **Valley of the Kings** — 3 hours — Start your day early to explore the tombs of ancient pharaohs, including Tutankhamun's tomb. Arrive at opening time to avoid crowds and the midday heat. 
  - 📍 Address: Valley of the Kings, Luxor
  - 💰 Entry Fee: 300 EGP (approx. $9.75)
  - ![Valley of the Kings](https://upload.wikimedia.org/wikipedia/commons/thumb/b/b1/Vall%C3%A9e_des_rois_%28Vall%C3%A9e_des_reines%29_%2840077562673%29.jpg/800px-Vall%C3%A9e_des_rois_%28Vall%C3%A9e_des_reines%29_%2840077562673%29.jpg)

**Lunch**
• **Local Eatery in the West Bank** — Enjoy traditional Egyptian dishes like grilled chicken or kofta.

**Afternoon (13:00–17:00)**
• **Deir el-Medina** — 2 hours — After lunch, visit this ancient village of art
```

**Retrieved context (for groundedness check):** SourceRef(label='Luxor Corniche', kind='database'); SourceRef(label='Deir el-Medina', kind='database'); SourceRef(label='West Bank Bicycle Tour', kind='database'); SourceRef(label='Temple of Khnum at Esna', kind='database'); SourceRef(label='Luxor Museum', kind='database')

**Your groundedness score:** 0.9 (0 / 0.5 / 1)

### 16. [itinerary] LLM-judge: 1.0
**Query:** What can I see in Aswan in 2 days?

**CLEO response:**
```
Here's a fantastic 2-day itinerary for exploring Aswan, packed with historical sites, local culture, and unforgettable experiences!

---

**Day 1 — Ancient Temples and Local Markets**

**Morning (9:00–12:00)**
• **Temple of Dakka** — 2 hours — This Greco-Roman temple dedicated to Thoth is a must-visit. It's been beautifully relocated near Wadi es-Sebua. Enjoy a boat trip on Lake Nasser to reach it, and be sure to examine the intricate high-relief decorations on the pylon! **Ticket price: 100 EGP**.  
![Temple of Dakka](***REMOVED***/storage/v1/object/public/poi-images/pois/temple-of-dakka-0.jpg)

**Lunch**
• **Local Nubian Restaurant** — Try some traditional Nubian dishes, such as grilled fish or lentil soup, while enjoying views of the Nile.

**Afternoon (13:00–
```

**Retrieved context (for groundedness check):** SourceRef(label='Temple of Dakka', kind='database'); SourceRef(label='Aswan Souk', kind='database'); SourceRef(label='Qasr Ibrim', kind='database'); SourceRef(label='El-Kab (Nekheb)', kind='database'); SourceRef(label='Rock Tombs of El-Kab', kind='database')

**Your groundedness score:** 1 (0 / 0.5 / 1)

### 17. [complex] LLM-judge: 1.0
**Query:** What's the difference between Luxor Temple and Karnak Temple?

**CLEO response:**
```
Both Luxor Temple and Karnak Temple are remarkable sites in Luxor, but they serve different historical and architectural purposes.

### Luxor Temple
- **Description:** Luxor Temple is an ancient Egyptian temple complex located on the east bank of the Nile. It is beautifully illuminated at night, creating a magical atmosphere. The temple was built primarily during the reign of Pharaoh Amenhotep III and later expanded by Ramses II.
- **Ticket Price:** 160 EGP
- **Average Rating:** 4.8/5
- **Significance:** Luxor Temple was dedicated to the rejuvenation of kingship and was a center for the annual Opet Festival, celebrating the god Amun.

### Karnak Temple
- **Description:** The Karnak Temple Complex is the largest ancient religious site in the world, built over 2000 years. It features massive
```

**Retrieved context (for groundedness check):** SourceRef(label='Luxor Temple', kind='database'); SourceRef(label='Temple of Dakka', kind='database'); SourceRef(label='Khufu Mortuary Temple', kind='database'); SourceRef(label='El-Kab (Nekheb)', kind='database'); SourceRef(label='Deir el-Medina', kind='database')

**Your groundedness score:** 0.7 (0 / 0.5 / 1)

### 18. [complex] LLM-judge: 0.9
**Query:** What's the best route for a Nile cruise between Luxor and Aswan?

**CLEO response:**
```
Ah, cruising the Nile between Luxor and Aswan is an unforgettable experience! 🌊 Here’s the best route and what to expect along the way:

### Overview of the Nile Cruise
The **Luxor to Aswan Nile Cruise** is a multi-day luxury experience that allows you to visit several fascinating temples and historical sites along the Nile. The cruise typically starts in Luxor and travels south to Aswan, providing stunning views and a comfortable way to explore ancient Egypt.

**Ticket Price:** Approximately 15,000 EGP ($150) per person  
**Best Time to Visit:** October to April (peak season; book ahead)  
**Average Rating:** 4.8/5 (26 reviews)

### Route Highlights

1. **Luxor**
   - **Karnak Temple:** A massive temple complex dedicated to the Theban triad, significant for its vast hypostyle hall and sac
```

**Retrieved context (for groundedness check):** SourceRef(label='Luxor to Aswan Nile Cruise', kind='database'); SourceRef(label='Luxor Corniche', kind='database'); SourceRef(label='Temple of Dakka', kind='database'); SourceRef(label='Qasr Ibrim', kind='database'); SourceRef(label='Great Sphinx of Giza', kind='database')

**Your groundedness score:** 0.9 (0 / 0.5 / 1)

### 19. [complex] LLM-judge: 1.0
**Query:** Compare the Pyramids of Giza with the Step Pyramid at Saqqara.

**CLEO response:**
```
The Pyramids of Giza and the Step Pyramid at Saqqara are both iconic symbols of ancient Egyptian architecture, but they represent different eras and architectural innovations.

### Pyramids of Giza
- **Historical Significance:** The Great Pyramids of Giza, built during the Fourth Dynasty (around 2580–2560 BC), are the most famous pyramids in the world. The Great Pyramid of Khufu (Cheops) is the largest and was originally 146.6 meters tall. It showcases the Egyptians' advanced engineering skills and serves as a testament to their religious beliefs about the afterlife.
- **Architecture:** The Giza pyramids are true pyramids with smooth sides, designed as monumental tombs for the pharaohs. The complex includes the Great Sphinx, which is also an iconic symbol of ancient Egypt, carved from lime
```

**Retrieved context (for groundedness check):** SourceRef(label='Tomb of Queen Hetepheres I', kind='database'); SourceRef(label='Abusir Pyramid Field', kind='database'); SourceRef(label='Great Sphinx of Giza', kind='database'); SourceRef(label='Pyramid of Unas', kind='database'); SourceRef(label='Tomb of Ti', kind='database')

**Your groundedness score:** 0.8 (0 / 0.5 / 1)

### 20. [complex] LLM-judge: 1.0
**Query:** Can I see all of Cairo's highlights in 2 days?

**CLEO response:**
```
Absolutely, you can see many of Cairo's highlights in just two days! Here’s a packed itinerary that will allow you to experience the essence of this vibrant city.

---

**Day 1 — Ancient Wonders & Cultural Treasures**

Morning (9:00–12:00)
• **The Egyptian Museum** — 2–3 hours — Start your day with the world’s largest collection of ancient Egyptian antiquities, including the treasures of Tutankhamun. Pro tip: Hire a guide to get the full story behind the exhibits!

Lunch
• **Local Restaurant near the Museum** — Try some traditional Egyptian fare like koshari or falafel.

Afternoon (13:00–17:00)
• **National Museum of Egyptian Civilization (NMEC)** — 2–3 hours — Explore this modern museum that houses the Royal Mummies Hall and over 50,000 artifacts tracing the history of Egyptian civilizati
```

**Retrieved context (for groundedness check):** SourceRef(label="Tentmakers' Street", kind='database'); SourceRef(label='Ben Ezra Synagogue', kind='database'); SourceRef(label='The Egyptian Museum', kind='database'); SourceRef(label='Bab al-Futuh', kind='database'); SourceRef(label='National Museum of Egyptian Civilization (NMEC)', kind='database

**Your groundedness score:** 0.8 (0 / 0.5 / 1)
