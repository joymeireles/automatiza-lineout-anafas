import pandas as pd
import matplotlib.pyplot as plt
from modelos.dadoscurtocircuito import DadosCurtoCircuito
from typing import List


def ler_relatorio_anafas(caminho_relatorio: str):
    line_outs: List[DadosCurtoCircuito] = []
    barras_submetidas = []
    with open(caminho_relatorio,
              "r",
              encoding="iso-8859-1") as relatorio:
        encontrou_contribuicoes = False
        total_barras = False
        while True:
            linha = relatorio.readline()
            if len(linha) == 0:
                break
            # Senão, ainda tem arquivo pra ler
            if "      Total:" in linha:
                total_barras = True

            if total_barras:
                for _ in range(6):
                    relatorio.readline()
                while True:
                    linha = relatorio.readline()
                    if len(linha) <= 3:
                        total_barras = False
                        break
                    barras_submetidas.append(int(linha[1:6].strip()))

            if "2) Contribuições de corrente" in linha:
                encontrou_contribuicoes = True
                continue
            
            if encontrou_contribuicoes:
                if "  Num.     Nome    Área" in linha:
                    # Pula 1 linha
                    relatorio.readline()
                    # Recorta a barra DE
                    linha = relatorio.readline()
                    barra_de = linha[1:6]
                    # Pula 6 linhas
                    for _ in range(6):
                        relatorio.readline()
                    while True:
                        linha = relatorio.readline()
                        if len(linha) <= 3:
                            break
                        # Recorta a barra PARA e os níveis
                        barra_para = linha[1:6]
                        curto_mono = linha[40:47]
                        curto_tri = linha[52:59]
                        curto_bif = linha[64:71]
                        line_outs.append(DadosCurtoCircuito(barra_de,
                                                            barra_para,
                                                            curto_mono,
                                                            curto_tri,
                                                            curto_bif))

    return line_outs, barras_submetidas

if __name__ == "__main__":

    caminho_planilha = "C:\\Users\\Joyce ONS\\Desktop\\Joyce ONS\\5- EGP\\Curto-Circuito\\_automatizar processos\\_entrega final\\_META_LINE OUT 2021_R1.xlsx" # noqa
    caminho_relatorio = "C:\\Users\\Joyce ONS\\Desktop\\Joyce ONS\\5- EGP\\Curto-Circuito\\_automatiza ANAFAS\\relatorio anafas tres barras.rel"
    [line_outs, barras_submetidass] = ler_relatorio_anafas(caminho_relatorio)
    df = pd.read_excel(caminho_planilha, "Dados Disjuntores", header=1)

    

    # df.columns
    # disj_1257 = df.loc[(df["Barra DE"] == 1257) & (df["Barra PARA"] == 1219), "Monofásico (%)"]
    # df.loc[(df["Barra DE"] == 1257) & (df["Barra PARA"] == 1219), "Monofásico (%)"] = 80
    # disj_1257
    # df
    # df["Nível de Tensão"].plot.hist()
    # plt.show()
