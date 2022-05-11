import numpy as np
import pandas as pd
from tabulate import tabulate
import matplotlib.pyplot as plt

def kelvin(temperature):
    return temperature + 273

def celsius(temperature):
    return temperature - 273

def interpolate(p1, p2, x):
    return p1[1] + (x-p1[0])*(p2[1]-p1[1])/(p2[0]-p1[0])

def getValues(table, variable, value):
    if value in table[variable].values:
        return table.loc[table[variable] == value] 
    else:
        previousIndex = table[table[variable] < value].index[-1]
        out = []
        for col in table.columns:
            if col != variable:
                p1 = [table[table.index == previousIndex][variable].values[0],
                      table[table.index == previousIndex][col].values[0]]
                p2 = [table[table.index == previousIndex + 1][variable].values[0],
                      table[table.index == previousIndex + 1][col].values[0]]
                out.append(interpolate(p1, p2, value))
            else:
                out.append(value)
        return pd.DataFrame(np.array([out]), columns=table.columns)

def simulacao(table_a22, a, b, c, d, e):
    # Dados fixos
    fluxo_ar_compressor = 14.16             # [kg/s]
    pci_gas_natural = 50010                 # [kJ/kg]
    relacao_pressao_compressao = 10.7

    # Dados variaveis
    perda_carga_combustao = a               # [%]
    temperatura_maxima = kelvin(b)       # [K]
    n_isentropica_compressor = c
    n_isentropica_expansao = d
    rendimento_eletromecanico = e

    # Compressor
    compressor_in = {}
    compressor_in["T"] = kelvin(15)                                    # [K]
    compressor_in["p"] = 100                                           # [kPa]
    interpolated = getValues(table_a22, "T", compressor_in["T"])
    compressor_in["h"] = interpolated["h"].values[0]                   # [kJ/kg]
    compressor_in["pr"] = interpolated["pr"].values[0]

    compressor_out = {}
    compressor_out["pr"] = compressor_in["pr"] * relacao_pressao_compressao
    compressor_out["p"] = compressor_in["p"] * relacao_pressao_compressao
    interpolated = getValues(table_a22, "pr", compressor_out["pr"])
    compressor_out["h"] = interpolated["h"].values[0]
    compressor_out["T"] = interpolated["T"].values[0]
    compressor_out["h_real"] = ((compressor_out["h"] - compressor_in["h"])/n_isentropica_compressor) + compressor_in["h"]
    interpolated = getValues(table_a22, "h", compressor_out["h_real"])
    compressor_out["t_real"] = interpolated["T"].values[0]

    potencia_compressor = fluxo_ar_compressor*(compressor_out["h_real"] - compressor_in["h"])

    # Câmara de combustão
    camara_out = {}
    camara_out["T"] = temperatura_maxima
    interpolated = getValues(table_a22, "T", camara_out["T"])
    camara_out["pr"] = interpolated["pr"].values[0]
    camara_out["h"] = interpolated["h"].values[0]
    camara_out["p"] = (1 - perda_carga_combustao/100)*compressor_out["p"]
    camara_out["mc"] = fluxo_ar_compressor*(camara_out["h"] - compressor_out["h_real"])/(pci_gas_natural - (camara_out["h"] - compressor_out["h_real"]))

    # Turbina
    turbina_out = {}
    turbina_out["p"] = 100
    turbina_out["pr"] = (turbina_out["p"]/camara_out["p"])*camara_out["pr"]
    interpolated = getValues(table_a22, "pr", turbina_out["pr"])
    turbina_out["h"] = interpolated["h"].values[0]
    turbina_out["T"] = interpolated["T"].values[0]
    turbina_out["h_real"] = camara_out["h"] - (n_isentropica_expansao*(camara_out["h"] - turbina_out["h"]))
    interpolated = getValues(table_a22, "h", turbina_out["h_real"])
    turbina_out["t_real"] = interpolated["T"].values[0]

    potencia_expansor = (fluxo_ar_compressor + camara_out["mc"])*(camara_out["h"] - turbina_out["h_real"])

    # Ciclo
    potencia_liquida = (potencia_expansor - potencia_compressor)*rendimento_eletromecanico
    q_fornecido = fluxo_ar_compressor*(camara_out["h"] - compressor_out["h_real"])
    n_termica = potencia_liquida/(camara_out["mc"]*pci_gas_natural)

    # Tabela de comparacao
    headers = ["Pot. Liq. (W)", "Efic. (%)", "Tgases (°C)"]
    l = [[3644, 29.56, 559], 
        [potencia_liquida, n_termica*100, celsius(turbina_out["t_real"])]]
    l.append([(l[1][0]-l[0][0])*100/l[0][0], (l[1][1]-l[0][1])*100/l[0][1], (l[1][2]-l[0][2])*100/l[0][2]])
    table = tabulate(l, headers=headers, tablefmt='orgtbl')
    print(table)

    return l[-1]

table_a22 = pd.read_excel("table_a22.xlsx")

a = 1.844
b = 1081.0
c = 0.882
d = 0.870
e = 0.867

desvios = simulacao(table_a22, a, b, c, d, e)
print(np.sum(np.abs(desvios)))