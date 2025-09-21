-- BigQuery SQL
CREATE OR REPLACE FUNCTION `kaggle-clinical-trials.aact.standardize_trial_inputs_fn`(
  official_title STRING,
  eligibility TEXT,
  raw_conditions STRING,
  raw_interventions STRING
)
RETURNS TABLE<ai_conditions ARRAY<STRING>, ai_interventions ARRAY<STRING>, metastatic BOOL>
AS (
  SELECT
    AI.GENERATE((
      'Extract the NCCN term(s) for the clinical condition(s) being studied. The term can be one or more of the following: "Acute Lymphoblastic Leukemia", "Acute Myeloid Leukemia", "Ampullary Adenocarcinoma", "Anal Carcinoma", "Astrocytoma", "B-Cell Lymphoma; Other or Unspecified", "B-Cell Lymphomas", "Basal Cell Skin Cancer", "Biliary Tract Cancers", "Bladder Cancer", "Bone Cancer", "Bone Sarcoma; Unspecified", "Breast Cancer", "Burkitt Lymphoma", "Cancer; Other or Unspecified", "Castleman Disease", "Central Nervous System Cancer, Other or Unspecified", "Central Nervous System Cancers", "Cervical Cancer", "Chondrosarcoma", "Chronic Lymphocytic Leukemia/Small Lymphocytic Lymphoma", "Chronic Myeloid Leukemia", "Classic Follicular Lymphoma", "Colon Cancer", "Dermatofibrosarcoma Protuberans", "Diffuse Large B-Cell Lymphoma", "Endometrial Carcinoma", "Ependymoma", "Esophageal and Esophagogastric Junction Cancers", "Esophageal and Esophagogastric Junction Cancers; Adenocarcinoma", "Esophageal and Esophagogastric Junction Cancers; Squamous Cell Carcinoma", "Esophageal and Esophagogastric Junction Cancers; Unspecified", "Essential Thrombocythemia", "Ewing Sarcoma", "Gastric Cancer", "Gastrointestinal Stromal Tumors", "Gestational Trophoblastic Neoplasia", "Glioblastoma", "Hairy Cell Leukemia", "Head and Neck Cancer; Unspecified", "Head and Neck Cancers", "Hepatocellular Carcinoma", "Histiocytic Neoplasms", "Hodgkin Lymphoma", "Hypopharyngeal Cancer", "Kaposi Sarcoma", "Kidney Cancer", "Larengeal Cancer", "Leiomyosarcoma", "Leukemia; Other or Unspecified", "Liposarcoma", "Liver Cancer; Other or Unspecified", "Lung Cancer; Other or Unspecified", "Lymphoma; Other or Unspecified", "Mantle Cell Lymphoma", "Marginal Zone Lymphoma", "Medulloblastoma", "Melanoma: Non-Occular", "Melanoma: Occular", "Melanoma: Uveal", "Merkel Cell Carcinoma", "Mesothelioma: Peritoneal", "Mesothelioma: Pleural", "Multiple Myeloma", "Myelodysplastic Syndromes", "Myeloid/Lymphoid Neoplasms with Eosinophilia and Tyrosine Kinase Gene Fusions", "Myeloproliferative Neoplasms", "Myeloproliferative Neoplasms; Unspecified", "Nasopharyngeal Cancer", "Neuroblastoma", "Neuroendocrine and Adrenal Tumors", "Neuroendocrine and Adrenal Tumors; Unspecified", "Non-Small Cell Lung Cancer (NSCLC)", "Non-Small Cell Lung Cancer (NSCLC); Adenocarcinoma", "Non-Small Cell Lung Cancer (NSCLC); Other or Unspecified", "Non-Small Cell Lung Cancer (NSCLC); Squamous Cell Carcinoma", "Occult Primary", "Oligodendroglioma", "Oral Cavity Cancer", "Oropharyngeal Cancer", "Osteosarcoma", "Ovarian Cancer/Fallopian Tube Cancer/Primary Peritoneal Cancer", "Pancreatic Adenocarcinoma", "Pancreatic Neuroendocrine Tumors", "Paraganglioma", "Penile Cancer", "Pheochromocytoma", "Polycythemia Vera", "Primary Cutaneous Lymphomas", "Primary Myelofibrosis", "Prostate Cancer", "Rectal Cancer", "Rhabdomyosarcoma", "Salivary Gland Cancer", "Small Bowel Adenocarcinoma", "Small Cell Lung Cancer (SCLC)", "Soft Tissue Sarcoma", "Soft Tissue Sarcoma; Unspecified", "Squamous Cell Skin Cancer", "Synovial sarcoma", "Systemic Light Chain Amyloidosis", "Systemic Mastocytosis", "T-Cell Lymphomas", "Testicular Cancer", "Thymomas and Thymic Carcinomas", "Thyroid Carcinoma", "Uterine Cancer; Unspecified", "Uterine Neoplasms", "Uterine Sarcoma", "Vaginal Cancer", "Vulvar Cancer", "Waldenström Macroglobulinemia / Lymphoplasmacytic Lymphoma", "Wilms Tumor (Nephroblastoma)"',
      'Provide only the relevant clinical term(s) as an array without JSON or line breaks. If a trial studies all cancer conditions, simply provide "All cancers" as a response. If a trial studies all solid tumors, provide "All solid cancers" as a response. If a trial does not study cancer, provide "Not cancer" as a response.',
      '\n\nTITLE: ', official_title,
      '\nCONDITIONS: ', raw_conditions
    ),
    connection_id => 'us.kaggle_connection',
    endpoint => 'gemini-2.5-flash',
    output_schema => 'items ARRAY<STRING>'
    ).items AS ai_conditions,

    AI.GENERATE((
       'Categorize the treatment(s) being investigated in the trial below into one or more of the following categories: Conventional Therapies, Targeted Therapies, Immunotherapies, Cell-based Therapies, Gene and Nucleic Acid Therapies, Artificial Intelligence, or Other',
       'Focus on the drug being tested, not the control arm of the trial.',
       'For investigational drug names (e.g., ABC-123): map to category if known; if not, classify as an investigational drug and preserve the code name using the following format: "investigational drug (ABC-123)".',
       'Return only an array of distinct strings in lowercase.',
       '\n\nTITLE: ', official_title,
       '\nINTERVENTIONS: ', mesh_interventions
    ),
    connection_id => 'us.kaggle_connection',
    endpoint => 'gemini-2.5-flash',
    output_schema => 'items ARRAY<STRING>'
    ).items AS ai_interventions,

    AI.GENERATE_BOOL((
        'Does the trial', brief_title, 'include patients with advanced/metastatic disease?',
        '\nELIGIBILITY CRITERIA:', eligibility
    ),
    connection_id => 'us.kaggle_connection',
    endpoint => 'gemini-2.5-flash'
    ).result AS metastatic,

    AI.GENERATE_INT(
        (
        'Evaluate and score the *complexity* of eligibility criteria in cancer clinical trials. Complexity refers to how difficult a criterion is to interpret, implement, or operationalize. It considers Boolean logic, temporal constraints, diagnostic or lab requirements, and whether clinician judgment is required. Use insights from Ross et al. (PMC3041539) on trial eligibility complexity.',
        'Scoring scale (1–5):',
        '1 = Low Complexity: Some Boolean logic or a single diagnostic/biomarker requirement (e.g., "Measurable disease by RECIST and ECOG ≤2")',
        '2 = Moderate Complexity: Multiple conditions combined with AND/OR logic or temporal qualifiers (e.g., "No chemotherapy within 6 months AND ECOG ≤2")',
        '3 = High Complexity: Several clauses spanning diagnostic, biomarker, and treatment history requirements, often with temporal constraints (e.g., "Histologically confirmed disease AND prior treatment within 3 months AND measurable disease")',
        '4 = Very High Complexity: Nested logic, multiple temporal + diagnostic + treatment requirements that are difficult to parse (e.g., "If patient received therapy X within 6 months, must also meet biomarker Y and ECOG ≤1")',
        '5 = Extreme Complexity: Extensive nested logic, numerous temporal and diagnostic conditions, vague or clinician-dependent wording, very hard to implement consistently (e.g., "If patient previously received therapy X, then must meet criteria Y and Z unless biomarker A is negative or ECOG >2")',
        'Provide only the score (1–5).',
        '\n\nTITLE: ', official_title,
        '\nEligibility criteria: ', eligibility
        ),
        connection_id => 'us.kaggle_connection',
        endpoint      => 'gemini-2.5-flash').result AS ai_complexity_score,
    AI.GENERATE_INT(
        (
        'Evaluate and score the *patient burden* of a cancer clinical trial. Patient burden refers to how demanding or disruptive a criterion is for the patient in terms of procedures, site visits, time, and data collection. Use concepts from the PHESI Patient Burden Score (PAS).',
        'Scoring scale (1–5):',
        '1 = Very Low Burden: Minimal requirements (e.g., basic age, consent, ECOG check)',
        '2 = Low Burden: Some routine labs or imaging, 1–2 extra site visits, modest data collection',
        '3 = Moderate Burden: Requires biomarker test, measurable disease, or repeated labs/imaging; moderate number of visits or outcome measures',
        '4 = High Burden: Invasive procedures (fresh biopsy, lumbar puncture), frequent visits, many data/outcome measures',
        '5 = Very High Burden: Serial invasive procedures, hospitalization, or frequent/prolonged visits; heavy disruption to patient life',
        'Provide only the score (1-5).',
        '\n\nTITLE: ', official_title,
        '\nEligibility criteria: ', eligibility,
        '\nStudy design: ', description
        ),
        connection_id => 'us.kaggle_connection',
        endpoint      => 'gemini-2.5-flash').result AS ai_burden_score
);


