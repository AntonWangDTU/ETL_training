-- Module 01: Solutions

-- 1a. All strains
SELECT * FROM strains;

-- 1b. Nitrogen-fixing strains
SELECT strain_code, species FROM strains WHERE nitrogen_fixing = 1;

-- 1c. Sites in Kenya
SELECT * FROM sites WHERE country = 'Kenya';

-- 2a. Wheat experiments
SELECT * FROM experiments WHERE crop = 'wheat';

-- 2b. Control experiments
SELECT * FROM experiments WHERE treatment = 'control';

-- 2c. Final harvest measurements sorted by yield
SELECT * FROM measurements
WHERE yield_kg_per_ha IS NOT NULL
ORDER BY yield_kg_per_ha DESC;

-- 3a. Total experiments
SELECT COUNT(*) AS total_experiments FROM experiments;

-- 3b. Experiments per treatment type
SELECT treatment, COUNT(*) AS count
FROM experiments
GROUP BY treatment;

-- 3c. Average yield
SELECT ROUND(AVG(yield_kg_per_ha), 1) AS avg_yield_kg_per_ha
FROM measurements
WHERE yield_kg_per_ha IS NOT NULL;

-- 4a. Experiments with site country and strain species (LEFT JOIN so controls appear)
SELECT
    e.experiment_id,
    e.crop,
    e.treatment,
    s.country,
    st.species
FROM experiments e
JOIN  sites   s  ON e.site_id    = s.id
LEFT JOIN strains st ON e.strain_id  = st.id;

-- 4b. Final measurements with context
SELECT
    e.experiment_id,
    e.crop,
    e.treatment,
    si.country,
    COALESCE(st.strain_code, 'control') AS strain_code,
    m.yield_kg_per_ha
FROM measurements m
JOIN experiments e  ON m.experiment_id = e.id
JOIN sites       si ON e.site_id       = si.id
LEFT JOIN strains st ON e.strain_id    = st.id
WHERE m.yield_kg_per_ha IS NOT NULL
ORDER BY m.yield_kg_per_ha DESC;

-- 4c. Experiments per researcher
SELECT
    r.name,
    r.institution,
    COUNT(e.id) AS experiment_count
FROM researchers r
LEFT JOIN experiments e ON r.id = e.researcher_id
GROUP BY r.id, r.name
ORDER BY experiment_count DESC;

-- 5a. Average yield per crop
SELECT
    e.crop,
    ROUND(AVG(m.yield_kg_per_ha), 1) AS avg_yield
FROM measurements m
JOIN experiments e ON m.experiment_id = e.id
WHERE m.yield_kg_per_ha IS NOT NULL
GROUP BY e.crop
ORDER BY avg_yield DESC;

-- 5b. Countries with more than 2 sites
SELECT country, COUNT(*) AS site_count
FROM sites
GROUP BY country
HAVING COUNT(*) > 2;

-- 5c. Strains used in more than 1 experiment
SELECT
    st.strain_code,
    st.species,
    COUNT(e.id) AS experiment_count
FROM strains st
JOIN experiments e ON st.id = e.strain_id
GROUP BY st.id
HAVING COUNT(e.id) > 1;
