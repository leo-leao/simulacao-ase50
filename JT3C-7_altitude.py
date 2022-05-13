import numpy as np
import pandas as pd
from tabulate import tabulate
from functions import Functions as func

table_a22 = pd.read_excel("table_a22.xlsx")
# Decolagem muda temperatura, pressao, velocidade 
# Enpuxo, consumo de combustivel, consumo especifico, eficiencia
def simulacao(table_a22, a, c, d):

    # Parâmetros da turbina JT3C-7
    m_ar_iso = 81.65                                            # [kg/s]
    impulso_cruzeiro = 15800                                # [N]

    """Consumo específico de combustível"""
    cce_cruzeiro = 25.7                                     # [g/kN/s]
    cc_cruzeiro = (cce_cruzeiro * impulso_cruzeiro)/1000    # [g/s]

    """Caracteristicas ISO"""
    temp_iso = func.kelvin(15)                              # [K]
    p_iso = 101.325                                         # [kPa]
    R_ar_iso = 8.314/28.96                                  # [kJ/kg*°C]
    v_iso = temp_iso*R_ar_iso/p_iso  

    # Avião a jato voando a 260m/s e 7000 metros de altitude
    v_in = 260                                              # [m/s]
    T_amb = func.kelvin(-29.7915)
    p_amb = 41.6948
    inter = func.getValues(table_a22, "T", T_amb)
    h_amb = inter["h"].values[0]  
    pr_amb = inter["pr"].values[0]


    """Dados"""
    pr_comp = 12.5
    R_ar = 8.314/28.97
    v = R_ar*T_amb/p_amb                                    # [m3/kg]
    m_ar_in = m_ar_iso*v_iso/v                              # [kg/s]
    PCI = 42800                                             # [kJ/kg]
    n_comp = c
    n_exps = d
    delta_p = a/100                                         # [kJ/kg*°C]
    pho = 1/v                                               # [kg/m3]
    phi_ar = m_ar_in*v                                      # [m3/s]
    area_frontal = phi_ar/v_in                              # [m2]
    diametro = (area_frontal*4/3.1418)**0.5                 # [m]

    # Estado 1:
    h_1 = h_amb+(v_in**2)/2/1000
    inter = func.getValues(table_a22, "h", h_1)
    T_1 = inter["T"].values[0]
    pr_1 = inter["pr"].values[0]
    p_1 = (pr_1/pr_amb)*p_amb

    # Estado 2s:
    pr_2s = pr_1*pr_comp
    inter = func.getValues(table_a22, "pr", pr_2s)
    T_2s = inter["T"].values[0]
    h_2s = inter["h"].values[0]

    # Estado 2:
    p_2 = p_1*pr_comp
    h_2 = h_1 + (h_2s - h_1)/n_comp
    inter = func.getValues(table_a22, "h", h_2)
    T_2 = inter["T"].values[0]

    # Estado 3:
    p_3 = p_2*(1 - delta_p)
    h_3 = 1123                                              # [kJ/kg]
    inter = func.getValues(table_a22, "h", h_3)
    T_3 = inter["T"].values[0]
    pr_3 = inter["pr"].values[0]

    #print("Estado 3:", T_3, pr_3, p_3, h_3)

    """Resultados parciais"""
    m_comb_1 = (m_ar_in * (h_3 - h_2))/(PCI - h_3)          # [kg/s]
    m_comb_2 = m_comb_1 * 3600                              # [kg/h]
    W_comp_1 = m_ar_in*(h_2 - h_1)                          # [kW]
    W_comp_2 = W_comp_1/m_ar_in                             # [kW/kg]
    W_exps_1 = W_comp_1                                     # [kW]
    W_exps_2 = W_comp_1/(m_ar_in + m_comb_1)                # [kW/kg]

    #print("Resultados parciais:", m_comb_1, W_comp_1, W_exps_1)

    # Estado 4s:
    h_4s = h_3 - (W_exps_1/((m_ar_in + m_comb_1)*n_exps))
    inter = func.getValues(table_a22, "h", h_4s)
    T_4s = inter["T"].values[0]
    pr_4s = inter["pr"].values[0]

    #print("Estado 4s:", T_4s, pr_4s, h_4s)

    # Estado 4:
    p_4 = p_3/(pr_3/pr_4s)
    h_4 = h_3 - (h_3 - h_4s)*n_exps
    inter = func.getValues(table_a22, "h", h_4)
    T_4 = inter["T"].values[0]
    pr_4 = inter["pr"].values[0]

    #print("Estado 4:",T_4, pr_4, p_4, h_4)

    # Estado 5:
    p_5 = p_amb
    pr_5 = pr_4/(p_4/p_5)
    inter = func.getValues(table_a22, "pr", pr_5)
    T_5 = inter["T"].values[0]
    h_5 = inter["h"].values[0]

    #print("Estado 5:", T_5, pr_5, p_5, h_5)

    """Resultados finais"""
    v_exaustao = (2*(h_4 - h_5)*1000)**0.5
    f_empuxo = (m_ar_in + m_comb_1)*v_exaustao - m_ar_in*v_in
    impulso_especifico_1 = f_empuxo/m_ar_in                # [N/kg/s_ar]   
    impulso_especifico_2 = impulso_especifico_1/101.973    # [g/kN/s]
    cce_cruzeiro_sim = (m_comb_1*1000)/(f_empuxo/1000)
    n_propulsiva = 2/(1+(v_exaustao/v_in))

    headers = ["", "Consumo", "Consumo específico", "Impulso"]
    l = [["Fabricante", cc_cruzeiro/1000, cce_cruzeiro, impulso_cruzeiro], 
        ["Simulação", m_comb_1, cce_cruzeiro_sim, f_empuxo]]
    l.append(["Desvio", (l[1][1]-l[0][1])*100/l[0][1], (l[1][2]-l[0][2])*100/l[0][2], (l[1][3]-l[0][3])*100/l[0][3]])
    table = tabulate(l, headers=headers, tablefmt='orgtbl')
    print(table)

    print("\nEficiência propulsiva:", n_propulsiva)

    return l[-1]

pdc, ec, ee = 2.1, 0.869, 0.854
simulacao(table_a22, pdc, ec, ee)