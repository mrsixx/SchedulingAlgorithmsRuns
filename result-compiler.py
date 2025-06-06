import os
import re
import sys
import shutil
from itertools import groupby
import pandas as pd
import matplotlib.pyplot as plt
from pypalettes import load_cmap

def gaps(
    output_path: str,
):
    # Dados fictícios: substitua pelos seus reais
    conjuntos = ['Fattahi et al.', 'Brandimarte', 'Dauzère-Pérès e Paulli', 'Hurink et al. (sdata)', 'Hurink et al. (vdata)']
    algoritmos = ['V0', 'V1', 'V2', 'V3', 'LLM-FJSSP']

    # Cada linha representa os valores de gap percentual médio para um algoritmo em cada conjunto
    gaps = {
        'V0': [59.26, 164.87, None, None, None],
        'V1': [53.07, 160.74, None, None, None],
        'V2': [28.51, 93.08, 101.43, 64.38, 96.29],
        'V3': [28.78, 92.89, 101.58, 64.16, 96.31],
        'LLM-FJSSP': [67.96, 215.11, 235.26, 171.38, 218.99],
    }

    marcadores = {
    'V0': '^',
    'V1': 'D',
    'V2': 'd',
    'V3': '.',
    'LLM-FJSSP': 's',
}

    # Cores consistentes com os gráficos anteriores
    cores = {
        'V0': '#1f77b4',     # azul escuro
        'V1': '#2ca02c',     # verde
        'V2': '#ff7f0e',     # laranja
        'V3': '#bcbd22',    # verde oliva
        'LLM-FJSSP': 'black'
    }
    color_map = load_cmap("basel")
    colors = [color_map(i) for i in range(4)]

    plt.figure(figsize=(10, 6))

    for i, alg in enumerate(algoritmos):
        plt.plot(
            conjuntos,
            gaps[alg],
            label=alg,
            color='#000000' if alg.lower().startswith('llm') else colors[i % len(colors)],
            marker= marcadores[alg],
            #linewidth=5 if alg.lower().startswith('v2') else 2,
            linestyle='-.' if alg.lower().startswith('v2') else '--',
            markersize=8
        )


    #plt.ylim(bottom=0)
    
    # plt.title(title)
    plt.ylabel('Gap médio (%)')
    plt.xticks(rotation=45)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend(title='Heurística', loc='best')
    plt.tight_layout()
    plt.savefig(output_path)
    plt.show()


def lawrence_rename(pivot):
    rename_map = {}
    for name in pivot.index:
        num = int(''.join(filter(str.isdigit, name)))
        rename_map[name] = f"la{num-3}" if num-3 > 9 else f"la0{num-3}"

    return rename_map

def fattahi_rename(pivot):
    rename_map = {}
    sfjs_counter = 1
    mfjs_counter = 1
    for name in pivot.index:
        num = int(''.join(filter(str.isdigit, name)))
        if num <= 10:
            rename_map[name] = f"SFJS{sfjs_counter}"
            sfjs_counter += 1
        else:
            rename_map[name] = f"MFJS{mfjs_counter}"
            mfjs_counter += 1
    
    return rename_map

def brandimarte_rename(pivot):
    rename_map = {}
    for name in pivot.index:
        num = int(''.join(filter(str.isdigit, name)))
        rename_map[name] = f"MK{num}"
    
    return rename_map

def paulli_rename(pivot):
    rename_map = {}
    for name in pivot.index:
        num = int(''.join(filter(str.isdigit, name)))
        rename_map[name] = f"DP{num}a"
    
    return rename_map

def ribeiro_rename(pivot):
    rename_map = {}
    for name in pivot.index:
        num = int(''.join(filter(str.isdigit, name)))
        rename_map[name] = f"ECALC{num}"
    
    return rename_map

def plot_line_chart(
    df,
    value_column: str,
    title: str,
    ylabel: str,
    output_path: str,
    rename_fn,
    transform=lambda x: x,
):
    # Cria a coluna combinada se não existir
    if 'Solver + Approach' not in df.columns:
        df['Solver + Approach'] = df['Solver'] + ' + ' + df['Approach']

    # Pivota
    pivot = df.pivot_table(index='Instance', columns='Solver + Approach', values=value_column)

    # Ordena instâncias numericamente
    pivot = pivot.reindex(
        sorted(pivot.index, key=lambda name: int(''.join(filter(str.isdigit, name))))
    )

    # Cria o mapeamento após a ordenação
    rename_map = rename_fn(pivot)

    # Aplica o novo rótulo ao eixo X
    pivot.index = pivot.index.map(rename_map)


    # Prefixos em ordem desejada
    prefix_order = ['AS', 'EAS', 'RBAS', 'MMAS', 'ACS', 'greedy']

    def sort_key(label):
        prefix = next((p for p in prefix_order if label.startswith(p)), '')
        prefix_index = prefix_order.index(prefix) if prefix in prefix_order else len(prefix_order)
        return (prefix_index, label)

    # Prepara cores e marcadores
    labels = sorted(pivot.columns, key=sort_key)

    #labels = sorted(pivot.columns)  # ordena legenda
    color_map = load_cmap("basel")
    #colors = [color_map(i) for i in range(10)]
    colors = [color_map(i) for i in [5,7,8,9]]

    plt.figure(figsize=(12, 6))

    for i, label in enumerate(labels):
        marker = (
            's' if label.lower().startswith('greedy') else
            'd' if label.lower().endswith('iterative') else
            'o'
        )

        replaced_label = (
            'LLM-FJSSP' if label.lower().startswith('greedy') else
            label.replace("iterative", "i") if label.lower().endswith('iterative') else
            label.replace("parallel", "p")
        )

        plt.plot(
            pivot.index,
            pivot[label].map(transform),
            label=replaced_label,
            marker=marker,
            color= '#000000' if label.lower().startswith('greedy') else colors[i % len(colors)]
        )

    # plt.title(title)
    plt.xlabel('Instância')
    plt.ylabel(ylabel)
    plt.xticks(rotation=45)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend(title='Implementação', loc='best')
    plt.tight_layout()
    plt.savefig(output_path)
    plt.show()


def plot_metric_with_errorbars(
    df,
    metric_prefix, 
    color, 
    output_path, 
    title, 
    transform=lambda x: x,
    x_order=None
):
    """
    Gera gráfico de barras com barras de erro (min/max) em torno da média.

    :param df: DataFrame com colunas no formato '<metric_prefix> (min)', '(avg)', '(max)'
    :param metric_prefix: Nome base da métrica, ex: 'Makespan' ou 'CPU TIME(ms)'
    :param color: Cor das barras
    :param output_path: Caminho do arquivo de saída (.png)
    :param title: Título do gráfico
    """

    # Ordena pela ordem definida pelo usuário (se houver)
    if x_order is not None:
        df['Solver + Approach'] = pd.Categorical(df['Solver + Approach'], categories=x_order, ordered=True)
        df = df.sort_values(by='Solver + Approach')
    else:
        df = df.sort_values(by='Solver + Approach')

    x = range(len(df))
    avg_col = f'{metric_prefix} (avg)'
    min_col = f'{metric_prefix} (min)'
    max_col = f'{metric_prefix} (max)'
    
    avg = transform(df[avg_col])
    err_lower = transform(df[avg_col] - df[min_col])
    err_upper = transform(df[max_col] - df[avg_col])
    errors = [err_lower, err_upper]

    plt.figure(figsize=(12, 6))
    bars = plt.bar(x, avg, yerr=errors, capsize=5, color=color)
    plt.xticks(x, df['Solver + Approach'], rotation=45, ha='right')
    plt.ylabel(metric_prefix)
    plt.title(title)

    for i, bar in enumerate(bars):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, (height/4) + 1, f'{height:,.2f}'.replace(",", "X").replace(".", ",").replace("X", "."), 
                 ha='center', va='bottom', fontsize=9)

    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

def plot_charts(df, output_dir, files_base_name, rename_fn, transform_fn):
    os.makedirs(output_dir, exist_ok=True)
    df['Solver + Approach'] = df['Solver'] + '-' + df['Approach']
    #plot_line_chart_by_solver(df, f'{output_dir}/{files_base_name}')
    #plot_line_chart(df, 'Makespan (avg)', 'Makespan médio por instância e por implementação', 'Makespan', f'{output_dir}/{files_base_name}_makespan', rename_fn,transform_fn)
    #plot_line_chart(df, 'CPU TIME(ms) (avg)', 'Tempo médio de CPU por instância e por implementação', 'Tempo de CPU (ms)', f'{output_dir}/{files_base_name}_cputime', rename_fn)

    for instance_name, df_instance in df.groupby('Instance'):
        safe_instance = f'{files_base_name}_{instance_name.replace(" ", "_").replace("/", "_")}'
        
        makespan_path = os.path.join(output_dir, f'{safe_instance}_makespan_chart.png')
        # plot_metric_with_errorbars(
        #     df_instance,
        #     metric_prefix='Makespan',
        #     color='#998ec3',
        #     output_path=makespan_path,
        #     title=f'{instance_name} - Makespan (hrs)',
        #     transform=lambda x: x / 3600,
        #     # x_order=[
        #     #     'ASV2-iterative', 'ASV2-parallel','EASV2-iterative', 'EASV2-parallel', 
        #     #     'RBASV2-iterative', 'RBASV2-parallel', 'MMASV2-iterative', 'MMASV2-parallel', 
        #     #     'ACSV2-iterative', 'ACSV2-parallel', 'greedy-iterative']
        #     # x_order=['greedy-iterative',
        #     #     'ASV1-iterative', 'ASV1-parallel',
        #     #     'ASV2-iterative', 'ASV2-parallel'
        #     #     'ASV3-iterative', 'ASV3-parallel']
        # )
        plot_bars_with_style(
            df_instance,
            metric_prefix='Makespan',
            output_path=makespan_path,
            title=f'{instance_name} - Makespan (hrs)',
            transform=lambda x: x / 3600,
        )

        cpu_path = os.path.join(output_dir, f'{safe_instance}_cputime_chart.png')
        plot_bars_with_style(
            df_instance,
            metric_prefix='CPU TIME(ms)',
            output_path=cpu_path,
            title=f'{instance_name} - CPU TIME',
        )
        # plot_metric_with_errorbars(
        #     df_instance,
        #     metric_prefix='CPU TIME(ms)',
        #     color='#f1a340',
        #     output_path=cpu_path,
        #     title=f'{instance_name} - CPU TIME',
        #     # x_order=[
        #     #     'ASV2-iterative', 'ASV2-parallel','EASV2-iterative', 'EASV2-parallel', 
        #     #     'RBASV2-iterative', 'RBASV2-parallel', 'MMASV2-iterative', 'MMASV2-parallel', 
        #     #     'ACSV2-iterative', 'ACSV2-parallel', 'greedy-iterative']
        #     # x_order=['greedy-iterative',
        #     #     'ASV1-iterative', 'ASV1-parallel',
        #     #     'ASV2-iterative', 'ASV2-parallel'
        #     #     'ASV3-iterative', 'ASV3-parallel']
        # )


def plot_bars_with_style(
    df,
    metric_prefix,
    output_path,
    title,
    transform=lambda x: x,
    x_order=None
):
    """
    Gera gráfico de barras com erro, com estética consistente com plot_line_chart.
    """

    # Aplica ordenação se fornecida
    if x_order is not None:
        df['Solver + Approach'] = pd.Categorical(df['Solver + Approach'], categories=x_order, ordered=True)
        df = df.sort_values(by='Solver + Approach')
    else:
        df['Solver + Approach'] = df['Solver'] + '-' + df['Approach']

        # Ordenação com base no prefixo
        prefix_order = ['AS', 'EAS', 'RBAS', 'MMAS', 'ACS', 'greedy']
        def sort_key(label):
            prefix = next((p for p in prefix_order if label.startswith(p)), '')
            prefix_index = prefix_order.index(prefix) if prefix in prefix_order else len(prefix_order)
            return (prefix_index, label)

        df = df.sort_values(by='Solver + Approach', key=lambda col: col.map(sort_key))

    # Define colunas da métrica
    avg_col = f'{metric_prefix} (avg)'
    min_col = f'{metric_prefix} (min)'
    max_col = f'{metric_prefix} (max)'

    # Valores transformados
    avg = transform(df[avg_col])
    err_lower = transform(df[avg_col] - df[min_col])
    err_upper = transform(df[max_col] - df[avg_col])
    errors = [err_lower, err_upper]

    # Estética
    color_map = load_cmap("basel")
    colors = [color_map(i) for i in range(10)]

    labels = df['Solver + Approach'].tolist()

    # Renomeia os rótulos conforme regras
    def rename_label(label):
        if label.lower().startswith('greedy'):
            return 'LLM-FJSSP'
        if label.lower().endswith('iterative'):
            return label.replace('iterative', 'i')
        return label.replace('parallel', 'p')

    renamed_labels = [rename_label(l) for l in labels]

    plt.figure(figsize=(12, 6))
    x = range(len(df))
    error_kw = dict(
        capsize=5,
        capthick=1,
        ecolor='black',     # cor da barra de erro
        alpha=0.3,           # opacidade da barra de erro (0 = invisível, 1 = opaco)
    )

    bars = plt.bar(
        x,
        avg,
        yerr=errors,
        capsize=5,
        error_kw=error_kw,
        color=[
            '#000000' if 'greedy' in l.lower() else colors[i % len(colors)]
            for i, l in enumerate(labels)
        ], alpha=0.7
    )
    plt.xticks(x, renamed_labels, rotation=45, ha='right')
    plt.ylabel(metric_prefix)
    #if 'makespan' in output_path:
    if False:
        current_makespan = None
        if 'ribeiro1' in output_path.lower():
            current_makespan = transform(167077843)
        elif 'ribeiro2' in output_path.lower():
            current_makespan = transform(4118161888)
        else:#ribeiro3
            current_makespan = transform(6758432125)
            
        plt.axhline(
            y=current_makespan,                 # valor no eixo y onde a linha será traçada
            color='red',           # cor da linha
            linestyle='--',        # linha tracejada (ou '-' para linha contínua)
            linewidth=1.5,         # espessura da linha
            label='Referência'      # para incluir na legenda
        )
    #plt.title(title)

    for i, bar in enumerate(bars):
        height = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            (height / 4) + 1,
            f'{height:,.2f}'.replace(",", "X").replace(".", ",").replace("X", "."),
            ha='center',
            va='bottom',
            fontsize=9,
            color='#ffffff' if renamed_labels[i].lower().startswith('llm') and 'makespan' in output_path else '#000000'
        )

    plt.grid(True, linestyle='--', alpha=0.2)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def listar_arquivos(dir, extensao):
    arquivos = []
    for root, dirs, files in os.walk(dir):
        for arquivo in files:
            if arquivo.endswith(extensao):
                filepath = os.path.join(root, arquivo)
                match = re.search(r"^(?P<filename>[^\.]+)\.fjs\.(?P<benchmark>[^-]+)-(?P<solver>[^-]+)-(?P<approach>[^\.]+)\.csv$", arquivo)
                if match is None: 
                    break

                file_obj = {
                    'path': filepath,
                    'filename': arquivo,
                    'solver': match.group("solver"),
                    'approach': match.group("approach"),
                    'benchmark': match.group("benchmark"),
                    'instance': match.group("filename")
                }

                arquivos.append(file_obj)
    return arquivos


def extrair_metricas(arquivos):
    instance, approach, solver = [], [], []
    min_makespan, mean_makespan, max_makespan = [], [], []
    min_cpu_time, mean_cpu_time, max_cpu_time = [], [], []
    std_makespan, std_cpu_time = [], []

    for arquivo in sorted(arquivos, key=lambda x: x['instance'], reverse=False):
        # Ler o arquivo CSV
        tabela = pd.read_csv(arquivo['path'])

        # Extrair dados dos valores do arquivo
        instance.append(arquivo['instance'])
        solver.append(arquivo['solver'])
        approach.append(arquivo['approach'])
        min_makespan.append(tabela['Makespan'].min()) 
        mean_makespan.append(tabela['Makespan'].mean()) 
        max_makespan.append(tabela['Makespan'].max())
        std_makespan.append(tabela['Makespan'].std())

        min_cpu_time.append(tabela['Ellapsed(ms)'].min())
        mean_cpu_time.append(tabela['Ellapsed(ms)'].mean())
        max_cpu_time.append(tabela['Ellapsed(ms)'].max())
        std_cpu_time.append(tabela['Ellapsed(ms)'].std())

    return pd.DataFrame({
        'Instance': instance,
        'Approach': approach,
        'Solver': solver,
        'Makespan (min)': min_makespan,
        'Makespan (avg)': mean_makespan,
        'Makespan (max)': max_makespan,
        'Makespan (std)': std_makespan,
        'CPU TIME(ms) (min)': min_cpu_time,
        'CPU TIME(ms) (avg)': mean_cpu_time,
        'CPU TIME(ms) (max)': max_cpu_time,
        'CPU TIME(ms) (std)': std_cpu_time,
    }) 

def mover_arquivos_lixeira(arquivos, lixeira_dir):
    for arquivo in arquivos:
        new_file = f'{lixeira_dir}//{arquivo['filename']}.old'
        os.makedirs(os.path.dirname(new_file), exist_ok=True)
        shutil.move(arquivo['path'], new_file)


def replace_fn_factory(name):
    identity_transform = lambda x: x
    hour_transform = lambda x: x / 3600
    if name == 'fattahi':
        return fattahi_rename,identity_transform
    if name == 'brandimarte':
        return brandimarte_rename,identity_transform
    if name == 'ribeiro':
        return ribeiro_rename,hour_transform
    if name == 'paulli':
        return paulli_rename, identity_transform
    if name == 'lawrence':
        return lawrence_rename, identity_transform

    def identity(pivot):
        rename_map = {}
        for name in pivot.index:
            rename_map[name] = name
        return rename_map
    
    return identity,identity_transform

if __name__ == "a__main__":
    gaps('/workspaces/SchedulingAlgorithmsRuns/gaps.png')
    sys.exit()


if __name__ == "__main__":
    if(len(sys.argv) <= 3):
        raise Exception("Diretório com resultados é obrigatório")
    
    file = sys.argv[1]
    file_base_name = sys.argv[2]

    replace_fn,transform_fn = replace_fn_factory(sys.argv[3])
    results_dir = f'/workspaces/SchedulingAlgorithmsRuns/{file}'
    arquivos = listar_arquivos(results_dir, '.csv')
    output_dir = f'{results_dir}/output'
    os.makedirs(output_dir, exist_ok=True)
    for benchmark, g in groupby(sorted(arquivos, key=lambda x: x['benchmark']), key=lambda x: x['benchmark']):
        arquivos_benchmark = list(g)
        print(f'{len(arquivos_benchmark)} arquivos no benchmark {benchmark}\n\n')
        benchmark_data = extrair_metricas(arquivos_benchmark)
        #mover_arquivos_lixeira(arquivos_benchmark, lixeira_dir)
        benchmark_data.to_csv(os.path.join(output_dir, f'{file_base_name}.csv'), index=False, sep=';', decimal=',', float_format='%.2f')
        plot_charts(benchmark_data, output_dir, file_base_name, replace_fn,transform_fn)
    
    print(f'resultados salvos em {output_dir}')