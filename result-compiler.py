import os
import re
import sys
import shutil
from itertools import groupby
import pandas as pd
import matplotlib.pyplot as plt

# def plot_makespan_and_cpu(df, output_dir='/'):
#     df['Solver-Approach'] = df['Solver'] + '-' + df['Approach']
#     instance_name = df['Instance'].iloc[0]
#     safe_instance = instance_name.replace(" ", "_").replace("/", "_")  # Nome do arquivo seguro

#     bar_width = 0.2
#     x = range(len(df))
    
#     # Cálculo dos erros (diferença entre média e extremos)
#     makespan_avg = df['Makespan (avg)']
#     makespan_err_lower = makespan_avg - df['Makespan (min)']
#     makespan_err_upper = df['Makespan (max)'] - makespan_avg
#     makespan_errors = [makespan_err_lower, makespan_err_upper]

#     # Adiciona valores acima das barras
#     for i, bar in enumerate(bars):
#         height = bar.get_height()
#         plt.text(bar.get_x() + bar.get_width() / 2, height + 1, f'{height:.1f}', ha='center', va='bottom', fontsize=9)

#     # Gráfico de Makespan
#     plt.figure(figsize=(12, 6))
#     plt.bar(x, makespan_avg, yerr=makespan_errors, capsize=5, color='skyblue')
#     plt.xticks(x, df['Solver-Approach'], rotation=45, ha='right')
#     plt.ylabel('Makespan')
#     plt.title(f'{instance_name} - Makespan')
#     plt.legend()
#     plt.tight_layout()
#     plt.savefig(f'{safe_instance}_makespan.png')
#     plt.close()


#     cpu_avg = df['CPU TIME(ms) (avg)']
#     cpu_err_lower = cpu_avg - df['CPU TIME(ms) (min)']
#     cpu_err_upper = df['CPU TIME(ms) (max)'] - cpu_avg
#     cpu_errors = [cpu_err_lower, cpu_err_upper]

#     # Gráfico de CPU TIME
#     plt.figure(figsize=(12, 6))
#     plt.bar(x, cpu_avg, yerr=cpu_errors, capsize=5, color='salmon')
#     plt.xticks(x, df['Solver-Approach'], rotation=45, ha='right')
#     plt.ylabel('CPU TIME (ms)')
#     plt.title(f'{instance_name} - CPU TIME')
#     plt.legend()
#     plt.tight_layout()
#     plt.savefig(f'{safe_instance}_cpu_time.png')
#     plt.close()


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

def plot_charts(df, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    df['Solver + Approach'] = df['Solver'] + '-' + df['Approach']

    for instance_name, df_instance in df.groupby('Instance'):
        safe_instance = instance_name.replace(" ", "_").replace("/", "_")
        
        makespan_path = os.path.join(output_dir, f'{safe_instance}_makespan_chart.png')
        plot_metric_with_errorbars(
            df_instance,
            metric_prefix='Makespan',
            color='#998ec3',
            output_path=makespan_path,
            title=f'{instance_name} - Makespan (hrs)',
            #transform=lambda x: x / 3600,
            x_order=[
                'ASV2-iterative', 'ASV2-parallel','EASV2-iterative', 'EASV2-parallel', 
                'RBASV2-iterative', 'RBASV2-parallel', 'MMASV2-iterative', 'MMASV2-parallel', 
                'ACSV2-iterative', 'ACSV2-parallel', 'greedy-iterative']
        )
        
        cpu_path = os.path.join(output_dir, f'{safe_instance}_cputime_chart.png')
        plot_metric_with_errorbars(
            df_instance,
            metric_prefix='CPU TIME(ms)',
            color='#f1a340',
            output_path=cpu_path,
            title=f'{instance_name} - CPU TIME',
            x_order=[
                'ASV2-iterative', 'ASV2-parallel','EASV2-iterative', 'EASV2-parallel', 
                'RBASV2-iterative', 'RBASV2-parallel', 'MMASV2-iterative', 'MMASV2-parallel', 
                'ACSV2-iterative', 'ACSV2-parallel', 'greedy-iterative']
        )

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


if __name__ == "__main__":
    if(len(sys.argv) <= 1):
        raise Exception("Diretório com resultados é obrigatório")

    results_dir = f'/workspaces/SchedulingAlgorithmsRuns/{sys.argv[1]}'
    arquivos = listar_arquivos(results_dir, '.csv')

    for benchmark, g in groupby(sorted(arquivos, key=lambda x: x['benchmark']), key=lambda x: x['benchmark']):
        arquivos_benchmark = list(g)
        print(f'{len(arquivos_benchmark)} arquivos no benchmark {benchmark}\n\n')
        benchmark_data = extrair_metricas(arquivos_benchmark)
        #mover_arquivos_lixeira(arquivos_benchmark, lixeira_dir)
        benchmark_data.to_csv(f'{benchmark}.csv', index=False, sep=';', decimal=',', float_format='%.2f')
        plot_charts(benchmark_data, results_dir)