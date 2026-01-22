#pip install pandas numpy scipy matplotlib seaborn

"""
Script para análise estatística de resultados do FJSSP comparando:
- ACSi: Ant Colony System sequencial
- ACSp: Ant Colony System paralelo
- ECT: Heurística de despacho ECT

Autor: [Seu Nome]
Data: [Data]
"""

import pandas as pd
import numpy as np
import scipy.stats as stats
from scipy.stats import friedmanchisquare, rankdata, wilcoxon, ttest_rel
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import rcParams
from itertools import combinations
import warnings
warnings.filterwarnings('ignore')

# Configuração para gráficos de qualidade para artigos
plt.style.use('seaborn-v0_8-whitegrid')
# rcParams.update({
#     'font.family': 'serif',
#     'font.serif': ['Times New Roman', 'Computer Modern Roman'],
#     'font.size': 11,
#     'axes.titlesize': 12,
#     'axes.labelsize': 11,
#     'legend.fontsize': 10,
#     'xtick.labelsize': 10,
#     'ytick.labelsize': 10,
#     'figure.dpi': 300,
#     'savefig.dpi': 300,
#     'savefig.bbox': 'tight',
#     'savefig.pad_inches': 0.1
# })

# APÓS AS IMPORTS, ADICIONE:
INSTANCE_ORDER = [
    # Fattahi - ordem clássica
    'SFJS1', 'SFJS2', 'SFJS3', 'SFJS4', 'SFJS5',
    'SFJS6', 'SFJS7', 'SFJS8', 'SFJS9', 'SFJS10',
    'MFJS1', 'MFJS2', 'MFJS3', 'MFJS4', 'MFJS5',
    'MFJS6', 'MFJS7', 'MFJS8', 'MFJS9', 'MFJS10',
    
    # Brandimarte - ordem clássica
    'MK01', 'MK02', 'MK03', 'MK04', 'MK05', 
    'MK06', 'MK07', 'MK08', 'MK09', 'MK10',
    # Kacem - do menor para maior
    '4x5', '8x8', '10x10', '15x10',
    # Dauzère-Pérès
    'DP01', 'DP02', 'DP03', 'DP04', 'DP05',
    # Barnes
    'MT06', 'MT10', 'MT20',
    # FFdata
    'FF1', 'FF2', 'FF3', 'FF4', 'FF5', 'FF6', 'FF7', 'FF8', 'FF9', 'FF10',
    # LA (Lawrence)
    'la01', 'la02', 'la03', 'la04', 'la05', 'la06', 'la07', 'la08', 'la09', 'la10',
    'la11', 'la12', 'la13', 'la14', 'la15', 'la16', 'la17', 'la18', 'la19', 'la20',
    'la21', 'la22', 'la23', 'la24', 'la25', 'la26', 'la27', 'la28', 'la29', 'la30',
    'la31', 'la32', 'la33', 'la34', 'la35', 'la36', 'la37', 'la38', 'la39', 'la40'
]

# ============================================================================
# 0. FUNÇÕES AUXILIARES
# ============================================================================

def sort_instances_custom(instances):
    """
    Ordena um array de instâncias de acordo com a ordem definida em INSTANCE_ORDER.
    Instâncias não encontradas em INSTANCE_ORDER são adicionadas no final.
    """
    instances_list = list(instances)
    
    # Separar instâncias em encontradas e não encontradas
    found = []
    not_found = []
    
    for instance in INSTANCE_ORDER:
        if instance in instances_list:
            found.append(instance)
    
    for instance in instances_list:
        if instance not in found:
            not_found.append(instance)
    
    # Retornar instâncias ordenadas
    return np.array(found + sorted(not_found))


# ============================================================================
# 1. FUNÇÕES PARA LEITURA E PREPARAÇÃO DOS DADOS
# ============================================================================

def load_and_prepare_data(filepath):
    """
    Carrega o arquivo CSV e prepara os dados para análise.
    
    Espera um CSV com colunas como:
    - instance: nome da instância (ex: MK01, MK02)
    - algorithm: ACSi, ACSp, ou ECT
    - run: número da execução (1 a 30)
    - makespan: valor do makespan obtido
    - time: tempo de execução em segundos
    """
    print("Carregando dados...")
    df = pd.read_csv(filepath)
    
    # Verificar colunas necessárias
    required_cols = ['instance', 'algorithm', 'run', 'makespan', 'time']
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Coluna '{col}' não encontrada no arquivo CSV")
    
    # Verificar algoritmos esperados
    expected_algs = ['ACSi', 'ACSp', 'ECT']
    actual_algs = df['algorithm'].unique()
    for alg in expected_algs:
        if alg not in actual_algs:
            print(f"Aviso: Algoritmo '{alg}' não encontrado nos dados")
    
    print(f"Dados carregados: {len(df)} registros")
    print(f"Instâncias: {df['instance'].nunique()}")
    print(f"Algoritmos: {list(df['algorithm'].unique())}")
    
    return df


def create_summary_tables(df):
    """
    Cria tabelas sumárias por instância e por algoritmo.
    """
    # Tabela por instância e algoritmo
    summary = df.groupby(['instance', 'algorithm']).agg({
        'makespan': ['mean', 'std', 'min', 'max'],
        'time': ['mean', 'std']
    }).round(2)
    
    # Renomear colunas
    summary.columns = ['makespan_mean', 'makespan_std', 
                      'makespan_min', 'makespan_max',
                      'time_mean', 'time_std']
    
    # Resetar índice para facilitar manipulação
    summary = summary.reset_index()
    
    # Ordenar por INSTANCE_ORDER
    instance_order = sort_instances_custom(summary['instance'].unique())
    instance_order_dict = {inst: i for i, inst in enumerate(instance_order)}
    summary['instance_sort_key'] = summary['instance'].map(instance_order_dict)
    summary = summary.sort_values('instance_sort_key').drop('instance_sort_key', axis=1)
    summary = summary.reset_index(drop=True)
    
    return summary


# ============================================================================
# 2. ANÁLISES ESTATÍSTICAS NÃO PARAMÉTRICAS
# ============================================================================

def calculate_friedman_test(df):
    """
    Realiza o teste de Friedman para comparar os 3 algoritmos em todas as instâncias.
    
    Retorna:
    - Estatística do teste
    - p-valor
    - Ranks médios por algoritmo
    """
    
    algorithms = ['ACSi', 'ACSp', 'ECT']
    instances = sort_instances_custom(df['instance'].unique())
    
    # Preparar matriz para teste de Friedman (instâncias x algoritmos)
    # Cada célula contém a média do makespan para aquela instância-algoritmo
    friedman_data = []
    
    for instance in instances:
        instance_data = []
        for alg in algorithms:
            # Filtrar dados para instância e algoritmo
            alg_data = df[(df['instance'] == instance) & (df['algorithm'] == alg)]
            if len(alg_data) > 0:
                # Usar a média das 30 execuções
                instance_data.append(alg_data['makespan'].mean())
            else:
                instance_data.append(np.nan)
        friedman_data.append(instance_data)
    
    # Converter para array numpy
    friedman_array = np.array(friedman_data)
    
    # Remover linhas com valores faltantes (se houver)
    valid_rows = ~np.any(np.isnan(friedman_array), axis=1)
    friedman_array = friedman_array[valid_rows]
    
    # Realizar teste de Friedman
    stat, p_value = friedmanchisquare(*friedman_array.T)
    
    # Calcular ranks médios
    # Para cada instância, rankear os algoritmos (1=melhor makespan)
    ranks = []
    for row in friedman_array:
        ranks.append(rankdata(row))
    
    ranks = np.array(ranks)
    avg_ranks = np.mean(ranks, axis=0)
    
    # Criar dicionário com ranks médios
    rank_dict = {alg: avg_ranks[i] for i, alg in enumerate(algorithms)}
    
    return {
        'statistic': stat,
        'p_value': p_value,
        'avg_ranks': rank_dict,
        'ranks_matrix': ranks
    }


def calculate_wilcoxon_holm(df, alpha=0.05):
    """
    Realiza testes de Wilcoxon signed-rank com correção de Holm para todas as instâncias.
    
    Retorna uma matriz com p-valores corrigidos para todas as comparações pareadas.
    """
    algorithms = ['ACSi', 'ACSp', 'ECT']
    instances = sort_instances_custom(df['instance'].unique())
    
    # Preparar dados: para cada instância, temos 30 makespans por algoritmo
    data_dict = {}
    for alg in algorithms:
        alg_data = {}
        for instance in instances:
            instance_data = df[(df['instance'] == instance) & 
                              (df['algorithm'] == alg)]['makespan'].values
            if len(instance_data) > 0:
                alg_data[instance] = instance_data
        data_dict[alg] = alg_data
    
    # Para cada instância, realizar testes pareados
    wilcoxon_results = {}
    
    for instance in instances:
        # Verificar se temos dados para todos os algoritmos nesta instância
        has_all_data = all(instance in data_dict[alg] for alg in algorithms)
        if not has_all_data:
            continue
        
        # Obter dados para os 3 algoritmos
        data_acsi = data_dict['ACSi'][instance]
        data_acsp = data_dict['ACSp'][instance]
        data_ect = data_dict['ECT'][instance]
        
        # Testes pareados
        p_values = []
        comparisons = []
        
        # ACSi vs ACSp
        stat, p = wilcoxon(data_acsi, data_acsp)
        p_values.append(p)
        comparisons.append('ACSi vs ACSp')
        
        # ACSi vs ECT
        stat, p = wilcoxon(data_acsi, data_ect)
        p_values.append(p)
        comparisons.append('ACSi vs ECT')
        
        # ACSp vs ECT
        stat, p = wilcoxon(data_acsp, data_ect)
        p_values.append(p)
        comparisons.append('ACSp vs ECT')
        
        # Aplicar correção de Holm
        # Ordenar p-valores do menor para o maior
        sorted_indices = np.argsort(p_values)
        sorted_p = [p_values[i] for i in sorted_indices]
        sorted_comparisons = [comparisons[i] for i in sorted_indices]
        
        # Aplicar correção
        m = len(p_values)
        holm_p = []
        for k, p_val in enumerate(sorted_p):
            holm_p.append(min(p_val * (m - k), 1.0))
        
        # Armazenar resultados
        wilcoxon_results[instance] = {
            'comparisons': sorted_comparisons,
            'p_values': sorted_p,
            'holm_p': holm_p
        }
    
    return wilcoxon_results


# ============================================================================
# 3. CÁLCULO DE MÉTRICAS DE DESEMPENHO
# ============================================================================

def calculate_performance_metrics(df, reference_values=None):
    """
    Calcula métricas de desempenho como gap, speedup, etc.
    
    reference_values: dicionário com {instance: (LB, UB)} se disponível
    """
    algorithms = ['ACSi', 'ACSp', 'ECT']
    instances = sort_instances_custom(df['instance'].unique())
    
    results = []
    
    for instance in instances:
        for alg in algorithms:
            alg_data = df[(df['instance'] == instance) & 
                         (df['algorithm'] == alg)]
            
            if len(alg_data) == 0:
                continue
            
            # Métricas básicas
            makespan_mean = alg_data['makespan'].mean()
            makespan_std = alg_data['makespan'].std()
            time_mean = alg_data['time'].mean()
            time_std = alg_data['time'].std()
            
            # Calcular gap se tiver valores de referência
            gap = None
            if reference_values and instance in reference_values:
                lb, ub = reference_values[instance]
                if lb is not None:
                    gap = ((makespan_mean - lb) / lb) * 100
            
            results.append({
                'instance': instance,
                'algorithm': alg,
                'makespan_mean': makespan_mean,
                'makespan_std': makespan_std,
                'makespan_min': alg_data['makespan'].min(),
                'makespan_max': alg_data['makespan'].max(),
                'time_mean': time_mean,
                'time_std': time_std,
                'gap_percent': gap
            })
    
    results_df = pd.DataFrame(results)
    
    # Calcular speedup do ACSp em relação ao ACSi
    speedup_data = []
    for instance in instances:
        # Tempo do ACSi
        time_acsi = results_df[(results_df['instance'] == instance) & 
                              (results_df['algorithm'] == 'ACSi')]['time_mean']
        # Tempo do ACSp
        time_acsp = results_df[(results_df['instance'] == instance) & 
                              (results_df['algorithm'] == 'ACSp')]['time_mean']
        
        if len(time_acsi) > 0 and len(time_acsp) > 0:
            speedup = float(time_acsi.iloc[0] / time_acsp.iloc[0])
            speedup_data.append({'instance': instance, 'speedup': speedup})
    
    speedup_df = pd.DataFrame(speedup_data)
    
    return results_df, speedup_df


def calculate_confidence_intervals(df, n_bootstrap=5000, confidence=0.95):
    """
    Calcula intervalos de confiança usando bootstrapping (método não paramétrico).
    """
    algorithms = df['algorithm'].unique()
    instances = sort_instances_custom(df['instance'].unique())
    
    bootstrap_results = []
    
    for instance in instances:
        for alg in algorithms:
            alg_data = df[(df['instance'] == instance) & 
                         (df['algorithm'] == alg)]['makespan'].values
            
            if len(alg_data) == 0:
                continue
            
            # Bootstrapping
            bootstrap_means = []
            for _ in range(n_bootstrap):
                sample = np.random.choice(alg_data, size=len(alg_data), replace=True)
                bootstrap_means.append(np.mean(sample))
            
            # Calcular percentis
            lower_perc = (1 - confidence) / 2 * 100
            upper_perc = (1 + confidence) / 2 * 100
            
            ci_lower = np.percentile(bootstrap_means, lower_perc)
            ci_upper = np.percentile(bootstrap_means, upper_perc)
            mean_val = np.mean(alg_data)
            
            bootstrap_results.append({
                'instance': instance,
                'algorithm': alg,
                'mean': mean_val,
                'ci_lower': ci_lower,
                'ci_upper': ci_upper,
                'ci_width': ci_upper - ci_lower
            })
    
    return pd.DataFrame(bootstrap_results)


# ============================================================================
# 4. VISUALIZAÇÕES
# ============================================================================

def plot_critical_difference(friedman_results, title="Critical Difference Diagram"):
    """
    Cria um gráfico Critical Difference (CD) a partir dos resultados do teste de Friedman.
    
    Adaptado do conceito de Demsar (2006).
    """
    avg_ranks = friedman_results['avg_ranks']
    k = len(avg_ranks)  # Número de algoritmos
    N = friedman_results['ranks_matrix'].shape[0]  # Número de instâncias
    
    # Ordenar algoritmos por rank médio (do melhor para o pior)
    sorted_algs = sorted(avg_ranks.items(), key=lambda x: x[1])
    algs = [alg for alg, _ in sorted_algs]
    ranks = [rank for _, rank in sorted_algs]
    
    # Calcular Critical Difference (CD) usando fórmula de Nemenyi
    # CD = q_alpha * sqrt(k*(k+1)/(6*N))
    # q_alpha para alpha=0.05 pode ser aproximado
    # Valores críticos para teste de Nemenyi (alpha=0.05)
    # k=2: 1.96, k=3: 2.343, k=4: 2.569, k=5: 2.728
    q_alpha_dict = {2: 1.96, 3: 2.343, 4: 2.569, 5: 2.728, 6: 2.850}
    q_alpha = q_alpha_dict.get(k, 2.343)  # Padrão para k=3
    
    CD = q_alpha * np.sqrt(k * (k + 1) / (6 * N))
    
    # Criar figura
    fig, ax = plt.subplots(figsize=(10, 4))
    
    # Plotar ranks
    y_pos = np.arange(len(algs))
    ax.barh(y_pos, ranks, color='steelblue', alpha=0.7)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(algs, fontweight='bold')
    ax.set_xlabel('Average Rank (lower is better)')
    ax.set_title(title)
    
    # Adicionar valores de rank nas barras
    for i, rank in enumerate(ranks):
        ax.text(rank + 0.05, i, f'{rank:.3f}', va='center', fontweight='bold')
    
    # Adicionar linha e anotação da Critical Difference
    ax.axvline(x=ranks[0] + CD, color='red', linestyle='--', alpha=0.7)
    ax.text(ranks[0] + CD/2, len(algs)-0.5, f'CD = {CD:.3f}', 
            color='red', ha='center', fontweight='bold', 
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
    
    # Conectar algoritmos que não são estatisticamente diferentes
    # (aqueles cuja diferença de rank é menor que CD)
    for i in range(len(algs)):
        for j in range(i+1, len(algs)):
            if ranks[j] - ranks[i] < CD:
                # Desenhar linha conectando
                y_positions = [i, j]
                x_position = max(ranks[i], ranks[j]) + 0.1
                ax.plot([x_position, x_position], y_positions, 
                       'k-', linewidth=2, alpha=0.7)
    
    plt.tight_layout()
    return fig


def plot_performance_comparison(metrics_df, instance_list=None):
    """
    Plota gráfico de barras comparando makespan médio e tempo de execução.
    """
    if instance_list is None:
        # Selecionar algumas instâncias representativas
        all_instances = metrics_df['instance'].unique()
        all_instances = sort_instances_custom(all_instances)  # <-- ADICIONE ESTA LINHA
        # Selecionar pequena, média e grande
        instance_list = all_instances[:min(3, len(all_instances))]
    
    n_instances = len(instance_list)
    
    # Criar subplots apropriadamente
    if n_instances > 1:
        fig, axes = plt.subplots(n_instances, 2, figsize=(12, 4*n_instances))
    else:
        # Para uma única instância, axes será um array 1D
        fig, axes = plt.subplots(1, 2, figsize=(12, 4))
        axes = axes.reshape(1, -1)  # Garantir que seja 2D
    
    for idx, instance in enumerate(instance_list):
        instance_data = metrics_df[metrics_df['instance'] == instance]
        
        # Subplot 1: Makespan
        if n_instances > 1:
            ax1 = axes[idx, 0]
            ax2 = axes[idx, 1]
        else:
            ax1 = axes[0, 0]
            ax2 = axes[0, 1]

        algorithms = instance_data['algorithm'].values
        makespan_means = instance_data['makespan_mean'].values
        makespan_stds = instance_data['makespan_std'].values
        
        x_pos = np.arange(len(algorithms))
        bars = ax1.bar(x_pos, makespan_means, yerr=makespan_stds, 
                      capsize=5, alpha=0.7, color=['#1f77b4', '#ff7f0e', '#2ca02c'])
        
        ax1.set_xlabel('Algorithm')
        ax1.set_ylabel('Makespan')
        ax1.set_title(f'Instance {instance} - Makespan Comparison')
        ax1.set_xticks(x_pos)
        ax1.set_xticklabels(algorithms)
        
        # Adicionar valores nas barras
        for bar, mean_val in zip(bars, makespan_means):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 0.02*height,
                    f'{mean_val:.1f}', ha='center', va='bottom')
        
        # Subplot 2: Tempo de execução
        if len(instance_list) > 1:
            ax2 = axes[idx, 1]
        else:
            ax2 = axes[0, 1]  # Para única instância, axes é 2D devido ao squeeze=False
        
        time_means = instance_data['time_mean'].values
        time_stds = instance_data['time_std'].values
        
        bars2 = ax2.bar(x_pos, time_means, yerr=time_stds, 
                       capsize=5, alpha=0.7, color=['#1f77b4', '#ff7f0e', '#2ca02c'])
        
        ax2.set_xlabel('Algorithm')
        ax2.set_ylabel('Time (ms)')
        ax2.set_title(f'Instance {instance} - Time Comparison')
        ax2.set_xticks(x_pos)
        ax2.set_xticklabels(algorithms)
        
        # Adicionar valores nas barras
        for bar, mean_val in zip(bars2, time_means):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + 0.02*height,
                    f'{mean_val:.1f}s', ha='center', va='bottom')
    
    plt.tight_layout()
    return fig


def plot_speedup_analysis(speedup_df, metrics_df):
    """
    Plota análise de speedup do ACSp em relação ao ACSi.
    """
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    # Subplot 1: Speedup por instância - ordenado por INSTANCE_ORDER
    # Primeiro, ordenar dataframe por INSTANCE_ORDER
    instance_order = sort_instances_custom(speedup_df['instance'].unique())
    instance_order_dict = {inst: i for i, inst in enumerate(instance_order)}
    speedup_df_ordered = speedup_df.copy()
    speedup_df_ordered['instance_sort_key'] = speedup_df_ordered['instance'].map(instance_order_dict)
    speedup_df_ordered = speedup_df_ordered.sort_values('instance_sort_key')
    
    instances = speedup_df_ordered['instance'].values
    speedups = speedup_df_ordered['speedup'].values
    
    # Manter ordem de INSTANCE_ORDER (não reordenar por speedup)
    sorted_instances = instances
    sorted_speedups = speedups
    
    bars = axes[0].bar(range(len(sorted_instances)), sorted_speedups, 
                      color=np.where(sorted_speedups >= 1, 'green', 'red'), alpha=0.7)
    
    axes[0].axhline(y=1, color='k', linestyle='--', alpha=0.5)
    axes[0].set_xlabel('Instances (sorted by speedup)')
    axes[0].set_ylabel('Speedup (ACSi / ACSp)')
    axes[0].set_title('Speedup Analysis')
    axes[0].set_xticks(range(len(sorted_instances)))
    axes[0].set_xticklabels(sorted_instances, rotation=45, ha='right')
    
    # Adicionar valores nas barras
    for bar, speedup in zip(bars, sorted_speedups):
        height = bar.get_height()
        axes[0].text(bar.get_x() + bar.get_width()/2., height + 0.02,
                    f'{speedup:.2f}x', ha='center', va='bottom', fontsize=8)
    
    # Subplot 2: Speedup vs. Tempo do ACSi (tamanho do problema)
    # Obter tempo médio do ACSi para cada instância
    acsi_times = []
    for instance in sorted_instances:
        time_val = metrics_df[(metrics_df['instance'] == instance) & 
                             (metrics_df['algorithm'] == 'ACSi')]['time_mean'].values
        if len(time_val) > 0:
            acsi_times.append(time_val[0])
        else:
            acsi_times.append(np.nan)
    
    axes[1].scatter(acsi_times, sorted_speedups, s=100, alpha=0.7)
    axes[1].axhline(y=1, color='k', linestyle='--', alpha=0.5)
    axes[1].set_xlabel('ACSi Execution Time (ms)')
    axes[1].set_ylabel('Speedup')
    axes[1].set_title('Speedup vs. Problem Size')
    
    # Adicionar rótulos para alguns pontos
    for i, instance in enumerate(sorted_instances):
        if i % max(1, len(sorted_instances)//5) == 0:  # Rotular ~5 pontos
            axes[1].annotate(instance, (acsi_times[i], sorted_speedups[i]), 
                           xytext=(5, 5), textcoords='offset points')
    
    # Adicionar linha de tendência
    if len(acsi_times) > 2:
        valid_idx = ~np.isnan(acsi_times) & ~np.isnan(sorted_speedups)
        if np.sum(valid_idx) > 2:
            z = np.polyfit(np.array(acsi_times)[valid_idx], 
                          np.array(sorted_speedups)[valid_idx], 1)
            p = np.poly1d(z)
            x_range = np.linspace(min(acsi_times), max(acsi_times), 100)
            axes[1].plot(x_range, p(x_range), "r--", alpha=0.5, 
                        label=f'Trend: y={z[0]:.3f}x+{z[1]:.3f}')
            axes[1].legend()
    
    plt.tight_layout()
    return fig


def plot_convergence_analysis(df, instance, max_iterations=100):
    """
    Plota análise de convergência para uma instância específica.
    (Assumindo que você tem dados de convergência por iteração)
    """
    # Esta função assume que você tem dados de convergência
    # Se não tiver, pode ser adaptada ou removida
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Exemplo simplificado - você precisaria adaptar para seus dados reais
    algorithms = ['ACSi', 'ACSp']
    colors = {'ACSi': '#1f77b4', 'ACSp': '#ff7f0e'}
    
    for alg in algorithms:
        # Filtrar dados para a instância e algoritmo
        alg_data = df[(df['instance'] == instance) & (df['algorithm'] == alg)]
        
        if len(alg_data) == 0:
            continue
        
        # Aqui você precisaria ter dados por iteração
        # Por enquanto, é apenas um placeholder
        ax.plot([1, max_iterations], 
                [alg_data['makespan'].mean(), alg_data['makespan'].mean()],
                label=alg, color=colors[alg], linewidth=2)
    
    ax.set_xlabel('Iteration')
    ax.set_ylabel('Best Makespan')
    ax.set_title(f'Convergence Analysis - Instance {instance}')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    return fig


# ============================================================================
# 5. FUNÇÃO PRINCIPAL E EXPORTAÇÃO DE RESULTADOS
# ============================================================================

def analyze_results(csv_filepath, output_dir='./results', reference_values=None):
    """
    Função principal que coordena toda a análise.
    """
    import os
    import json
    
    # Criar diretório de saída se não existir
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Carregar dados
    df = load_and_prepare_data(csv_filepath)
    
    # 2. Criar tabelas sumárias
    print("\nCriando tabelas sumárias...")
    summary_tables = create_summary_tables(df)
    
    # Salvar tabelas sumárias
    summary_tables.to_csv(f'{output_dir}/summary_tables.csv', index=False)
    print(f"Tabelas sumárias salvas em {output_dir}/summary_tables.csv")
    
    # 3. Análises estatísticas
    print("\nRealizando análises estatísticas...")
    
    # Teste de Friedman
    friedman_results = calculate_friedman_test(df)
    print(f"Teste de Friedman:")
    print(f"  Estatística: {friedman_results['statistic']:.4f}")
    print(f"  p-valor: {friedman_results['p_value']:.6f}")
    print(f"  Ranks médios: {friedman_results['avg_ranks']}")
    
    # Teste de Wilcoxon com correção de Holm
    wilcoxon_results = calculate_wilcoxon_holm(df)
    
    # 4. Calcular métricas de desempenho
    print("\nCalculando métricas de desempenho...")
    metrics_df, speedup_df = calculate_performance_metrics(df, reference_values)
    
    # Salvar métricas
    metrics_df.to_csv(f'{output_dir}/performance_metrics.csv', index=False)
    speedup_df.to_csv(f'{output_dir}/speedup_analysis.csv', index=False)
    
    # 5. Intervalos de confiança por bootstrapping
    print("\nCalculando intervalos de confiança por bootstrapping...")
    ci_df = calculate_confidence_intervals(df)
    ci_df.to_csv(f'{output_dir}/confidence_intervals.csv', index=False)
    
    # 6. Gerar visualizações
    print("\nGerando visualizações...")
    
    # Gráfico Critical Difference
    cd_fig = plot_critical_difference(friedman_results)
    cd_fig.savefig(f'{output_dir}/critical_difference.png')
    
    # Gráfico de comparação de desempenho
    perf_fig = plot_performance_comparison(metrics_df)
    if perf_fig is not None:
        perf_fig.savefig(f'{output_dir}/performance_comparison.png')
        plt.close(perf_fig)  # Fechar a figura para liberar memória
    else:
        print("Aviso: Não foi possível criar gráfico de performance")
    
    # Gráfico de speedup
    if not speedup_df.empty:
        speedup_fig = plot_speedup_analysis(speedup_df, metrics_df)
        speedup_fig.savefig(f'{output_dir}/speedup_analysis.png')
    
    # 7. Gerar relatório em LaTeX (opcional)
    print("\nGerando relatório em LaTeX...")
    generate_latex_report(friedman_results, metrics_df, speedup_df, 
                         wilcoxon_results, output_dir)
    
    # 8. Salvar resultados em JSON para referência
    results_dict = {
        'friedman_test': {
            'statistic': float(friedman_results['statistic']),
            'p_value': float(friedman_results['p_value']),
            'avg_ranks': friedman_results['avg_ranks']
        },
        'summary_stats': {
            'n_instances': df['instance'].nunique(),
            'n_runs': df['run'].nunique(),
            'algorithms': list(df['algorithm'].unique())
        }
    }
    
    with open(f'{output_dir}/analysis_results.json', 'w') as f:
        json.dump(results_dict, f, indent=4)
    
    print(f"\nAnálise concluída! Resultados salvos em: {output_dir}")
    
    return {
        'data': df,
        'friedman': friedman_results,
        'wilcoxon': wilcoxon_results,
        'metrics': metrics_df,
        'speedup': speedup_df,
        'confidence_intervals': ci_df
    }


def generate_latex_report(friedman_results, metrics_df, speedup_df, 
                         wilcoxon_results, output_dir):
    """
    Gera um relatório em LaTeX com os principais resultados.
    """
    # Extrair valores para usar em f-strings
    friedman_stat = friedman_results['statistic']
    friedman_p = friedman_results['p_value']
    reject_text = "rejecting" if friedman_p < 0.05 else "not rejecting"
    
    latex_content = """\\documentclass[10pt]{article}
\\usepackage{booktabs}
\\usepackage{multirow}
\\usepackage{graphicx}
\\usepackage{float}
\\usepackage{siunitx}
\\usepackage[hmargin=2.5cm,vmargin=2.5cm]{geometry}

\\title{Statistical Analysis Results for FJSSP Algorithms}
\\author{}
\\date{\\today}

\\begin{document}

\\maketitle

\\section*{Statistical Summary}

\\section{Friedman Test Results}
\\begin{table}[H]
\\centering
\\caption{Average ranks from Friedman test (lower is better)}
\\label{tab:friedman}
\\begin{tabular}{lc}
\\toprule
Algorithm & Average Rank \\\\
\\midrule
"""
    
    for alg, rank in friedman_results['avg_ranks'].items():
        latex_content += f"{alg} & {rank:.3f} \\\\\n"
    
    latex_content += f"""\\bottomrule
\\end{{tabular}}
\\end{{table}}

The Friedman test resulted in a statistic of $\\chi^2 = {friedman_stat:.4f}$ with a p-value of {friedman_p:.6f}, {reject_text} the null hypothesis that all algorithms perform equally.

\\section{{Performance Metrics Summary}}
\\begin{{table}}[H]
\\centering
\\caption{{Summary of performance metrics (mean ± standard deviation)}}
\\label{{tab:metrics}}
\\begin{{tabular}}{{lcccc}}
\\toprule
Instance & Algorithm & Makespan & Time (ms) & Gap (\\%) \\\\
\\midrule
"""
    
    # Agrupar por instância para formato mais legível
    instances = sort_instances_custom(metrics_df['instance'].unique())[:5]  # Mostrar apenas 5 primeiras
    for instance in instances:
        instance_data = metrics_df[metrics_df['instance'] == instance]
        first_row = True
        
        for _, row in instance_data.iterrows():
            if first_row:
                latex_content += f"\\multirow{{3}}{{*}}{{{instance}}} & "
                first_row = False
            else:
                latex_content += " & "
            
            latex_content += f"{row['algorithm']} & "
            latex_content += f"{row['makespan_mean']:.1f} ± {row['makespan_std']:.1f} & "
            latex_content += f"{row['time_mean']:.1f} ± {row['time_std']:.1f} & "
            
            if pd.notnull(row['gap_percent']):
                latex_content += f"{row['gap_percent']:.2f} \\\\\n"
            else:
                latex_content += "-- \\\\\n"
        
        latex_content += "\\midrule\n"
    
    latex_content += """\\bottomrule
\\end{tabular}
\\end{table}
"""

    # Adicionar análise de speedup
    if not speedup_df.empty:
        # Ordenar speedup_df por INSTANCE_ORDER
        instance_order = sort_instances_custom(speedup_df['instance'].unique())
        instance_order_dict = {inst: i for i, inst in enumerate(instance_order)}
        speedup_df_ordered = speedup_df.copy()
        speedup_df_ordered['instance_sort_key'] = speedup_df_ordered['instance'].map(instance_order_dict)
        speedup_df_ordered = speedup_df_ordered.sort_values('instance_sort_key')
        
        avg_speedup = speedup_df_ordered['speedup'].mean()
        latex_content += """
\\section{Speedup Analysis}
\\begin{table}[H]
\\centering
\\caption{Speedup of ACSp relative to ACSi}
\\label{tab:speedup}
\\begin{tabular}{lc}
\\toprule
Instance & Speedup (ACSi/ACSp) \\\\
\\midrule
"""
        
        for _, row in speedup_df_ordered.iterrows():
            latex_content += f"{row['instance']} & {row['speedup']:.2f}x \\\\\n"
        
        latex_content += f"""\\midrule
Average & {avg_speedup:.2f}x \\\\
\\bottomrule
\\end{{tabular}}
\\end{{table}}
"""

    # Adicionar referência às figuras
    latex_content += """
\\section{Graphical Analysis}
The following figures provide visual analysis of the results:

\\begin{figure}[H]
\\centering
\\includegraphics[width=0.9\\textwidth]{critical_difference.png}
\\caption{Critical Difference diagram showing statistical comparison of algorithms}
\\label{fig:cd}
\\end{figure}

\\begin{figure}[H]
\\centering
\\includegraphics[width=0.9\\textwidth]{performance_comparison.png}
\\caption{Comparison of makespan and execution time for selected instances}
\\label{fig:perf}
\\end{figure}
"""
    
    if not speedup_df.empty:
        latex_content += """
\\begin{figure}[H]
\\centering
\\includegraphics[width=0.9\\textwidth]{speedup_analysis.png}
\\caption{Speedup analysis of parallel implementation}
\\label{fig:speedup}
\\end{figure}
"""
    
    latex_content += """
\\end{document}
"""
    
    # Salvar arquivo LaTeX
    with open(f'{output_dir}/report.tex', 'w') as f:
        f.write(latex_content)
    
    print(f"Relatório LaTeX salvo em {output_dir}/report.tex")

# ============================================================================
# 6. EXEMPLO DE USO
# ============================================================================

if __name__ == "__main__":
    """
    Exemplo de como usar o script.
    """
    
    # Exemplo 1: Análise básica
    csv_path = "./paper/fattahi.csv"  # Substitua pelo caminho real
    
    # Valores de referência (Lower Bound/Upper Bound) - opcional
    # Pode ser um dicionário: {'MK01': (LB, UB), 'MK02': (LB, UB), ...}
    reference_values = {
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
    
    try:
        results = analyze_results(csv_path, output_dir='./paper/analysis_results/FattahiSort', 
                                 reference_values=reference_values)
        
        # Exibir alguns resultados no terminal
        print("\n" + "="*60)
        print("RESUMO DOS RESULTADOS")
        print("="*60)
        
        print(f"\nTeste de Friedman:")
        print(f"  p-valor: {results['friedman']['p_value']:.6f}")
        if results['friedman']['p_value'] < 0.05:
            print("  → Diferença estatisticamente significativa entre algoritmos")
        else:
            print("  → Nenhuma diferença estatisticamente significativa")
        
        print("\nRanks médios (1=melhor, 3=pior):")
        for alg, rank in results['friedman']['avg_ranks'].items():
            print(f"  {alg}: {rank:.3f}")
        
        if 'speedup' in results and not results['speedup'].empty:
            print(f"\nSpeedup médio (ACSp vs ACSi): {results['speedup']['speedup'].mean():.2f}x")
        
    except FileNotFoundError:
        print(f"Erro: Arquivo '{csv_path}' não encontrado.")
        print("\nExemplo de estrutura do CSV esperada:")
        print("instance,algorithm,run,makespan,time")
        print("MK01,ACSi,1,45,120.5")
        print("MK01,ACSi,2,46,118.3")
        print("MK01,ACSp,1,44,40.2")
        print("...")