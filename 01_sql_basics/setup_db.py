"""
Creates ibis.db — the central IBIS research database.
Run once before starting the SQL modules:

    uv run python 01_sql_basics/setup_db.py
"""
import sqlite3

conn = sqlite3.connect("ibis.db")
cur = conn.cursor()

cur.executescript("""
DROP TABLE IF EXISTS measurements;
DROP TABLE IF EXISTS experiments;
DROP TABLE IF EXISTS researchers;
DROP TABLE IF EXISTS sites;
DROP TABLE IF EXISTS strains;

-- Bacterial strains being evaluated as biofertilizers
CREATE TABLE strains (
    id               INTEGER PRIMARY KEY,
    strain_code      TEXT UNIQUE NOT NULL,   -- e.g. 'IBIS-001'
    species          TEXT NOT NULL,
    isolation_source TEXT,                   -- where the strain was originally isolated
    origin_country   TEXT,
    nitrogen_fixing  INTEGER NOT NULL        -- 1 = yes, 0 = no
);

-- Field trial locations
CREATE TABLE sites (
    id           INTEGER PRIMARY KEY,
    site_code    TEXT UNIQUE NOT NULL,
    country      TEXT NOT NULL,
    region       TEXT,
    soil_type    TEXT,
    climate_zone TEXT    -- e.g. 'tropical', 'semi-arid', 'temperate'
);

-- Collaborating researchers
CREATE TABLE researchers (
    id          INTEGER PRIMARY KEY,
    name        TEXT NOT NULL,
    institution TEXT,
    country     TEXT,
    email       TEXT UNIQUE
);

-- One experiment = one strain applied at one site by one researcher
-- 'control' experiments have strain_id = NULL (no inoculant applied)
CREATE TABLE experiments (
    id            INTEGER PRIMARY KEY,
    experiment_id TEXT UNIQUE NOT NULL,   -- e.g. 'KE-2024-001'
    site_id       INTEGER REFERENCES sites(id),
    strain_id     INTEGER REFERENCES strains(id),  -- NULL = control
    researcher_id INTEGER REFERENCES researchers(id),
    crop          TEXT NOT NULL,
    treatment     TEXT NOT NULL,   -- 'inoculated', 'control', 'chemical_fertilizer'
    start_date    TEXT,
    end_date      TEXT
);

-- Measurements recorded during an experiment
CREATE TABLE measurements (
    id            INTEGER PRIMARY KEY,
    experiment_id INTEGER REFERENCES experiments(id),
    measured_at   TEXT,
    plant_height_cm    REAL,
    chlorophyll_spad   REAL,   -- leaf greenness (SPAD units, roughly 0-80)
    shoot_dw_g         REAL,   -- shoot dry weight in grams
    root_dw_g          REAL,   -- root dry weight in grams
    yield_kg_per_ha    REAL,   -- grain/fruit yield
    notes              TEXT
);
""")

strains = [
    (1, "IBIS-001", "Rhizobium leguminosarum",   "root nodule",       "DK", 1),
    (2, "IBIS-002", "Azospirillum brasilense",    "wheat rhizosphere", "BR", 1),
    (3, "IBIS-003", "Pseudomonas fluorescens",    "maize rhizosphere", "IN", 0),
    (4, "IBIS-004", "Bacillus subtilis",          "soil",              "KE", 0),
    (5, "IBIS-005", "Rhizobium tropici",          "bean nodule",       "BR", 1),
    (6, "IBIS-006", "Gluconacetobacter diazotro", "sugarcane",         "BR", 1),
]

sites = [
    (1, "KE-KISUMU",  "Kenya",   "Kisumu",       "clay loam",  "tropical"),
    (2, "KE-NAKURU",  "Kenya",   "Nakuru",       "loam",       "semi-arid"),
    (3, "IN-PUNE",    "India",   "Pune",         "black soil", "semi-arid"),
    (4, "IN-LUCKNOW", "India",   "Lucknow",      "alluvial",   "subtropical"),
    (5, "DK-RISO",    "Denmark", "Roskilde",     "sandy loam", "temperate"),
    (6, "BR-CAMPINAS", "Brazil", "Campinas",     "oxisol",     "tropical"),
]

researchers = [
    (1, "Amara Odhiambo", "University of Nairobi",  "Kenya",   "a.odhiambo@uon.ac.ke"),
    (2, "Priya Sharma",   "ICAR-IARI",               "India",   "p.sharma@iari.res.in"),
    (3, "Lars Eriksen",   "DTU Bioengineering",      "Denmark", "laer@dtu.dk"),
    (4, "Carlos Mendes",  "EMBRAPA",                 "Brazil",  "c.mendes@embrapa.br"),
    (5, "Fatima Hassan",  "University of Nairobi",   "Kenya",   "f.hassan@uon.ac.ke"),
]

experiments = [
    # Kenya - maize trials
    (1,  "KE-2024-001", 1, 1,    1, "maize", "inoculated",         "2024-03-01", "2024-07-01"),
    (2,  "KE-2024-002", 1, 4,    1, "maize", "inoculated",         "2024-03-01", "2024-07-01"),
    (3,  "KE-2024-003", 1, None, 1, "maize", "control",            "2024-03-01", "2024-07-01"),
    (4,  "KE-2024-004", 1, None, 5, "maize", "chemical_fertilizer","2024-03-01", "2024-07-01"),
    (5,  "KE-2024-005", 2, 1,    5, "beans", "inoculated",         "2024-03-15", "2024-07-15"),
    (6,  "KE-2024-006", 2, None, 5, "beans", "control",            "2024-03-15", "2024-07-15"),
    # India - wheat trials
    (7,  "IN-2024-001", 3, 2,    2, "wheat", "inoculated",         "2024-11-01", "2025-03-01"),
    (8,  "IN-2024-002", 3, 3,    2, "wheat", "inoculated",         "2024-11-01", "2025-03-01"),
    (9,  "IN-2024-003", 3, None, 2, "wheat", "control",            "2024-11-01", "2025-03-01"),
    (10, "IN-2024-004", 4, 2,    2, "wheat", "inoculated",         "2024-11-15", "2025-03-15"),
    # Denmark - barley trials
    (11, "DK-2024-001", 5, 1,    3, "barley","inoculated",         "2024-04-01", "2024-08-15"),
    (12, "DK-2024-002", 5, None, 3, "barley","control",            "2024-04-01", "2024-08-15"),
    # Brazil - soybean trials
    (13, "BR-2024-001", 6, 5,    4, "soybean","inoculated",        "2024-10-01", "2025-02-01"),
    (14, "BR-2024-002", 6, 6,    4, "soybean","inoculated",        "2024-10-01", "2025-02-01"),
    (15, "BR-2024-003", 6, None, 4, "soybean","control",           "2024-10-01", "2025-02-01"),
]

measurements = [
    # KE-2024-001 (inoculated IBIS-001, maize, Kisumu)
    (1,  1,  "2024-05-15", 78.2, 42.1, 18.4, 6.2,  None,    None),
    (2,  1,  "2024-07-01", 142.5,48.3, 38.7, 11.4, 4850.0,  None),
    # KE-2024-002 (inoculated IBIS-004, maize, Kisumu)
    (3,  2,  "2024-05-15", 71.0, 38.5, 15.2, 5.1,  None,    None),
    (4,  2,  "2024-07-01", 128.3,41.2, 31.5, 9.3,  3920.0,  None),
    # KE-2024-003 (control, maize, Kisumu)
    (5,  3,  "2024-05-15", 58.4, 31.2, 11.0, 3.8,  None,    None),
    (6,  3,  "2024-07-01", 108.1,34.5, 22.3, 7.1,  2780.0,  None),
    # KE-2024-004 (chemical fertilizer, maize, Kisumu)
    (7,  4,  "2024-05-15", 82.1, 44.8, 20.1, 6.8,  None,    None),
    (8,  4,  "2024-07-01", 155.0,51.2, 42.0, 12.8, 5100.0,  None),
    # KE-2024-005 (inoculated IBIS-001, beans, Nakuru)
    (9,  5,  "2024-05-20", 33.1, 39.4, 8.5,  4.2,  None,    None),
    (10, 5,  "2024-07-15", 55.8, 44.1, 19.2, 8.8,  1820.0,  None),
    # KE-2024-006 (control, beans, Nakuru)
    (11, 6,  "2024-05-20", 28.7, 33.0, 6.4,  3.1,  None,    None),
    (12, 6,  "2024-07-15", 44.2, 35.8, 13.5, 5.9,  1240.0,  None),
    # IN-2024-001 (IBIS-002, wheat, Pune)
    (13, 7,  "2025-01-15", 55.3, 40.8, 12.3, 3.9,  None,    None),
    (14, 7,  "2025-03-01", 88.4, 46.2, 24.1, 7.2,  3650.0,  None),
    # IN-2024-002 (IBIS-003, wheat, Pune)
    (15, 8,  "2025-01-15", 52.1, 38.1, 11.5, 3.5,  None,    None),
    (16, 8,  "2025-03-01", 82.0, 42.5, 21.8, 6.5,  3210.0,  None),
    # IN-2024-003 (control, wheat, Pune)
    (17, 9,  "2025-01-15", 44.8, 31.5, 8.9,  2.8,  None,    None),
    (18, 9,  "2025-03-01", 71.2, 35.8, 17.4, 5.1,  2580.0,  None),
    # IN-2024-004 (IBIS-002, wheat, Lucknow)
    (19, 10, "2025-01-20", 57.8, 41.5, 13.0, 4.1,  None,    None),
    (20, 10, "2025-03-15", 91.2, 47.8, 25.5, 7.8,  3820.0,  None),
    # DK-2024-001 (IBIS-001, barley, Risø)
    (21, 11, "2024-06-01", 38.5, 43.2, 9.8,  3.2,  None,    None),
    (22, 11, "2024-08-15", 72.1, 48.5, 21.2, 6.8,  4120.0,  None),
    # DK-2024-002 (control, barley, Risø)
    (23, 12, "2024-06-01", 35.1, 39.8, 8.5,  2.9,  None,    None),
    (24, 12, "2024-08-15", 64.8, 43.1, 17.8, 5.5,  3540.0,  None),
    # BR-2024-001 (IBIS-005, soybean, Campinas)
    (25, 13, "2024-12-01", 42.3, 40.1, 14.2, 5.8,  None,    None),
    (26, 13, "2025-02-01", 88.5, 47.3, 32.5, 12.1, 3280.0,  None),
    # BR-2024-002 (IBIS-006, soybean, Campinas)
    (27, 14, "2024-12-01", 40.1, 38.8, 13.5, 5.3,  None,    None),
    (28, 14, "2025-02-01", 82.1, 44.5, 29.8, 11.2, 3050.0,  None),
    # BR-2024-003 (control, soybean, Campinas)
    (29, 15, "2024-12-01", 35.8, 33.2, 10.8, 4.2,  None,    None),
    (30, 15, "2025-02-01", 68.4, 38.9, 22.1, 8.5,  2410.0,  None),
]

cur.executemany("INSERT INTO strains VALUES (?,?,?,?,?,?)", strains)
cur.executemany("INSERT INTO sites VALUES (?,?,?,?,?,?)", sites)
cur.executemany("INSERT INTO researchers VALUES (?,?,?,?,?)", researchers)
cur.executemany("INSERT INTO experiments VALUES (?,?,?,?,?,?,?,?,?)", experiments)
cur.executemany("INSERT INTO measurements VALUES (?,?,?,?,?,?,?,?,?)", measurements)

conn.commit()
conn.close()
print("ibis.db created: strains, sites, researchers, experiments, measurements")
