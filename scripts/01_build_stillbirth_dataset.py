"""
Build the public-use NHANES 2017-March 2020 PFAS/stillbirth analytic dataset.

Expected raw files in ./raw/:
  P_PFAS.xpt
  P_RHQ.xpt
  P_DEMO.xpt
  P_BMX.xpt

Requires: pandas, numpy
"""

from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "raw"
OUT = ROOT / "data"
OUT.mkdir(exist_ok=True)

pfas = pd.read_sas(RAW / "P_PFAS.xpt", format="xport")
rhq  = pd.read_sas(RAW / "P_RHQ.xpt", format="xport")
demo = pd.read_sas(RAW / "P_DEMO.xpt", format="xport")
bmx  = pd.read_sas(RAW / "P_BMX.xpt", format="xport")

df = (
    demo.merge(rhq, on="SEQN", how="inner")
        .merge(pfas, on="SEQN", how="inner")
        .merge(bmx[["SEQN", "BMXBMI"]], on="SEQN", how="left")
)

# Normalize exact zero counts that pandas' XPORT reader may represent as a
# tiny positive floating-point value.
for v in ["RHD167", "RHQ171"]:
    df.loc[df[v].notna() & (df[v].abs() < 1e-10), v] = 0

df = df.loc[
    (df["RIAGENDR"] == 2) &
    (df["RIDAGEYR"].between(20, 59)) &
    (df["RHD167"] >= 1)
].copy()

def derive_stillbirth(row):
    total, live = row["RHD167"], row["RHQ171"]
    if pd.isna(total) or pd.isna(live):
        return np.nan
    if total in (77, 99) or live in (77, 99):
        return np.nan
    if total == 5 and live == 5:
        return np.nan
    if total == 5 and live < 5:
        return 1
    if total < 5 and live == 5:
        return np.nan
    if total < 5 and 0 <= live <= total:
        return int(total > live)
    return np.nan

df["stillbirth_history"] = df.apply(derive_stillbirth, axis=1)
df = df.loc[df["stillbirth_history"].notna()].copy()

race_labels = {
    1: "Mexican American",
    2: "Other Hispanic",
    3: "Non-Hispanic White",
    4: "Non-Hispanic Black",
    6: "Non-Hispanic Asian",
    7: "Other / Multiracial",
}

analytic = pd.DataFrame({
    "SEQN": df["SEQN"].astype("Int64"),
    "age_years": df["RIDAGEYR"],
    "race_ethnicity_code": df["RIDRETH3"].astype("Int64"),
    "race_ethnicity": df["RIDRETH3"].map(race_labels),
    "bmi_kg_m2": df["BMXBMI"],
    "poverty_income_ratio": df["INDFMPIR"],
    "total_deliveries": df["RHD167"],
    "live_birth_deliveries": df["RHQ171"],
    "stillbirth_history": df["stillbirth_history"].astype("Int64"),
    "pfhxs_ng_ml": df["LBXPFHS"],
    "pfna_ng_ml": df["LBXPFNA"],
    "n_pfoa_ng_ml": df["LBXNFOA"],
    "n_pfos_ng_ml": df["LBXNFOS"],
    "sm_pfos_ng_ml": df["LBXMFOS"],
    "pfos_total_ng_ml": df["LBXNFOS"] + df["LBXMFOS"],
    "pfas_subsample_weight": df["WTSBAPRP"],
    "survey_stratum": df["SDMVSTRA"].astype("Int64"),
    "survey_psu": df["SDMVPSU"].astype("Int64"),
})

model_vars = [
    "stillbirth_history", "pfhxs_ng_ml", "age_years", "race_ethnicity_code",
    "bmi_kg_m2", "poverty_income_ratio", "total_deliveries",
    "pfas_subsample_weight", "survey_stratum", "survey_psu"
]
analytic["primary_model_complete_case"] = analytic[model_vars].notna().all(axis=1).astype(int)
analytic["sensitivity_age_20_49"] = (analytic["age_years"] <= 49).astype(int)

analytic.to_csv(OUT / "nhanes_2017_2020_pfas_stillbirth_analytic.csv", index=False)

print(f"Rows: {len(analytic)}")
print(analytic["stillbirth_history"].value_counts(dropna=False))
print("Primary model complete cases:",
      int(analytic["primary_model_complete_case"].sum()))
