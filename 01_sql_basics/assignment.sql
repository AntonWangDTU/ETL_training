-- Module 01: SQL Basics — IBIS Research Database
-- Run against ibis.db:  sqlite3 ibis.db < 01_sql_basics/assignment.sql

-- 1a. List all bacterial strains
-- SELECT * FROM strains;


-- 1b. Strain code and species of nitrogen-fixing strains only
--SELECT strain_code, species FROM strains where nitrogen_fixing = 1;

-- 1c. All field sites in Kenya
-- SELECT * FROM sites WHERE country = 'Kenya';

-- 2a. All experiments where crop is wheat
-- SELECT * FROM experiments WHERE crop = 'wheat'

-- 2b. All control experiments (no inoculant applied)
-- SELECT * FROM experiments WHERE treatment = 'control'

-- 2c. Final harvest measurements (yield not null), sorted by yield descending
-- SELECT * FROM measurements 
-- WHERE yield_kg_per_ha IS NOT NULL
-- ORDER BY yield_kg_per_ha DESC;

-- 3a. Total number of experiments
-- SELECT COUNT(*) FROM experiments;
-- SELECT COUNT(*) AS total_experiments FROM experiments;



-- 3b. Number of experiments per treatment type
SELECT treatment, COUNT(*) AS count
FROM experiments
GROUP BY treatment;


-- 3c. Average yield across all measurements that have a yield value
-- SELECT ROUND(AVG(yield_kg_per_ha), 1) AS avg_yield_kg_per_ha
-- FROM measurements
-- WHERE yield_kg_per_ha IS NOT NULL;

-- 4a. Every experiment with site country and strain species (include controls)
SELECT 


-- 4b. Final measurements with: experiment_id, crop, treatment, country, strain_code, yield
-- YOUR QUERY HERE

-- 4c. Each researcher and how many experiments they are responsible for
-- YOUR QUERY HERE

-- 5a. Average yield per crop type
-- YOUR QUERY HERE

-- 5b. Countries with more than 2 experimental sites
-- YOUR QUERY HERE

-- 5c. Strains used in more than 1 experiment
-- YOUR QUERY HERE
