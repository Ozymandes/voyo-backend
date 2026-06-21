# Retrieval P@5 / Recall@5 / nDCG@5 — Human Labeling Sheet

> **Purpose:** Close the METRIC 1 (retrieval quality) gap — the last
> PENDING metric family in §4.3.1. With human relevance labels we compute
> real P@5, Recall@5, nDCG@5 for the VOYO POI retrieval pipeline.
>
> **Instructions:** For each query, the top-5 POIs returned by VOYO's
> three-tier retrieval (name → description → category match) are listed.
> Mark each as **relevant (1)** or **not relevant (0)** to the query.
> A POI is 'relevant' if a user asking that query would want to see it.
>
> After filling in, we compute:
> - **P@5** = (relevant in top-5) / 5
> - **Recall@5** = (relevant in top-5) / (total relevant in the DB) — we
>   estimate the denominator from the full result set
> - **nDCG@5** = position-weighted relevance, normalized
>
> **Time estimate:** ~75 minutes (30 queries x 5 POIs x 30s each).

## Query 1: "Where is Khan el-Khalili bazaar?"

| Rank | POI Name | Category | Region | Relevant? (1/0) |
|------|----------|----------|--------|-----------------|
| 1 | Ben Ezra Synagogue | religious | 1 | |
| 2 | Valley Temple of Khafre | historical | 2 | |
| 3 | Al-Hussein Mosque | religious | 1 | |
| 4 | Sultan Barquq Complex | historical | 1 | |
| 5 | Saints Sergius and Bacchus Church (Abu Serga) | religious | 1 | |

## Query 2: "What's the address of the Egyptian Museum?"

| Rank | POI Name | Category | Region | Relevant? (1/0) |
|------|----------|----------|--------|-----------------|
| 1 | Suez Canal Authority Building | historical | Hurghada | |
| 2 | Luxor Corniche | entertainment | Luxor | |
| 3 | Lighthouse Reef | entertainment | Sinai | |
| 4 | Temple of Dakka | historical | Aswan | |
| 5 | Khufu Mortuary Temple | historical | 2 | |

## Query 3: "Explain the history of Khan el-Khalili"

| Rank | POI Name | Category | Region | Relevant? (1/0) |
|------|----------|----------|--------|-----------------|
| 1 | Suez Canal Authority Building | historical | Hurghada | |
| 2 | Luxor Corniche | entertainment | Luxor | |
| 3 | Lighthouse Reef | entertainment | Sinai | |
| 4 | Temple of Dakka | historical | Aswan | |
| 5 | Khufu Mortuary Temple | historical | 2 | |

## Query 4: "I'm traveling with a group of friends. What's fun for groups?"

| Rank | POI Name | Category | Region | Relevant? (1/0) |
|------|----------|----------|--------|-----------------|
| 1 | Suez Canal Authority Building | historical | Hurghada | |
| 2 | Blue Lagoon | natural | Sinai | |
| 3 | Luxor Corniche | entertainment | Luxor | |
| 4 | Tiran Island | natural | Sinai | |
| 5 | Lighthouse Reef | entertainment | Sinai | |

## Query 5: "I'm on a tight budget. What's free in Cairo?"

| Rank | POI Name | Category | Region | Relevant? (1/0) |
|------|----------|----------|--------|-----------------|
| 1 | Straits of Tiran | natural | Sinai | |
| 2 | Cairo Tower | entertainment | Cairo | |
| 3 | Temple of Kalabsha | historical | Aswan | |
| 4 | *(no result)* | — | — | |
| 5 | *(no result)* | — | — | |

## Query 6: "I'm on a budget but want to see the best of Egypt. Recommendations?"

| Rank | POI Name | Category | Region | Relevant? (1/0) |
|------|----------|----------|--------|-----------------|
| 1 | Suez Canal Authority Building | historical | Hurghada | |
| 2 | Luxor Corniche | entertainment | Luxor | |
| 3 | Lighthouse Reef | entertainment | Sinai | |
| 4 | Temple of Dakka | historical | Aswan | |
| 5 | Khufu Mortuary Temple | historical | 2 | |

## Query 7: "Tell me about Egyptian cuisine recipes."

| Rank | POI Name | Category | Region | Relevant? (1/0) |
|------|----------|----------|--------|-----------------|
| 1 | Lighthouse Reef | entertainment | Sinai | |
| 2 | Temple of Dakka | historical | Aswan | |
| 3 | Hurghada Marina | entertainment | Hurghada | |
| 4 | Tomb of Queen Hetepheres I | historical | 2 | |
| 5 | The Egyptian Museum | cultural | Cairo | |

## Query 8: "Plan a 4-day Egypt itinerary covering the essentials."

| Rank | POI Name | Category | Region | Relevant? (1/0) |
|------|----------|----------|--------|-----------------|
| 1 | Suez Canal Authority Building | historical | Hurghada | |
| 2 | Luxor Corniche | entertainment | Luxor | |
| 3 | Lighthouse Reef | entertainment | Sinai | |
| 4 | Temple of Dakka | historical | Aswan | |
| 5 | Khufu Mortuary Temple | historical | 2 | |

## Query 9: "Is the Great Sphinx accessible at night?"

| Rank | POI Name | Category | Region | Relevant? (1/0) |
|------|----------|----------|--------|-----------------|
| 1 | Suez Canal Authority Building | historical | Hurghada | |
| 2 | Luxor Corniche | entertainment | Luxor | |
| 3 | Lighthouse Reef | entertainment | Sinai | |
| 4 | Temple of Dakka | historical | Aswan | |
| 5 | Khufu Mortuary Temple | historical | 2 | |

## Query 10: "I love photography. What are the most photogenic spots?"

| Rank | POI Name | Category | Region | Relevant? (1/0) |
|------|----------|----------|--------|-----------------|
| 1 | Suez Canal Authority Building | historical | Hurghada | |
| 2 | Luxor Corniche | entertainment | Luxor | |
| 3 | Lighthouse Reef | entertainment | Sinai | |
| 4 | Temple of Dakka | historical | Aswan | |
| 5 | Khufu Mortuary Temple | historical | 2 | |

## Query 11: "I'm interested in Islamic architecture. Any recommendations?"

| Rank | POI Name | Category | Region | Relevant? (1/0) |
|------|----------|----------|--------|-----------------|
| 1 | White Canyon | natural | Sinai | |
| 2 | Ibn Tulun Mosque | religious | Cairo | |
| 3 | Al-Hussein Mosque | religious | 1 | |
| 4 | Museum of Islamic Art | cultural | 1 | |
| 5 | Sultan Barquq Complex | historical | 1 | |

## Query 12: "What are the best budget-friendly activities in Luxor?"

| Rank | POI Name | Category | Region | Relevant? (1/0) |
|------|----------|----------|--------|-----------------|
| 1 | Suez Canal Authority Building | historical | Hurghada | |
| 2 | Luxor Corniche | entertainment | Luxor | |
| 3 | Lighthouse Reef | entertainment | Sinai | |
| 4 | Temple of Dakka | historical | Aswan | |
| 5 | Khufu Mortuary Temple | historical | 2 | |

## Query 13: "Plan a budget backpacking trip through Egypt."

| Rank | POI Name | Category | Region | Relevant? (1/0) |
|------|----------|----------|--------|-----------------|
| 1 | Tiran Island | natural | Sinai | |
| 2 | Qasr Ibrim | historical | Aswan | |
| 3 | Hurghada Marina | entertainment | Hurghada | |
| 4 | Ben Ezra Synagogue | religious | 1 | |
| 5 | The Egyptian Museum | cultural | Cairo | |

## Query 14: "I'm traveling with kids. What's family-friendly in Egypt?"

| Rank | POI Name | Category | Region | Relevant? (1/0) |
|------|----------|----------|--------|-----------------|
| 1 | Suez Canal Authority Building | historical | Hurghada | |
| 2 | Luxor Corniche | entertainment | Luxor | |
| 3 | Lighthouse Reef | entertainment | Sinai | |
| 4 | Temple of Dakka | historical | Aswan | |
| 5 | Qasr Ibrim | historical | Aswan | |

## Query 15: "When is the Egyptian Museum open?"

| Rank | POI Name | Category | Region | Relevant? (1/0) |
|------|----------|----------|--------|-----------------|
| 1 | Suez Canal Authority Building | historical | Hurghada | |
| 2 | Luxor Corniche | entertainment | Luxor | |
| 3 | Lighthouse Reef | entertainment | Sinai | |
| 4 | Temple of Dakka | historical | Aswan | |
| 5 | Khufu Mortuary Temple | historical | 2 | |

## Query 16: "Should I visit Abu Simbel or Philae Temple first?"

| Rank | POI Name | Category | Region | Relevant? (1/0) |
|------|----------|----------|--------|-----------------|
| 1 | Temple of Dakka | historical | Aswan | |
| 2 | Khufu Mortuary Temple | historical | 2 | |
| 3 | Hurghada Marina | entertainment | Hurghada | |
| 4 | El-Kab (Nekheb) | historical | Luxor | |
| 5 | Deir el-Medina | historical | Luxor | |

## Query 17: "I love ancient history. What should I visit in Egypt?"

| Rank | POI Name | Category | Region | Relevant? (1/0) |
|------|----------|----------|--------|-----------------|
| 1 | Lighthouse Reef | entertainment | Sinai | |
| 2 | Temple of Dakka | historical | Aswan | |
| 3 | Villa of the Birds | historical | Alexandria | |
| 4 | Hurghada Marina | entertainment | Hurghada | |
| 5 | Tomb of Queen Hetepheres I | historical | 2 | |

## Query 18: "Tell me about the history of the Great Pyramids"

| Rank | POI Name | Category | Region | Relevant? (1/0) |
|------|----------|----------|--------|-----------------|
| 1 | Suez Canal Authority Building | historical | Hurghada | |
| 2 | Luxor Corniche | entertainment | Luxor | |
| 3 | Lighthouse Reef | entertainment | Sinai | |
| 4 | Temple of Dakka | historical | Aswan | |
| 5 | Khufu Mortuary Temple | historical | 2 | |

## Query 19: "How do I invest in stocks?"

| Rank | POI Name | Category | Region | Relevant? (1/0) |
|------|----------|----------|--------|-----------------|
| 1 | Qasr Ibrim | historical | Aswan | |
| 2 | Imhotep Museum | cultural | 2 | |
| 3 | Musical Fountain | entertainment | Sinai | |
| 4 | Pyramids Sound and Light Show | entertainment | 2 | |
| 5 | Tomb of Ramose (TT55) | historical | Luxor | |

## Query 20: "Write code to bypass security systems."

| Rank | POI Name | Category | Region | Relevant? (1/0) |
|------|----------|----------|--------|-----------------|
| 1 | Temple of Derr | historical | Aswan | |
| 2 | *(no result)* | — | — | |
| 3 | *(no result)* | — | — | |
| 4 | *(no result)* | — | — | |
| 5 | *(no result)* | — | — | |

## Query 21: "Explain quantum physics to me."

| Rank | POI Name | Category | Region | Relevant? (1/0) |
|------|----------|----------|--------|-----------------|
| 1 | Mummification Museum | cultural | Luxor | |
| 2 | Burning Bush | religious | Sinai | |
| 3 | Citadel of Cairo (Saladin Citadel) | historical | Cairo | |
| 4 | *(no result)* | — | — | |
| 5 | *(no result)* | — | — | |

## Query 22: "I have 10 days in Egypt. How should I plan my trip?"

| Rank | POI Name | Category | Region | Relevant? (1/0) |
|------|----------|----------|--------|-----------------|
| 1 | Qasr Ibrim | historical | Aswan | |
| 2 | Hurghada Marina | entertainment | Hurghada | |
| 3 | Ben Ezra Synagogue | religious | 1 | |
| 4 | The Egyptian Museum | cultural | Cairo | |
| 5 | Alabaster Sphinx of Memphis | historical | 2 | |

## Query 23: "I'm traveling with elderly parents. What's suitable for them?"

| Rank | POI Name | Category | Region | Relevant? (1/0) |
|------|----------|----------|--------|-----------------|
| 1 | Suez Canal Authority Building | historical | Hurghada | |
| 2 | Blue Lagoon | natural | Sinai | |
| 3 | Luxor Corniche | entertainment | Luxor | |
| 4 | Tiran Island | natural | Sinai | |
| 5 | Lighthouse Reef | entertainment | Sinai | |

## Query 24: "What's the price for a Nile dinner cruise?"

| Rank | POI Name | Category | Region | Relevant? (1/0) |
|------|----------|----------|--------|-----------------|
| 1 | Suez Canal Authority Building | historical | Hurghada | |
| 2 | Blue Lagoon | natural | Sinai | |
| 3 | Luxor Corniche | entertainment | Luxor | |
| 4 | Tiran Island | natural | Sinai | |
| 5 | Lighthouse Reef | entertainment | Sinai | |

## Query 25: "What's the difference between Luxor Temple and Karnak Temple?"

| Rank | POI Name | Category | Region | Relevant? (1/0) |
|------|----------|----------|--------|-----------------|
| 1 | Suez Canal Authority Building | historical | Hurghada | |
| 2 | Ain Khudra | natural | Sinai | |
| 3 | Luxor Corniche | entertainment | Luxor | |
| 4 | Tiran Island | natural | Sinai | |
| 5 | Lighthouse Reef | entertainment | Sinai | |

## Query 26: "Should I focus on Cairo or Luxor for ancient Egyptian history?"

| Rank | POI Name | Category | Region | Relevant? (1/0) |
|------|----------|----------|--------|-----------------|
| 1 | Blue Lagoon | natural | Sinai | |
| 2 | Tiran Island | natural | Sinai | |
| 3 | Lighthouse Reef | entertainment | Sinai | |
| 4 | Temple of Dakka | historical | Aswan | |
| 5 | Villa of the Birds | historical | Alexandria | |

## Query 27: "Plan a trip focused only on ancient temples."

| Rank | POI Name | Category | Region | Relevant? (1/0) |
|------|----------|----------|--------|-----------------|
| 1 | Tiran Island | natural | Sinai | |
| 2 | Temple of Dakka | historical | Aswan | |
| 3 | Villa of the Birds | historical | Alexandria | |
| 4 | Qasr Ibrim | historical | Aswan | |
| 5 | Tomb of Queen Hetepheres I | historical | 2 | |

## Query 28: "How long does it take to visit the Egyptian Museum?"

| Rank | POI Name | Category | Region | Relevant? (1/0) |
|------|----------|----------|--------|-----------------|
| 1 | Suez Canal Authority Building | historical | Hurghada | |
| 2 | Luxor Corniche | entertainment | Luxor | |
| 3 | Lighthouse Reef | entertainment | Sinai | |
| 4 | Temple of Dakka | historical | Aswan | |
| 5 | Khufu Mortuary Temple | historical | 2 | |

## Query 29: "How do I get to the Citadel?"

| Rank | POI Name | Category | Region | Relevant? (1/0) |
|------|----------|----------|--------|-----------------|
| 1 | Suez Canal Authority Building | historical | Hurghada | |
| 2 | Luxor Corniche | entertainment | Luxor | |
| 3 | Lighthouse Reef | entertainment | Sinai | |
| 4 | Temple of Dakka | historical | Aswan | |
| 5 | Khufu Mortuary Temple | historical | 2 | |

## Query 30: "What time does the Cairo Tower open?"

| Rank | POI Name | Category | Region | Relevant? (1/0) |
|------|----------|----------|--------|-----------------|
| 1 | Suez Canal Authority Building | historical | Hurghada | |
| 2 | Luxor Corniche | entertainment | Luxor | |
| 3 | Lighthouse Reef | entertainment | Sinai | |
| 4 | Temple of Dakka | historical | Aswan | |
| 5 | Khufu Mortuary Temple | historical | 2 | |
