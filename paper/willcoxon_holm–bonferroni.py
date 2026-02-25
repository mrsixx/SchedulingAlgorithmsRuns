import pandas as pd
import numpy as np
from scipy.stats import wilcoxon
from statsmodels.stats.multitest import multipletests

def descriptive_pairwise_analysis(
    df,
    algo_a,
    algo_b,
    metric="makespan"
):
    """
    Performs descriptive pairwise comparison between two algorithms
    using per-instance medians.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame with columns [instance, algorithm, run, makespan, time]
    algo_a : str
        First algorithm (e.g., "ACSp")
    algo_b : str
        Second algorithm (e.g., "ACSi")
    metric : str
        Metric to analyze ("makespan" or "time")

    Returns
    -------
    dict with descriptive statistics
    """

    # Compute median per instance and algorithm
    medians = (
        df[df["algorithm"].isin([algo_a, algo_b])]
        .groupby(["instance", "algorithm"])[metric]
        .median()
        .unstack()
        .dropna()
    )

    # Differences
    diff = medians[algo_a] - medians[algo_b]

    wins_a = (diff < 0).sum()
    wins_b = (diff > 0).sum()
    ties = (diff == 0).sum()
    total = len(diff)

    # Relative improvement (%)
    rel_improvement = (medians[algo_b] - medians[algo_a]) / medians[algo_b] * 100

    results = {
        # "Alg. A": algo_a,
        # "Alg. B": algo_b,
        # "Metric": metric,
        "Instances": total,
        f"{algo_a} wins": wins_a,
        f"{algo_b} wins": wins_b,
        "Ties": ties,
        f"{algo_a} win rate (%)": 100 * wins_a / total,
        f"{algo_b} win rate (%)": 100 * wins_b / total,
        "Median absolute difference": np.median(diff),
        "Median relative improvement (%)": np.median(rel_improvement),
    }

    return results



# ===============================
# 1. Load data
# ===============================
# df = pd.read_csv("./paper/fattahi_brandimarte.csv")
df = pd.read_csv("./paper/ribeirosuzarte.csv")

# Sanity check
required_cols = {"instance", "algorithm", "run", "makespan", "time"}
assert required_cols.issubset(df.columns), "CSV header does not match expected format"

# ===============================
# 2. Aggregate: median makespan per instance & algorithm
# ===============================
agg = (
    df.groupby(["instance", "algorithm"])["makespan"]
      .median()
      .reset_index()
)

# Pivot to wide format: one row per instance
pivot = agg.pivot(index="instance", columns="algorithm", values="makespan")

# Keep only instances where all algorithms are present
pivot = pivot.dropna(subset=["ECT", "ACSi", "ACSp"])

# ===============================
# 3. Prepare paired samples
# ===============================
ect   = pivot["ECT"].values
acsi  = pivot["ACSi"].values
acsp  = pivot["ACSp"].values

# ===============================
# 4. Wilcoxon signed-rank tests
#    (one-sided: ACS expected to be better than ECT)
# ===============================
tests = {
    "ACSi vs ECT": wilcoxon(acsi, ect, alternative="less"),
    "ACSp vs ECT": wilcoxon(acsp, ect, alternative="less"),
    "ACSp vs ACSi": wilcoxon(acsp, acsi, alternative="two-sided"),
}

# Collect raw p-values
test_names = []
p_values = []

for name, result in tests.items():
    test_names.append(name)
    p_values.append(result.pvalue)

# ===============================
# 5. Holm–Bonferroni correction
# ===============================
reject, pvals_corrected, _, _ = multipletests(
    p_values, alpha=0.05, method="holm"
)

# ===============================
# 6. Report results
# ===============================
results = pd.DataFrame({
    "Comparison": test_names,
    "Raw p-value": p_values,
    "Adjusted p-value (Holm)": pvals_corrected,
    "Significant (α=0.05)": reject
})

print("\nWilcoxon signed-rank test results (makespan):\n")
print(results.to_string(index=False))
print("\n\n")


# ACSi vs ECT
res_acsi_ect = descriptive_pairwise_analysis(
    df, "ACSi", "ECT", metric="makespan"
)

print("ACSi vs ECT (makespan):")
print(pd.DataFrame([res_acsi_ect]).to_string(index=False))
print("\n\n")

# ACSp vs ECT
res_acsp_ect = descriptive_pairwise_analysis(
    df, "ACSp", "ECT", metric="makespan"
)

print("ACSp vs ECT (makespan):")
print(pd.DataFrame([res_acsp_ect]).to_string(index=False))
print("\n\n")

# ACSp vs ACSi (makespan)
res_acsp_acsi = descriptive_pairwise_analysis(
    df, "ACSp", "ACSi", metric="makespan"
)

print("ACSp vs ACSi (makespan):")
print(pd.DataFrame([res_acsp_acsi]).to_string(index=False))
print("\n\n")