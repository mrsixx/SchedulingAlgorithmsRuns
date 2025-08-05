import numpy as np
from arch.bootstrap import IIDBootstrap

def media_geometrica(x):
    x = np.array(x)
    if len(x[x > 0]) == 0:
        return 0
    x[x == 0] = 1e-6
    return np.exp(np.mean(np.log(x)))



def bootstrap_geom_ci(data, reps=100000, ci=95):
    if np.any(data < 0):
        return np.nan, np.nan, np.nan
    data[data == 0] = 1e-6  # ou algum valor pequeno, tipo 0.0001%
    bs = IIDBootstrap(data)
    stats = bs.apply(lambda x: media_geometrica(x), reps=reps)
    lower = np.percentile(stats, (100 - ci) / 2)
    upper = np.percentile(stats, 100 - (100 - ci) / 2)
    return media_geometrica(data), lower, upper

