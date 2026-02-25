import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def load_time_data(csv_path):
    """
    Lê o CSV e retorna um DataFrame com a mediana do tempo
    por instância e algoritmo.
    """
    df = pd.read_csv(csv_path)

    time_inst = (
        df.groupby(["instance", "algorithm"])["time"]
        .median()
        .reset_index()
    )

    return time_inst

import matplotlib.pyplot as plt

def plot_time_boxplot(time_inst, output_path):
    """
    Salva um boxplot do tempo de execução (mediana por instância)
    comparando ACSi e ACSp.
    """
    acsi = time_inst[time_inst["algorithm"] == "ACSi"]["time"]
    acsp = time_inst[time_inst["algorithm"] == "ACSp"]["time"]

    plt.figure()
    plt.boxplot([acsi, acsp], labels=["ACSi", "ACSp"])
    plt.ylabel("Median execution time (ms)")
    plt.yscale('log')
    # plt.title("Execution time distribution per instance")

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"Boxplot saved to: {output_path}")


def plot_time_vs_size(time_inst, size_dict, output_path):
    """
    Scatter plot do tempo vs tamanho da instância com
    distinção por shape e estilo de linha (P&B friendly).
    """
    df = time_inst.copy()
    df["size"] = df["instance"].map(size_dict)
    df = df.dropna(subset=["size"])

    styles = {
        "ACSi": {"marker": "o", "linestyle": "-"},
        "ACSp": {"marker": "^", "linestyle": "--"}
    }

    plt.figure()

    for alg in ["ACSi", "ACSp"]:
        subset = df[df["algorithm"] == alg]

        x = subset["size"].values
        y = subset["time"].values

        style = styles[alg]

        # Scatter
        plt.scatter(
            x,
            y,
            marker=style["marker"],
            #label=alg,
            #facecolors="none",   # melhora leitura em P&B
            #edgecolors="black"
        )

        # Trend line (log-log)
        log_x = np.log10(x)
        log_y = np.log10(y)
        slope, intercept = np.polyfit(log_x, log_y, 1)

        x_fit = np.logspace(log_x.min(), log_x.max(), 100)
        y_fit = 10 ** (intercept + slope * np.log10(x_fit))

        a = 10 ** intercept
        b = slope

        plt.plot(
            x_fit,
            y_fit,
            linestyle=style["linestyle"],
            #color="black",
            label=rf"{alg}: $t = {a:.2g}\, s^{{{b:.2f}}}$"
        )

    plt.xlabel("Instance size (|J| × |M|)")
    plt.ylabel("Median execution time (ms)")
    plt.xscale("log")
    plt.yscale("log")
    plt.legend()

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"Time vs size plot saved to: {output_path}")
def plot_time_vs_size2(time_inst, size_dict, output_path):
    """
    Salva um scatter plot do tempo (mediana) vs tamanho da instância.
    """
    df = time_inst.copy()
    df["size"] = df["instance"].map(size_dict)

    # Remove instâncias sem tamanho definido
    df = df.dropna(subset=["size"])

    plt.figure()

    for alg in ["ACSi", "ACSp"]:
        subset = df[df["algorithm"] == alg]
        plt.scatter(subset["size"], subset["time"], label=alg)

    plt.xlabel("Instance size (|J| × |M|)")
    plt.ylabel("Median execution time (ms)")
    plt.xscale('log')
    plt.yscale('log')
    # plt.title("Execution time vs instance size")
    plt.legend()

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"Time vs size plot saved to: {output_path}")

def plot_speedup_per_instance(
    time_inst,
    output_path="speedup_per_instance.png",
    seq_algo="ACSi",
    par_algo="ACSp"
):
    # Load data
    df = time_inst.copy()

    # Keep only ACSi and ACSp
    df = df[df["algorithm"].isin([seq_algo, par_algo])]

    # Compute median time per instance and algorithm
    medians = (
        df.groupby(["instance", "algorithm"])["time"]
        .median()
        .unstack()
        .dropna()
    )

    # Compute speedup
    medians["speedup"] = medians[seq_algo] / medians[par_algo]

    # Sort by speedup
    medians = medians.sort_values("speedup", ascending=False)

    # Plot
    # plt.figure(figsize=(12, 5))
    # plt.bar(medians.index, medians["speedup"])
    # plt.axhline(1.0, linestyle="--")
    # plt.ylabel("Speedup")
    # plt.xlabel("Instance")
    # plt.xticks(rotation=90)
    # plt.tight_layout()

    plt.figure(figsize=(12, 5))
    plt.bar(medians.index, medians["speedup"])

    plt.axhline(1.0, linestyle="--", color="orange", linewidth=1)

    plt.ylabel("Speedup")
    plt.xlabel("Instance")

    plt.xticks(rotation=90)

    # Reduce lateral spacing
    plt.margins(x=0)
    plt.xlim(-0.5, len(medians) - 0.5)

    plt.subplots_adjust(left=0.04, right=0.99, bottom=0.28)
    plt.tight_layout()
    # Save
    plt.savefig(output_path, dpi=300)
    plt.close()

    print(f"Speedup plot saved to: {output_path}")

def plot_speedup_vs_size(
    time_inst,
    size_dict,
    output_path="speedup_vs_size.png",
    seq_algo="ACSi",
    par_algo="ACSp"
):
    df = time_inst.copy()
    df = df[df["algorithm"].isin([seq_algo, par_algo])]

    medians = (
        df.groupby(["instance", "algorithm"])["time"]
        .median()
        .unstack()
        .dropna()
    )

    medians["speedup"] = medians[seq_algo] / medians[par_algo]

    medians["size"] = medians.index.map(
        lambda inst: size_dict.get(inst)
    )


    medians = medians.dropna(subset=["size"])

    # Plot
    plt.figure(figsize=(7, 5))
    plt.scatter(medians["size"], medians["speedup"])
    plt.axhline(1.0, linestyle="--")
    plt.xlabel("Instance size (|J| × |M|)")
    plt.ylabel("Speedup (median time ratio)")
    plt.xscale('log')
    plt.tight_layout()

    plt.savefig(output_path, dpi=300)
    plt.close()

    print(f"Speedup vs size plot saved to: {output_path}")


if __name__ == "__main__":
    # time_inst = load_time_data("./paper/fattahi_brandimarte.csv")
    time_inst = load_time_data("./paper/fattahi_brandimarte_ribas.csv")

    size_dict = {
        # Brandimarte
        "MK1":  10*6,
        "MK2":  10*6,
        "MK3":  15*8,
        "MK4":  15*8,
        "MK5":  15*4,
        "MK6":  10*15,
        "MK7":  20*5,
        "MK8":  20*10,
        "MK9":  20*10,
        "MK10": 20*15,
        "MK11": 30*5,
        "MK12": 30*10,
        "MK13": 30*10,
        "MK14": 30*15,
        "MK15": 30*15,

        # Fattahi
        "SFJS1":  2*2,
        "SFJS2":  2*2,
        "SFJS3":  3*2,
        "SFJS4":  3*2,
        "SFJS5":  3*2,
        "SFJS6":  3*2,
        "SFJS7":  3*5,
        "SFJS8":  3*4,
        "SFJS9":  3*3,
        "SFJS10": 4*5,
        "MFJS1":  5*6,
        "MFJS2":  5*7,
        "MFJS3":  6*7,
        "MFJS4":  7*7,
        "MFJS5":  7*7,
        "MFJS6":  8*7,
        "MFJS7":  8*7,
        "MFJS8":  9*8,
        "MFJS9":  11*8,
        "MFJS10": 12*8,

        # Ribeiro-Suzarte
        "RBSZ1":  110 * 27,
        "RBSZ2":  155 * 40,
        "RBSZ3":  180 * 39,
        "RBSZ4":  1435 * 29,
    }

    plot_time_boxplot(time_inst, "./paper/charts/boxplot.png")
    plot_time_vs_size(time_inst, size_dict, "./paper/charts/time_vs_size.png")
    plot_speedup_per_instance(time_inst, "./paper/charts/speedup_per_instance.png")
    plot_speedup_vs_size(time_inst, size_dict, "./paper/charts/speedup_vs_size.png")