
import seaborn as sns
import os
import pandas as pd
import matplotlib.pyplot as plt
from math_helpers import media_geometrica, bootstrap_geom_ci
from pypalettes import load_cmap
import math

 # Cores consistentes com os gráficos anteriores
custom_palette = {
    "LLM-FJSSP": "#ffc107",
    "V0": "#0156dd",
    "V1": "#f66000",
    "V2": "#c90007",
    "V3": "#00ff3c"
}

def get_pallete(heur):
    color_map = load_cmap("basel")
    algoritmos = [
        f'AS{heur}-i', f'AS{heur}-p',
        f'EAS{heur}-i', f'EAS{heur}-p',
        f'RBAS{heur}-i', f'RBAS{heur}-p',
        f'MMAS{heur}-i', f'MMAS{heur}-p',
        f'ACS{heur}-i', f'ACS{heur}-p', 
        'LLM-FJSSP'
    ]
    colors = [color_map(i) for i in range(10)]+['#000000']
    return dict(zip(algoritmos, colors))

def internal_plot_line_chart(
    df,
    heur: str,
    value_column: str,
    ylabel: str,
    output_path: str,
    show: bool
):
    # pivotando
    pivot = df.pivot_table(index='Instance', columns='Algorithm', values=value_column)
    pivot = pivot.reindex(
        sorted(pivot.index, key=lambda name: df[df["Instance"] == name]["InstanceSort"].values[0]))

    # Prefixos em ordem desejada
    prefix_order = ['AS', 'EAS', 'RBAS', 'MMAS', 'ACS', 'LLM']

    def sort_key(label):
        prefix = next((p for p in prefix_order if label.startswith(p)), '')
        prefix_index = prefix_order.index(prefix) if prefix in prefix_order else len(prefix_order)
        return (prefix_index, label)

    # Prepara cores e marcadores
    labels = sorted(pivot.columns, key=sort_key)

    plt.figure(figsize=(12, 6))

    for i, label in enumerate(labels):
        marker = (
            's' if label.lower().startswith('llm') else
            'd' if label.lower().endswith('i') else
            'o'
        )
        
        pallete = get_pallete(heur)
        sns.lineplot(
            x=pivot.index,
            y=pivot[label],
            label=label,
            marker=marker,
            color=pallete[label]
            #color='#000000' if label.lower().startswith('LLM') else colors[i % len(colors)]
        )
    # plt.title(title)
    plt.xlabel('Instância')
    plt.ylabel(ylabel)
    plt.xticks(rotation=45)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend(title='Implementação', loc='best')
    plt.tight_layout()
    plt.savefig(output_path)
    if show:
        manager = plt.get_current_fig_manager()
        manager.set_window_title(f"Chart {output_path} 🚀")
        plt.show(block=False)  # <- exibe sem travar a execução

def plot_line_charts(conjunto, df_all, output_dir, show=True):
    resumo = df_all.groupby(["Algorithm", "Heuristic", "Instance", "LowerBound", "InstanceSort"]).agg(
        {'Makespan': 'mean', 'Ellapsed': 'mean'}
    ).reset_index()
    llm_results = None
    for heur, grupo in resumo.groupby("Heuristic"):
        if heur == 'LLM-FJSSP':
            llm_results = grupo
            continue
        print(f"Plotando heurística {heur}")
        print(grupo)
        df_heur = pd.concat([llm_results, grupo], ignore_index=True)
        dir = f"{output_dir}/{conjunto}"
        os.makedirs(dir, exist_ok=True)
        internal_plot_line_chart(df_heur, heur, "Makespan", 'Makespan', f'{dir}/{conjunto}_{heur}_makespan.png', show)
        internal_plot_line_chart(df_heur, heur, "Ellapsed", 'Tempo de CPU (ms)', f'{dir}/{conjunto}_{heur}_cputime.png', show)

def plot_kde_cputime(conjunto, df_all, output_dir, show=True):
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f'kde_cputime{conjunto}.png')
    # === Calcula a média por algoritmo-instância ===
    resumo = df_all.groupby(["Algorithm", "Heuristic", "Instance"]).agg(
        {'Ellapsed': 'mean'}
    ).reset_index()
    print(resumo)
    
    plt.figure(figsize=(10, 6))

    # Paleta com uma cor por heurística
    palette = sns.color_palette("Set2", n_colors=resumo["Algorithm"].nunique())
    # Loop por heurísticas e cores
    #for i, (heuristica, cor) in enumerate(zip(resumo["Algorithm"].nunique(), palette)):
    for i, (alg, grupo) in enumerate(resumo[resumo["Heuristic"] == "V2"].groupby("Algorithm")):
        if alg.endswith('i'):
            continue
        
        sns.kdeplot(
            data=grupo,
            x="Ellapsed",
            fill=True,
            alpha=0.2,
            label=alg,
            color=palette[i],
            #hue_order=["V0", "V1", "V3", "V2", "LLM-FJSSP"],
            #hue="Algorithm",
            #palette=palette
        )
        
        # Valor da média geométrica (ajustado aqui!)
        #valor_medio = resumo[resumo["Heuristic"] == heuristica]["media_geom_gap"].values[0]
        #plt.axvline(valor_medio, color=custom_palette[heuristica], linestyle="--", linewidth=2, alpha=0.6)

    plt.xlabel("Gap (%)")
    plt.ylabel("Densidade")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    if show:
        manager = plt.get_current_fig_manager()
        manager.set_window_title(f"Chart {output_path} 🚀")
        plt.show(block=False)  # <- exibe sem travar a execução

# Esta função plota a densidade de probabilidade (KDE) dos gaps por heurística,
# calculando a média geométrica dos gaps e seus intervalos de confiança, e salva o gráfico no diretório especificado.
# Os gaps são calculados como a diferença percentual entre o makespan médio e o lower bound
def plot_kde(conjunto, df, output_dir, show=True):
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f'kde_{conjunto}.png')
    # === Calcula a media por algoritmo-instancia ===
    resumo = df.groupby(["Heuristic", "Instance", "LowerBound"]).agg(
        Makespan=('Makespan', 'mean'),
        Ellapsed=('Ellapsed', 'mean'),
        Samples=('Makespan', 'count')
    ).reset_index()

    # === Cálculo do gap baseado na média do makespan ===
    resumo["gap"] = 100 * (resumo["Makespan"] - resumo["LowerBound"]) / resumo["LowerBound"]
    
    # === Resumo por heurística ===
    resultados = []
    for heur, grupo in resumo.groupby("Heuristic"):
        gaps = grupo["gap"].values
        
        #print(heur, grupo["gap"], len(gaps))
        media_geom, ic_min, ic_max = bootstrap_geom_ci(gaps)
        resultados.append({
            "Heuristic": heur,
            "media_geom_gap": media_geom,
            "IC_min": ic_min,
            "IC_max": ic_max,
            "n_Instances": len(gaps),
            "n_Samples": sum(grupo["Samples"].values)
        })
    #
    df_compiled = pd.DataFrame(resultados)
    print(f"\nGaps de {conjunto} por heurística:")
    print(df_compiled)

    plt.figure(figsize=(10, 6))

    # Loop por heurísticas e cores
    for i, heuristica in enumerate(df_compiled["Heuristic"]):
        sns.kdeplot(
            data=resumo[resumo["Heuristic"] == heuristica],
            x="gap",
            fill=True,
            alpha=0.2,
            label=heuristica,
            hue_order=["V0", "V1", "V3", "V2", "LLM-FJSSP"],
            hue="Heuristic",
            palette=custom_palette
        )
        
        # Valor da média geométrica (ajustado aqui!)
        valor_medio = df_compiled[df_compiled["Heuristic"] == heuristica]["media_geom_gap"].values[0]
        plt.axvline(valor_medio, color=custom_palette[heuristica], linestyle="--", linewidth=2, alpha=0.6)

    plt.xlabel("Gap (%)")
    plt.ylabel("Densidade")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    if show:
        manager = plt.get_current_fig_manager()
        manager.set_window_title(f"Chart {output_path} 🚀")
        plt.show(block=False)  # exibe sem travar a execução

import matplotlib.pyplot as plt

def plot_gaps(
    gaps: dict[str, list[float]],
    gap_ic: dict[str, list[tuple[float, float]]],  # (inferior, superior) percentis
    output_path: str
):
    conjuntos = ['Fattahi et al.', 'Brandimarte', 'Dauzère-Pérès e Paulli', 'Hurink et al. (sdata)', 'Hurink et al. (vdata)']
    algoritmos = ['V0', 'V1', 'V2', 'V3', 'LLM-FJSSP']

    marcadores = {
        'V0': '*',
        'V1': 'x',
        'V2': 'd',
        'V3': '.',
        'LLM-FJSSP': 's',
    }


    plt.figure(figsize=(10, 6))

    for alg in algoritmos:
        y = gaps[alg]
        ic = gap_ic[alg]  # lista de tuplas (inferior, superior)

        # separa os deltas inferior e superior
        erro_inferior = []
        erro_superior = []
        for m, (ic_inf, ic_sup) in zip(y, ic):
            if (
                m is None or ic_inf is None or ic_sup is None or
                math.isnan(m) or math.isnan(ic_inf) or math.isnan(ic_sup)
            ):
                erro_inferior.append(math.nan)
                erro_superior.append(math.nan)
            else:
                erro_inferior.append(m - ic_inf)
                erro_superior.append(ic_sup - m)

        plt.errorbar(
            conjuntos,
            y,
            yerr=[erro_inferior, erro_superior],
            label=alg,
            color=custom_palette[alg],
            marker=marcadores[alg],
            linestyle='-' if alg.lower().startswith('v2') else '--',
            markersize=8,
            capsize=4
        )

    plt.ylabel('Gap médio (%)')
    plt.xticks(rotation=45)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend(title='Heurística', loc='best')
    plt.tight_layout()
    plt.savefig(f'{output_path}\\gaps.png', dpi=300)
    plt.show()
