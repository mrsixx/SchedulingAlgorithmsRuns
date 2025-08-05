import math
import plot

OUTPUT_PATH = f"D:\\UFABC\\PGC\\runs\\charts"

#conjuntos = ['Fattahi et al.', 'Brandimarte', 'Dauzère-Pérès e Paulli', 'Hurink et al. (sdata)', 'Hurink et al. (vdata)']
if __name__ == "__main__": 
    # === Curvas gaps com intervalos de confiança ===
    gaps = {
        'LLM-FJSSP': [43.807792, 124.371046, 123.764212, 78.858572, 121.479384],
        'V0': [10.685438, 137.554552, math.nan, math.nan, math.nan],
        'V1': [33.204501, 133.936233, math.nan, math.nan, math.nan],
        'V2': [14.095290, 75.315282, 99.243343, 59.802584, 89.080749],
        'V3': [14.277543, 75.301648, 99.367952, 59.683423, 89.040037],
    }


    gaps_errors = {
        'LLM-FJSSP': [(31.898707, 59.357071), (97.892283, 159.622974), (109.030768, 139.925009), (72.405276, 85.804162), (107.091202, 137.480033)],
        'V0': [(1.491660, 37.866025), (104.215660, 186.174614), (math.nan, math.nan), (math.nan, math.nan), (math.nan, math.nan)],
        'V1': [(20.852038, 51.889559), (100.996049, 181.414697), (math.nan, math.nan), (math.nan, math.nan), (math.nan, math.nan)],
        'V2': [(8.092308, 24.704767), (54.890976, 104.750268), (89.364250, 108.991861), (52.794177, 67.532328), (78.500401, 100.833248)],
        'V3': [(8.168367, 24.797309), (55.021811, 104.555726), (89.454912, 109.283208), (52.809038, 67.258117), (78.420150, 100.861348)],
    }
    plot.plot_gaps(gaps, gaps_errors, OUTPUT_PATH)
    print('Aperte ENTER para encerrar...', end=math.nan)
    input()