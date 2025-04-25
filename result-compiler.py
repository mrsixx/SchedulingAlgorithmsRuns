import os
import re
import sys
import shutil
from itertools import groupby
import pandas as pd


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