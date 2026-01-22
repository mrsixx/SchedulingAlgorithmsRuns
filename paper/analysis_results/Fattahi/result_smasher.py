import pandas as pd
import os
import re
from pathlib import Path

def extract_instance_name(filename):
    """
    Extrai o nome da instância do nome do arquivo.
    Fattahi1-10 -> SFJS1-10
    Fattahi11-20 -> MFJS1-10
    """
    match = re.search(r'Fattahi(\d+)', filename)
    if match:
        num = int(match.group(1))
        if 1 <= num <= 10:
            return f'SFJS{num}'
        elif 11 <= num <= 20:
            return f'MFJS{num - 10}'
    return None

def extract_algorithm(filename):
    """
    Extrai o algoritmo do nome do arquivo.
    ACSV2-iterative -> ACSi
    ACSV2-parallel -> ACSp
    greedy-iterative -> ECT
    """
    if 'ACSV2-iterative' in filename:
        return 'ACSi'
    elif 'ACSV2-parallel' in filename:
        return 'ACSp'
    elif 'greedy-iterative' in filename:
        return 'ECT'
    return None

def consolidate_results(input_dir, output_file):
    """
    Consolida todos os arquivos CSV em um único arquivo.
    """
    all_results = []
    
    # Listar todos os arquivos CSV no diretório
    csv_files = sorted(Path(input_dir).glob('*.csv'))
    
    for csv_file in csv_files:
        filename = csv_file.name
        
        # Extrair instance e algorithm do nome do arquivo
        instance = extract_instance_name(filename)
        algorithm = extract_algorithm(filename)
        
        if instance is None or algorithm is None:
            print(f'Pulando arquivo: {filename} (não corresponde ao padrão esperado)')
            continue
        
        # Ler o arquivo CSV
        try:
            df = pd.read_csv(csv_file)
            
            # Processar cada linha (run)
            for run_number, row in enumerate(df.itertuples(index=False), start=1):
                print(row)
                all_results.append({
                    'instance': instance,
                    'algorithm': algorithm,
                    'run': run_number,
                    'makespan': row.Makespan,
                    'time': row._1
                })
        except Exception as e:
            print(f'Erro ao processar {filename}: {e}')
    
    # Criar DataFrame consolidado
    consolidated_df = pd.DataFrame(all_results)
    
    # Salvar arquivo consolidado
    consolidated_df.to_csv(output_file, index=False)
    print(f'Arquivo consolidado salvo em: {output_file}')
    print(f'Total de registros: {len(consolidated_df)}')

if __name__ == '__main__':
    # Configurar diretórios
    input_directory = './paper/brute-data/Fattahi'
    output_filepath = './paper/fattahi.csv'
    
    # Criar diretório de saída se não existir
    os.makedirs(os.path.dirname(output_filepath), exist_ok=True)
    
    # Executar consolidação
    consolidate_results(input_directory, output_filepath)