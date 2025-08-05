import os
import re
import pandas as pd
import bounds

def get_bounds(name):
    if name == '6_Fattahi':
        return bounds.FATTAHI_BOUNDS
    if name == '1_Brandimarte':
        return bounds.BRANDIMARTE_BOUNDS
    if name == '3_DPpaulli':
        return bounds.DP_BOUNDS
    if name == '2a_Hurink_sdata':
        return bounds.HURINKSDATA_BOUNDS
    if name == '2d_Hurink_vdata':
        return bounds.HURINKVDATA_BOUNDS
    # if name == 'ribeiro':
    #     return ribeiro_rename

    return {}

def replace_fn_factory(name):
    if name == '6_Fattahi':
        return fattahi_rename
    if name == '1_Brandimarte':
        return brandimarte_rename
    # if name == 'ribeiro':
    #     return ribeiro_rename
    if name == '3_DPpaulli':
        return paulli_rename
    if name == '2a_Hurink_sdata':
        return lawrence_rename
    if name == '2d_Hurink_vdata':
        return lawrence_rename

    def identity(n):
        return n
    
    return identity


def lawrence_rename(name):
    num = int(''.join(filter(str.isdigit, name)))
    return f"la{num-3}" if num-3 > 9 else f"la0{num-3}"


def fattahi_rename(name):
    num = int(''.join(filter(str.isdigit, name)))
    if num <= 10:
        return f"SFJS{num}"
    return f"MFJS{num-10}"
    
def brandimarte_rename(name):
    num = int(''.join(filter(str.isdigit, name)))
    return f"MK{num}"

def paulli_rename(name):
    num = int(''.join(filter(str.isdigit, name)))
    return f"DP{num}a"

# === FUNÇÃO PARA EXTRair INFO DO NOME DO ARQUIVO ===
# === EXTRAI INFO DO NOME DO ARQUIVO ===
def extrair_info(nome_arquivo):
    nome = os.path.splitext(nome_arquivo)[0]  # tira .csv
    instancia, resto = nome.split(".fjs.")
    partes = resto.split("-")
    conjunto = partes[0]  # ex: Fattahi
    algoritmo_nome = "-".join(partes[1:])  # ex: Fattahi-ACSV1-iterative
    
    #tratando nomes
    if algoritmo_nome == "greedy-iterative":
        algoritmo_nome = "LLM-FJSSP"
    else:
        algoritmo_nome = algoritmo_nome.replace("iterative", "i")
        algoritmo_nome = algoritmo_nome.replace("parallel", "p")


    replacer = replace_fn_factory(conjunto)
    sort = num = int(''.join(filter(str.isdigit, instancia)))
    instancia = replacer(instancia)
    # Heurística vem de algo tipo "ACSV1", "MMASV2" etc.
    heuristica_match = re.search(r'V[0-9]+', algoritmo_nome)
    heuristica = heuristica_match.group(0) if heuristica_match else "LLM-FJSSP"

    return instancia, algoritmo_nome, heuristica, conjunto,sort



def read_instances(path):
    # === CARREGAR TODOS OS CSVs ===
    registros = []
    arquivos = os.listdir(path)
    read_counter = 0
    print(f"{len(arquivos)} founded in {path}")
    for arquivo in os.listdir(path):
        if arquivo.endswith(".csv"):
            caminho = os.path.join(path, arquivo)
            instancia, algoritmo, heuristica, conjunto, sort = extrair_info(arquivo)
            bounds = get_bounds(conjunto)
            df = pd.read_csv(caminho)
            df.rename(columns={"Ellapsed(ms)": "Ellapsed"}, inplace=True)
            df["Algorithm"] = algoritmo
            df["InstanceSort"] = sort
            df["Heuristic"] = heuristica
            df["Instance"] = instancia
            read_counter = read_counter + 1
            df["LowerBound"] = df["Instance"].map(bounds)
            registros.append(df)
    
    print(f"{read_counter} files compiled")
    df_all = pd.concat(registros, ignore_index=True)

    # === Adiciona o LB correspondente à instância ===
    #df_all["LowerBound"] = df_all["Instance"].map(LOWER_BOUNDS)
    return df_all