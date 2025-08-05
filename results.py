# pip install pandas numpy arch matplotlib seaborn pypalettes
import sys
from compiler import read_instances
import plot
# === Bootstrap com média geométrica ===

# === CONFIGURAÇÕES ===
CONJUNTO = sys.argv[1]
INPUT_PATH = f"D:\\UFABC\\PGC\\runs\\data\\{CONJUNTO}"  # Substitua pelo caminho correto
OUTPUT_PATH = f"D:\\UFABC\\PGC\\runs\\charts\\{CONJUNTO}"  # Substitua pelo caminho correto

if __name__ == "__main__":
    df_all = read_instances(INPUT_PATH)
    
    # === KDE por heurística ===
    plot.plot_kde(CONJUNTO, df_all, OUTPUT_PATH, True)

    # === Curvas makespan e cpu time por algoritmo de cada heuristica ===
    #plot.plot_line_charts(CONJUNTO, df_all, OUTPUT_PATH, False)

    # print('Aperte ENTER para encerrar...', end=None)
    input()