# PFHxS and stillbirth history: NHANES 2017-March 2020
# Requires: survey, readr, dplyr, broom

library(survey)
library(readr)
library(dplyr)
library(broom)

options(survey.lonely.psu = "adjust")

dat <- read_csv("data/nhanes_2017_2020_pfas_stillbirth_analytic.csv",
                show_col_types = FALSE)

cc <- dat %>%
  filter(primary_model_complete_case == 1)

des <- svydesign(
  ids = ~survey_psu,
  strata = ~survey_stratum,
  weights = ~pfas_subsample_weight,
  nest = TRUE,
  data = cc
)

# Primary model: effect estimate is per doubling of PFHxS.
fit_pfhxs <- svyglm(
  stillbirth_history ~ log2(pfhxs_ng_ml) +
    age_years + I(age_years^2) +
    factor(race_ethnicity_code) +
    bmi_kg_m2 + poverty_income_ratio +
    total_deliveries,
  design = des,
  family = quasibinomial()
)

primary <- tidy(fit_pfhxs, conf.int = TRUE) %>%
  filter(term == "log2(pfhxs_ng_ml)") %>%
  mutate(
    aOR = exp(estimate),
    CI_low = exp(conf.low),
    CI_high = exp(conf.high)
  )

print(primary)

# Sensitivity analysis restricted to ages 20-49.
des_20_49 <- subset(des, sensitivity_age_20_49 == 1)

fit_20_49 <- svyglm(
  stillbirth_history ~ log2(pfhxs_ng_ml) +
    age_years + I(age_years^2) +
    factor(race_ethnicity_code) +
    bmi_kg_m2 + poverty_income_ratio +
    total_deliveries,
  design = des_20_49,
  family = quasibinomial()
)

sensitivity <- tidy(fit_20_49, conf.int = TRUE) %>%
  filter(term == "log2(pfhxs_ng_ml)") %>%
  mutate(
    aOR = exp(estimate),
    CI_low = exp(conf.low),
    CI_high = exp(conf.high)
  )

print(sensitivity)

# Comparison PFAS models.
pfas_vars <- c("pfna_ng_ml", "n_pfoa_ng_ml", "pfos_total_ng_ml")

comparison_results <- lapply(pfas_vars, function(v) {
  f <- as.formula(
    paste0(
      "stillbirth_history ~ log2(", v, ") + ",
      "age_years + I(age_years^2) + factor(race_ethnicity_code) + ",
      "bmi_kg_m2 + poverty_income_ratio + total_deliveries"
    )
  )
  model <- svyglm(f, design = des, family = quasibinomial())
  tidy(model, conf.int = TRUE) %>%
    filter(grepl("^log2", term)) %>%
    mutate(
      exposure = v,
      aOR = exp(estimate),
      CI_low = exp(conf.low),
      CI_high = exp(conf.high)
    )
})

bind_rows(comparison_results) %>%
  select(exposure, aOR, CI_low, CI_high, p.value) %>%
  print()
