import pandas as pd

# -----------------------------
# Helper functions
# -----------------------------

def reference_value(instance, ref_dict):
    """
    Returns (ref_value, is_optimal)
    """
    lb, ub = ref_dict[instance]
    if lb == ub:
        return lb, True
    return ub, False


def compute_gap(value, ref):
    return 100.0 * (value - ref) / ref


def format_cell(value, gap):
    return f"{int(value)} ({gap:.2f}\\%)"


# -----------------------------
# Main table generation
# -----------------------------

def generate_table(csv_path, ref_dict, size_dict):
    """
    csv_path   : path to results csv
    ref_dict   : {instance: (LB, UB)}
    size_dict  : {instance: "J×M"}  (already formatted in LaTeX)
    """

    df = pd.read_csv(csv_path)

    rows = []

    for instance in sorted(ref_dict.keys()):
        ref, is_opt = reference_value(instance, ref_dict)

        # --- ECT ---
        ect_val = (
            df[(df.instance == instance) & (df.algorithm == "ECT")]
            .makespan
            .iloc[0]
        )
        ect_gap = compute_gap(ect_val, ref)

        # --- ACSi (best of 30) ---
        acsi_best = (
            df[(df.instance == instance) & (df.algorithm == "ACSi")]
            .makespan
            .min()
        )
        acsi_gap = compute_gap(acsi_best, ref)

        # --- ACSp (best of 30) ---
        acsp_best = (
            df[(df.instance == instance) & (df.algorithm == "ACSp")]
            .makespan
            .min()
        )
        acsp_gap = compute_gap(acsp_best, ref)

        # --- UB formatting ---
        lb, ub = ref_dict[instance]
        if lb == ub:
            ub_str = f"\\opt{{{ub}}}"
        else:
            ub_str = f"{ub}"

        rows.append(
            f"{instance}"
            f"&{size_dict[instance]}"
            f"&{ub_str}"
            f"&{format_cell(ect_val, ect_gap)}"
            f"&{format_cell(acsi_best, acsi_gap)}"
            f"&{format_cell(acsp_best, acsp_gap)}\\\\"
        )

    # -----------------------------
    # LaTeX table output
    # -----------------------------

    header = r"""
\begin{tabular}{l|c|r|r|r|r}
\hline
\textbf{Instance} & Size & UB & ECT & ACS$_i$ & ACS$_p$\\
\hline
"""

    footer = r"""
\hline
\end{tabular}
"""

    table = header + "\n".join(rows) + footer
    return table



if __name__ == "__mainfattahi__":
    # Example usage
    ref_dict = {
        'SFJS1': (66,66),
        'SFJS2': (107,107),
        'SFJS3': (221,221),
        'SFJS4': (355,355),
        'SFJS5': (119,119),
        'SFJS6': (320,320),
        'SFJS7': (397,397),
        'SFJS8': (253,253),
        'SFJS9': (210,210),
        'SFJS10': (516,516),
        'MFJS1': (468,468),
        'MFJS2': (446,446),
        'MFJS3': (466,466),
        'MFJS4': (554,554),
        'MFJS5': (514,514),
        'MFJS6': (614,634),
        'MFJS7': (879,879), 
        'MFJS8': (775,884),
        'MFJS9': (845.26,1088),
        'MFJS10': (944.8,1251)
    }

    size_dict = {
        "SFJS1":  "2\\times2",
        "SFJS2":  "2\\times2",
        "SFJS3":  "3\\times2",
        "SFJS4":  "3\\times2",
        "SFJS5":  "3\\times2",
        "SFJS6":  "3\\times2",
        "SFJS7":  "3\\times5",
        "SFJS8":  "3\\times4",
        "SFJS9":  "3\\times3",
        "SFJS10": "4\\times5",
        "MFJS1":  "5\\times6",
        "MFJS2":  "5\\times7",
        "MFJS3":  "6\\times7",
        "MFJS4":  "7\\times7",
        "MFJS5":  "7\\times7",
        "MFJS6":  "8\\times7",
        "MFJS7":  "8\\times7",
        "MFJS8":  "9\\times8",
        "MFJS9":  "11\\times8",
        "MFJS10": "12\\times8",
    }


    table_latex = generate_table("./paper/fattahi_brandimarte.csv", ref_dict, size_dict)
    print(table_latex)



if __name__ == "__mainbrandimarte__":
    # Example usage
    ref_dict = {
        'MK1': (40,40),
        'MK2': (25,26),
        'MK3': (204,204),
        'MK4': (48,60),
        'MK5': (168,172),
        'MK6': (37,58),
        'MK7': (133,139),
        'MK8': (523,523),
        'MK9': (307,307),
        'MK10': (165,197),
        'MK11': (594,649),
        'MK12': (508,508),
        'MK13': (353,478),
        'MK14': (694,694),
        'MK15': (283,383),
    }

    size_dict = {
        'MK1': "10$\\times$6",
        'MK2': "10$\\times$6",
        'MK3': "15$\\times$8",
        'MK4': "15$\\times$8",
        'MK5': "15$\\times$4",
        'MK6': "10$\\times$15",
        'MK7': "20$\\times$5",
        'MK8': "20$\\times$10",
        'MK9': "20$\\times$10",
        'MK10': "20$\\times$15",
        'MK11': "30$\\times$5",
        'MK12': "30$\\times$10",
        'MK13': "30$\\times$10",
        'MK14': "30$\\times$15",
        'MK15': "30$\\times$15",
    }


    table_latex = generate_table("./paper/fattahi_brandimarte.csv", ref_dict, size_dict)
    print(table_latex)


if __name__ == "__main__":
    # Example usage
    ref_dict = {
        'RBSZ1': (1370.81,1370.81),
        'RBSZ2': (14310.42,14310.42),
        'RBSZ3': (522.62,522.62),
        'RBSZ4': (1536.37,1536.37),
    }

    size_dict = {
        'RBSZ1': "110$\\times$27",
        'RBSZ2': "155$\\times$40",
        'RBSZ3': "180$\\times$39",
        'RBSZ4': "1435$\\times$29",
    }


    table_latex = generate_table("./paper/ribeirosuzarte.csv", ref_dict, size_dict)
    print(table_latex)



