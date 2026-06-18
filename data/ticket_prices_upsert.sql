-- data/ticket_prices_upsert.sql
-- Idempotent upsert of ticket_prices JSONB for POIs matched to egymonuments.gov.eg
-- Gate: (real POI match) AND (prices.json matched=true) AND (egyptian_adult & foreigner_adult both non-null ints).
-- Guard: WHERE ticket_prices IS NULL  -> NEVER overwrites an existing value. Re-runnable.
-- Matching key: pois.name (exact canonical POI name as stored; the DB has no slug).
-- Student prices are recorded ONLY in these SQL comments (the CHECK constraint
-- in config/sql/004_ticket_prices.sql forbids extra JSONB keys).
-- JSONB shape enforced by constraint: {"egyptian":N,"foreigner":N,"currency":"EGP"}.
BEGIN;

UPDATE pois SET ticket_prices = '{"egyptian":60,"foreigner":220,"currency":"EGP"}' WHERE name = 'Manial Palace Museum' AND ticket_prices IS NULL;  -- student: egyptian=20, foreigner=110
UPDATE pois SET ticket_prices = '{"egyptian":60,"foreigner":220,"currency":"EGP"}' WHERE name = 'Baron Empain Palace' AND ticket_prices IS NULL;  -- student: egyptian=30, foreigner=110
UPDATE pois SET ticket_prices = '{"egyptian":10,"foreigner":100,"currency":"EGP"}' WHERE name = 'Gayer-Anderson Museum' AND ticket_prices IS NULL;  -- student: egyptian=5, foreigner=50
UPDATE pois SET ticket_prices = '{"egyptian":30,"foreigner":550,"currency":"EGP"}' WHERE name = 'The Egyptian Museum' AND ticket_prices IS NULL;  -- student: egyptian=10, foreigner=275
UPDATE pois SET ticket_prices = '{"egyptian":0,"foreigner":220,"currency":"EGP"}' WHERE name = 'Mosque of Sultan Hassan' AND ticket_prices IS NULL;  -- student: egyptian=0, foreigner=110
UPDATE pois SET ticket_prices = '{"egyptian":0,"foreigner":220,"currency":"EGP"}' WHERE name = 'Al-Rifa''i Mosque' AND ticket_prices IS NULL;  -- student: egyptian=0, foreigner=110
UPDATE pois SET ticket_prices = '{"egyptian":90,"foreigner":550,"currency":"EGP"}' WHERE name = 'National Museum of Egyptian Civilization (NMEC)' AND ticket_prices IS NULL;  -- student: egyptian=45, foreigner=300
UPDATE pois SET ticket_prices = '{"egyptian":30,"foreigner":300,"currency":"EGP"}' WHERE name = 'Royal Carriages Museum' AND ticket_prices IS NULL;  -- student: egyptian=10, foreigner=150
UPDATE pois SET ticket_prices = '{"egyptian":20,"foreigner":220,"currency":"EGP"}' WHERE name = 'Qalawun Complex' AND ticket_prices IS NULL;  -- student: egyptian=10, foreigner=110
UPDATE pois SET ticket_prices = '{"egyptian":20,"foreigner":220,"currency":"EGP"}' WHERE name = 'Sultan Barquq Complex' AND ticket_prices IS NULL;  -- student: egyptian=10, foreigner=110
UPDATE pois SET ticket_prices = '{"egyptian":10,"foreigner":100,"currency":"EGP"}' WHERE name = 'Wekalet El Ghouri' AND ticket_prices IS NULL;  -- student: egyptian=5, foreigner=50
UPDATE pois SET ticket_prices = '{"egyptian":10,"foreigner":150,"currency":"EGP"}' WHERE name = 'Al-Ghuri Complex' AND ticket_prices IS NULL;  -- student: egyptian=5, foreigner=75
UPDATE pois SET ticket_prices = '{"egyptian":20,"foreigner":220,"currency":"EGP"}' WHERE name = 'Al-Mu''izz Street' AND ticket_prices IS NULL;  -- student: egyptian=10, foreigner=110
UPDATE pois SET ticket_prices = '{"egyptian":60,"foreigner":550,"currency":"EGP"}' WHERE name = 'Citadel of Cairo (Saladin Citadel)' AND ticket_prices IS NULL;  -- student: egyptian=30, foreigner=275
UPDATE pois SET ticket_prices = '{"egyptian":10,"foreigner":100,"currency":"EGP"}' WHERE name = 'Bab Zuweila' AND ticket_prices IS NULL;  -- student: egyptian=5, foreigner=50
UPDATE pois SET ticket_prices = '{"egyptian":20,"foreigner":120,"currency":"EGP"}' WHERE name = 'Nilometer (Rhoda Island)' AND ticket_prices IS NULL;  -- student: egyptian=10, foreigner=60
UPDATE pois SET ticket_prices = '{"egyptian":20,"foreigner":280,"currency":"EGP"}' WHERE name = 'Coptic Museum' AND ticket_prices IS NULL;  -- student: egyptian=10, foreigner=140
UPDATE pois SET ticket_prices = '{"egyptian":20,"foreigner":340,"currency":"EGP"}' WHERE name = 'Museum of Islamic Art' AND ticket_prices IS NULL;  -- student: egyptian=10, foreigner=170
UPDATE pois SET ticket_prices = '{"egyptian":60,"foreigner":700,"currency":"EGP"}' WHERE name = 'Giza Plateau' AND ticket_prices IS NULL;  -- student: egyptian=30, foreigner=350
UPDATE pois SET ticket_prices = '{"egyptian":100,"foreigner":1000,"currency":"EGP"}' WHERE name = 'Great Pyramid of Giza (Khufu)' AND ticket_prices IS NULL;  -- student: egyptian=50, foreigner=500
UPDATE pois SET ticket_prices = '{"egyptian":30,"foreigner":280,"currency":"EGP"}' WHERE name = 'Pyramid of Menkaure' AND ticket_prices IS NULL;  -- student: egyptian=10, foreigner=140
UPDATE pois SET ticket_prices = '{"egyptian":30,"foreigner":600,"currency":"EGP"}' WHERE name = 'Saqqara (Step Pyramid)' AND ticket_prices IS NULL;  -- student: egyptian=10, foreigner=300
UPDATE pois SET ticket_prices = '{"egyptian":10,"foreigner":200,"currency":"EGP"}' WHERE name = 'Dahshur Pyramids' AND ticket_prices IS NULL;  -- student: egyptian=5, foreigner=100
UPDATE pois SET ticket_prices = '{"egyptian":40,"foreigner":150,"currency":"EGP"}' WHERE name = 'Djoser Funerary Complex' AND ticket_prices IS NULL;  -- student: egyptian=20, foreigner=75
UPDATE pois SET ticket_prices = '{"egyptian":20,"foreigner":180,"currency":"EGP"}' WHERE name = 'Serapeum of Saqqara' AND ticket_prices IS NULL;  -- student: egyptian=5, foreigner=90
UPDATE pois SET ticket_prices = '{"egyptian":20,"foreigner":100,"currency":"EGP"}' WHERE name = 'Mastaba of Mereruka' AND ticket_prices IS NULL;  -- student: egyptian=5, foreigner=50
UPDATE pois SET ticket_prices = '{"egyptian":30,"foreigner":600,"currency":"EGP"}' WHERE name = 'Imhotep Museum' AND ticket_prices IS NULL;  -- student: egyptian=10, foreigner=300
UPDATE pois SET ticket_prices = '{"egyptian":20,"foreigner":200,"currency":"EGP"}' WHERE name = 'Tomb of Meresankh III' AND ticket_prices IS NULL;  -- student: egyptian=5, foreigner=100
UPDATE pois SET ticket_prices = '{"egyptian":40,"foreigner":500,"currency":"EGP"}' WHERE name = 'Luxor Temple' AND ticket_prices IS NULL;  -- student: egyptian=20, foreigner=250
UPDATE pois SET ticket_prices = '{"egyptian":40,"foreigner":600,"currency":"EGP"}' WHERE name = 'Karnak Temple Complex' AND ticket_prices IS NULL;  -- student: egyptian=20, foreigner=300
UPDATE pois SET ticket_prices = '{"egyptian":60,"foreigner":750,"currency":"EGP"}' WHERE name = 'Valley of the Kings' AND ticket_prices IS NULL;  -- student: egyptian=30, foreigner=375
UPDATE pois SET ticket_prices = '{"egyptian":40,"foreigner":440,"currency":"EGP"}' WHERE name = 'Temple of Hatshepsut (Deir el-Bahari)' AND ticket_prices IS NULL;  -- student: egyptian=20, foreigner=220
UPDATE pois SET ticket_prices = '{"egyptian":500,"foreigner":2000,"currency":"EGP"}' WHERE name = 'Tomb of Seti I (KV17)' AND ticket_prices IS NULL;  -- student: egyptian=250, foreigner=2000
UPDATE pois SET ticket_prices = '{"egyptian":40,"foreigner":700,"currency":"EGP"}' WHERE name = 'Tomb of Tutankhamun (KV62)' AND ticket_prices IS NULL;  -- student: egyptian=20, foreigner=350
UPDATE pois SET ticket_prices = '{"egyptian":30,"foreigner":220,"currency":"EGP"}' WHERE name = 'Tomb of Ramesses VI (KV9)' AND ticket_prices IS NULL;  -- student: egyptian=10, foreigner=110
UPDATE pois SET ticket_prices = '{"egyptian":20,"foreigner":230,"currency":"EGP"}' WHERE name = 'Medinet Habu (Mortuary Temple of Ramesses III)' AND ticket_prices IS NULL;  -- student: egyptian=10, foreigner=110
UPDATE pois SET ticket_prices = '{"egyptian":20,"foreigner":220,"currency":"EGP"}' WHERE name = 'Ramesseum (Mortuary Temple of Ramesses II)' AND ticket_prices IS NULL;  -- student: egyptian=10, foreigner=110
UPDATE pois SET ticket_prices = '{"egyptian":20,"foreigner":220,"currency":"EGP"}' WHERE name = 'Mummification Museum' AND ticket_prices IS NULL;  -- student: egyptian=5, foreigner=110
UPDATE pois SET ticket_prices = '{"egyptian":20,"foreigner":300,"currency":"EGP"}' WHERE name = 'Dendera Temple Complex (Temple of Hathor)' AND ticket_prices IS NULL;  -- student: egyptian=10, foreigner=150
UPDATE pois SET ticket_prices = '{"egyptian":20,"foreigner":300,"currency":"EGP"}' WHERE name = 'Temple of Hathor at Dendera' AND ticket_prices IS NULL;  -- student: egyptian=10, foreigner=150
UPDATE pois SET ticket_prices = '{"egyptian":30,"foreigner":750,"currency":"EGP"}' WHERE name = 'Abu Simbel Temples' AND ticket_prices IS NULL;  -- student: egyptian=10, foreigner=375
UPDATE pois SET ticket_prices = '{"egyptian":40,"foreigner":550,"currency":"EGP"}' WHERE name = 'Philae Temple (Temple of Isis)' AND ticket_prices IS NULL;  -- student: egyptian=20, foreigner=275
UPDATE pois SET ticket_prices = '{"egyptian":40,"foreigner":450,"currency":"EGP"}' WHERE name = 'Temple of Kom Ombo' AND ticket_prices IS NULL;  -- student: egyptian=20, foreigner=225
UPDATE pois SET ticket_prices = '{"egyptian":40,"foreigner":450,"currency":"EGP"}' WHERE name = 'Crocodile Museum (Kom Ombo)' AND ticket_prices IS NULL;  -- student: egyptian=20, foreigner=225
UPDATE pois SET ticket_prices = '{"egyptian":30,"foreigner":400,"currency":"EGP"}' WHERE name = 'Nubia Museum' AND ticket_prices IS NULL;  -- student: egyptian=10, foreigner=200
UPDATE pois SET ticket_prices = '{"egyptian":10,"foreigner":200,"currency":"EGP"}' WHERE name = 'Temple of Kalabsha' AND ticket_prices IS NULL;  -- student: egyptian=5, foreigner=100
UPDATE pois SET ticket_prices = '{"egyptian":20,"foreigner":220,"currency":"EGP"}' WHERE name = 'Unfinished Obelisk' AND ticket_prices IS NULL;  -- student: egyptian=10, foreigner=110
UPDATE pois SET ticket_prices = '{"egyptian":10,"foreigner":100,"currency":"EGP"}' WHERE name = 'Temple of Amada' AND ticket_prices IS NULL;  -- student: egyptian=5, foreigner=50
UPDATE pois SET ticket_prices = '{"egyptian":40,"foreigner":550,"currency":"EGP"}' WHERE name = 'Temple of Horus at Edfu' AND ticket_prices IS NULL;  -- student: egyptian=20, foreigner=275
UPDATE pois SET ticket_prices = '{"egyptian":10,"foreigner":100,"currency":"EGP"}' WHERE name = 'Sehel Island' AND ticket_prices IS NULL;  -- student: egyptian=5, foreigner=50
UPDATE pois SET ticket_prices = '{"egyptian":10,"foreigner":150,"currency":"EGP"}' WHERE name = 'Temple of Wadi es-Sebua' AND ticket_prices IS NULL;  -- student: egyptian=5, foreigner=75
UPDATE pois SET ticket_prices = '{"egyptian":10,"foreigner":70,"currency":"EGP"}' WHERE name = 'Temple of Derr' AND ticket_prices IS NULL;  -- student: egyptian=5, foreigner=35
UPDATE pois SET ticket_prices = '{"egyptian":10,"foreigner":150,"currency":"EGP"}' WHERE name = 'Monastery of St. Simeon' AND ticket_prices IS NULL;  -- student: egyptian=5, foreigner=50
UPDATE pois SET ticket_prices = '{"egyptian":20,"foreigner":200,"currency":"EGP"}' WHERE name = 'Elephantine Island' AND ticket_prices IS NULL;  -- student: egyptian=10, foreigner=100
UPDATE pois SET ticket_prices = '{"egyptian":60,"foreigner":200,"currency":"EGP"}' WHERE name = 'Citadel of Qaitbay' AND ticket_prices IS NULL;  -- student: egyptian=30, foreigner=100
UPDATE pois SET ticket_prices = '{"egyptian":20,"foreigner":220,"currency":"EGP"}' WHERE name = 'Alexandria National Museum' AND ticket_prices IS NULL;  -- student: egyptian=5, foreigner=110
UPDATE pois SET ticket_prices = '{"egyptian":30,"foreigner":220,"currency":"EGP"}' WHERE name = 'Royal Jewelry Museum' AND ticket_prices IS NULL;  -- student: egyptian=10, foreigner=110
UPDATE pois SET ticket_prices = '{"egyptian":40,"foreigner":400,"currency":"EGP"}' WHERE name = 'Greco-Roman Museum' AND ticket_prices IS NULL;  -- student: egyptian=20, foreigner=200

COMMIT;
