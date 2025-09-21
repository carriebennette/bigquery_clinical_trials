--Don't need to query for incidence (all values are pre-computed and stored on BigQuery)
CREATE OR REPLACE FUNCTION `kaggle-clinical-trials.aact.standardize_and_engineer_features_fn`(
  official_title STRING,
  eligibility TEXT,
  raw_conditions STRING,
  raw_interventions STRING,
  phase STRING,
  is_randomized BOOL,
  is_blinded BOOL
)
RETURNS TABLE<
  total_incidence FLOAT64,
  total_deaths FLOAT64,
  num_interventions INT64,
  num_conditions INT64,
  intervention_chemotherapy INT64,
  intervention_targeted INT64,
  intervention_immuno INT64,
  intervention_conventional INT64,
  intervention_investigational INT64,
  is_randomized INT64,
  is_blinded INT64,
  phase_2 INT64,
  phase_3 INT64
>
AS (
  WITH llm AS (
    SELECT * 
    FROM `kaggle-clinical-trials.aact.standardize_trial_inputs_fn`(
      official_title, eligibility, raw_conditions, raw_interventions
    )
  ),

  -- Flatten conditions and interventions
  exploded_conditions AS (
    SELECT ai_condition
    FROM llm, UNNEST(ai_conditions) AS ai_condition
  ),

  flattened_interventions AS (
    SELECT
      LOWER(TRIM(REGEXP_REPLACE(ai_intervention, r"investigational drug.*", "investigational drug"))) AS cleaned_intervention
    FROM llm, UNNEST(ai_interventions) AS ai_intervention
  ),

  epi_lookup AS (
    SELECT
      SUM(e.incidence) AS total_incidence,
      SUM(e.deaths) AS total_deaths
    FROM exploded_conditions c
    LEFT JOIN `kaggle-clinical-trials.aact.epidemiology_data` e
    ON c.ai_condition = e.ai_condition
  ),

  intervention_encoding AS (
    SELECT
      COUNT(*) AS num_interventions,
      COUNTIF(cleaned_intervention = 'chemotherapy') AS intervention_chemotherapy,
      COUNTIF(cleaned_intervention = 'targeted therapies') AS intervention_targeted,
      COUNTIF(cleaned_intervention = 'immunotherapies') AS intervention_immuno,
      COUNTIF(cleaned_intervention = 'conventional therapies') AS intervention_conventional,
      COUNTIF(cleaned_intervention = 'investigational drug') AS intervention_investigational
    FROM flattened_interventions
  )

  SELECT
    e.total_incidence,
    e.total_deaths,
    i.num_interventions,
    ARRAY_LENGTH(l.ai_conditions) AS num_conditions,
    i.intervention_chemotherapy,
    i.intervention_targeted,
    i.intervention_immuno,
    i.intervention_conventional,
    i.intervention_investigational,
    IF(is_randomized, 1, 0) AS is_randomized,
    IF(is_blinded, 1, 0) AS is_blinded,
    IF(phase = "2", 1, 0) AS phase_2,
    IF(phase = "3", 1, 0) AS phase_3
  FROM llm l
  CROSS JOIN epi_lookup e
  CROSS JOIN intervention_encoding i
);