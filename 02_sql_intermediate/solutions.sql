-- Module 02: Solutions

-- 1a. Yield improvement: inoculated vs control at same site + crop
WITH harvest AS (
    SELECT
        e.id            AS exp_id,
        e.experiment_id,
        e.site_id,
        e.crop,
        e.treatment,
        e.strain_id,
        m.yield_kg_per_ha
    FROM experiments e
    JOIN measurements m ON e.id = m.experiment_id
    WHERE m.yield_kg_per_ha IS NOT NULL
),
controls AS (
    SELECT site_id, crop, yield_kg_per_ha AS control_yield
    FROM harvest
    WHERE treatment = 'control'
)
SELECT
    si.country,
    h.crop,
    st.strain_code,
    ROUND(h.yield_kg_per_ha, 1)  AS inoculated_yield,
    ROUND(c.control_yield, 1)    AS control_yield,
    ROUND(100.0 * (h.yield_kg_per_ha - c.control_yield) / c.control_yield, 1) AS improvement_pct
FROM harvest h
JOIN controls c  ON h.site_id = c.site_id AND h.crop = c.crop
JOIN sites   si  ON h.site_id = si.id
JOIN strains st  ON h.strain_id = st.id
WHERE h.treatment = 'inoculated'
ORDER BY improvement_pct DESC;

-- 1b. Strains ranked by average yield improvement over control
WITH harvest AS (
    SELECT e.site_id, e.crop, e.treatment, e.strain_id, m.yield_kg_per_ha
    FROM experiments e
    JOIN measurements m ON e.id = m.experiment_id
    WHERE m.yield_kg_per_ha IS NOT NULL
),
controls AS (
    SELECT site_id, crop, yield_kg_per_ha AS control_yield
    FROM harvest WHERE treatment = 'control'
),
improvements AS (
    SELECT
        h.strain_id,
        100.0 * (h.yield_kg_per_ha - c.control_yield) / c.control_yield AS improvement_pct
    FROM harvest h
    JOIN controls c ON h.site_id = c.site_id AND h.crop = c.crop
    WHERE h.treatment = 'inoculated'
)
SELECT
    st.strain_code,
    st.species,
    ROUND(AVG(i.improvement_pct), 1) AS avg_improvement_pct,
    COUNT(*) AS trial_count
FROM improvements i
JOIN strains st ON i.strain_id = st.id
GROUP BY i.strain_id
ORDER BY avg_improvement_pct DESC;

-- 2a. Rank experiments by final yield within each country
SELECT
    si.country,
    e.experiment_id,
    e.crop,
    COALESCE(st.strain_code, 'control') AS strain,
    m.yield_kg_per_ha,
    RANK() OVER (PARTITION BY si.country ORDER BY m.yield_kg_per_ha DESC) AS rank_in_country
FROM measurements m
JOIN experiments e  ON m.experiment_id = e.id
JOIN sites       si ON e.site_id = si.id
LEFT JOIN strains st ON e.strain_id = st.id
WHERE m.yield_kg_per_ha IS NOT NULL;

-- 2b. Plant height growth between measurements using LAG
SELECT
    e.experiment_id,
    m.measured_at,
    m.plant_height_cm,
    LAG(m.plant_height_cm) OVER (PARTITION BY m.experiment_id ORDER BY m.measured_at) AS prev_height,
    m.plant_height_cm -
        LAG(m.plant_height_cm) OVER (PARTITION BY m.experiment_id ORDER BY m.measured_at)
        AS height_growth_cm
FROM measurements m
JOIN experiments e ON m.experiment_id = e.id
ORDER BY e.experiment_id, m.measured_at;

-- 2c. Each harvest yield as % of max yield for that crop
SELECT
    e.experiment_id,
    e.crop,
    COALESCE(st.strain_code, 'control') AS strain,
    m.yield_kg_per_ha,
    ROUND(100.0 * m.yield_kg_per_ha /
        MAX(m.yield_kg_per_ha) OVER (PARTITION BY e.crop), 1) AS pct_of_crop_max
FROM measurements m
JOIN experiments e  ON m.experiment_id = e.id
LEFT JOIN strains st ON e.strain_id = st.id
WHERE m.yield_kg_per_ha IS NOT NULL
ORDER BY e.crop, pct_of_crop_max DESC;

-- 3a. Strains never tested in a tropical climate zone
SELECT strain_code, species FROM strains
WHERE id NOT IN (
    SELECT DISTINCT e.strain_id
    FROM experiments e
    JOIN sites s ON e.site_id = s.id
    WHERE s.climate_zone = 'tropical'
      AND e.strain_id IS NOT NULL
);

-- 3b. Experiments with final yield below average for that crop
WITH crop_avg AS (
    SELECT e.crop, AVG(m.yield_kg_per_ha) AS avg_yield
    FROM measurements m
    JOIN experiments e ON m.experiment_id = e.id
    WHERE m.yield_kg_per_ha IS NOT NULL
    GROUP BY e.crop
)
SELECT
    e.experiment_id,
    e.crop,
    e.treatment,
    m.yield_kg_per_ha,
    ROUND(ca.avg_yield, 1) AS crop_avg_yield
FROM measurements m
JOIN experiments e ON m.experiment_id = e.id
JOIN crop_avg    ca ON e.crop = ca.crop
WHERE m.yield_kg_per_ha IS NOT NULL
  AND m.yield_kg_per_ha < ca.avg_yield
ORDER BY e.crop, m.yield_kg_per_ha;

-- 4a. Experiments referencing non-existent site_id or strain_id
SELECT experiment_id, 'bad site_id' AS issue
FROM experiments
WHERE site_id NOT IN (SELECT id FROM sites)
UNION ALL
SELECT experiment_id, 'bad strain_id'
FROM experiments
WHERE strain_id IS NOT NULL
  AND strain_id NOT IN (SELECT id FROM strains);

-- 4b. Biologically impossible measurement values
SELECT *
FROM measurements
WHERE plant_height_cm  > 300
   OR chlorophyll_spad > 80
   OR chlorophyll_spad < 0
   OR yield_kg_per_ha  > 15000
   OR yield_kg_per_ha  < 0
   OR shoot_dw_g       < 0
   OR root_dw_g        < 0;

-- 4c. Experiments with no final yield recorded
SELECT e.experiment_id, e.crop, e.treatment
FROM experiments e
WHERE NOT EXISTS (
    SELECT 1 FROM measurements m
    WHERE m.experiment_id = e.id
      AND m.yield_kg_per_ha IS NOT NULL
);

-- 4d. Duplicate experiment_id values
SELECT experiment_id, COUNT(*) AS count
FROM experiments
GROUP BY experiment_id
HAVING COUNT(*) > 1;
