# PFAS and Stillbirth History in NHANES 2017-March 2020

## Project overview

This repository contains a reproducible public-use NHANES dataset for examining the association between measured serum per- and polyfluoroalkyl substances (PFAS), particularly perfluorohexane sulfonic acid (PFHxS), and a derived history of stillbirth among U.S. women.

The project uses the **NHANES 2017-March 2020 pre-pandemic** public-use files. Serum PFAS were measured in a one-third subsample, so analyses must use the PFAS-specific subsample weight and the NHANES complex survey design variables.

## Research question

Among U.S. women with a history of delivery, are serum PFAS concentrations associated with a history of stillbirth?

The primary exposure is **PFHxS**. PFNA, n-PFOA, and calculated total PFOS are retained as comparison exposures.

## Source files

The analytic dataset was built from four public NHANES files:

| File | Component | Key variables |
|---|---|---|
| `P_PFAS.xpt` | Serum PFAS laboratory data | PFHxS, PFNA, n-PFOA, PFOS isomers, `WTSBAPRP` |
| `P_RHQ.xpt` | Reproductive Health Questionnaire | `RHD167`, `RHQ171` |
| `P_DEMO.xpt` | Demographics and survey design | age, race/ethnicity, PIR, `SDMVSTRA`, `SDMVPSU` |
| `P_BMX.xpt` | Body Measures | BMI |

Official documentation:

- PFAS: https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/P_PFAS.htm
- Reproductive Health: https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/P_RHQ.htm
- Demographics: https://wwwn.cdc.gov/NCHS/Data/Nhanes/Public/2017/DataFiles/P_DEMO.htm
- Body Measures: https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/P_BMX.htm

The raw XPT files are **not required to use the analytic CSV**. To rebuild the dataset, place the four files in a repository-level `raw/` folder and run `scripts/01_build_stillbirth_dataset.py`.

## Cohort

The cleaned dataset contains women who:

1. were age **20-59 years** at NHANES participation;
2. had measured PFAS data;
3. reported at least one delivery; and
4. had a reproductive history that allowed stillbirth status to be classified unambiguously from the public-use delivery variables.

The final derived dataset contains **591 women**, including **43 with derived stillbirth history** and **548 without derived stillbirth history**.

For the primary adjusted model, **466 women** have complete data for PFHxS, age, race/ethnicity, BMI, poverty-income ratio, number of deliveries, and NHANES survey-design variables; **30** have derived stillbirth history.

The age 20-49 sensitivity complete-case sample contains **323 women**, including **19** with derived stillbirth history.

## Stillbirth derivation

NHANES asks:

- `RHD167`: **Total number of deliveries**, instructing participants to count vaginal and Cesarean deliveries and to count stillbirths as well as live births.
- `RHQ171`: **How many deliveries resulted in a live birth?**

A derived history of stillbirth is therefore coded as:

`stillbirth_history = 1` when total deliveries exceed deliveries resulting in live birth.

`stillbirth_history = 0` when the two counts are equal and the counts are known exactly.

### Important public-use top-coding issue

In the uploaded public-use `P_RHQ.xpt`, both delivery variables are top-coded at **5 or more**.

- `RHD167 = 5` and `RHQ171 < 5` is classified as stillbirth history because at least one delivery definitively did not result in a live birth.
- `RHD167 = 5` and `RHQ171 = 5` is **excluded as ambiguous**. The participant could have had exactly five deliveries and five live births, or more than five deliveries with five live-birth deliveries.
- Implausible/inconsistent combinations and missing/refused/don't-know responses are excluded.

Thus, the outcome is a **derived lifetime history of stillbirth**, not a directly asked NHANES stillbirth item.

## Exposure variables

Serum concentrations are expressed in ng/mL.

- `pfhxs_ng_ml`: PFHxS
- `pfna_ng_ml`: PFNA
- `n_pfoa_ng_ml`: linear PFOA
- `pfos_total_ng_ml`: calculated as n-PFOS + Sm-PFOS

For regression modeling, PFAS concentrations should be **log2-transformed**, so an odds ratio represents the change in odds associated with a **doubling** of serum concentration.

## Survey analysis

PFAS were measured in a one-third NHANES subsample. Use:

- Weight: `pfas_subsample_weight` (`WTSBAPRP`)
- Stratum: `survey_stratum` (`SDMVSTRA`)
- PSU: `survey_psu` (`SDMVPSU`)

The included `scripts/02_analysis_stillbirth.R` uses the R `survey` package for design-based logistic regression.

The planned primary model is:

`stillbirth history ~ log2(PFHxS) + age + age^2 + race/ethnicity + BMI + poverty-income ratio + number of deliveries`

A sensitivity analysis restricts the sample to ages **20-49 years**.

## Files in this repository

```text
data/
  nhanes_2017_2020_pfas_stillbirth_analytic.csv
  data_dictionary.csv

scripts/
  01_build_stillbirth_dataset.py
  02_analysis_stillbirth.R

README.md
```

## Key limitations

1. **Cross-sectional exposure measurement.** Serum PFAS was measured at the NHANES examination, often years after the pregnancy or stillbirth. Temporal ordering cannot be established.
2. **Reproductive history can influence PFAS concentrations.** Pregnancy and lactation can reduce maternal PFAS body burden, creating potential reverse-causation or reproductive-history bias.
3. **Stillbirth is derived rather than directly reported.** The outcome relies on the difference between total delivery and live-birth delivery counts.
4. **Timing is unavailable.** The dataset does not identify the year, gestational age, or pregnancy-specific PFAS concentration associated with the stillbirth.
5. **Top-coding.** Women with `5+` total deliveries and `5+` live-birth deliveries cannot be classified unambiguously and are excluded.
6. **Small number of cases.** Estimates should be interpreted as hypothesis-generating and require confirmation in longitudinal pregnancy cohorts.
7. **Multiple PFAS comparisons.** If several PFAS are examined, multiplicity should be acknowledged and adjusted analyses considered.

## Suggested citation of the data source

Centers for Disease Control and Prevention, National Center for Health Statistics. National Health and Nutrition Examination Survey, 2017-March 2020 Pre-Pandemic Data. https://www.cdc.gov/nchs/nhanes/

## Suggested project title

**Serum Perfluorohexane Sulfonic Acid and History of Stillbirth Among U.S. Women: NHANES 2017-March 2020**

## Reproducibility note

`SEQN` is retained because it is the public NHANES participant identifier needed for transparent linkage and verification. The analytic file contains only variables from publicly available, de-identified NHANES datasets and includes no restricted geographic identifiers.
