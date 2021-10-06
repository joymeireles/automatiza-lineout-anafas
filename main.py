import pandas as pd
from os.path import join
import matplotlib.pyplot as plt
from modelos.dadosdisjuntor import DadosDisjuntor
from modelos.dadosbarra import DadosBarra
from typing import List


def ler_relatorio_anafas(caminho_relatorio: str):
    line_outs: List[DadosDisjuntor] = []
    curto_barra: List[DadosBarra] = []
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
            # if "      Total:" in linha:
            #     total_barras = True

            # if total_barras:
            #     for _ in range(6):
            #         relatorio.readline()
            #     while True:
            #         linha = relatorio.readline()
            #         if len(linha) <= 3:
            #             total_barras = False
            #             break
            #         barras_submetidas.append(int(linha[1:6].strip()))

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
                    curto_mono = linha[30:37]
                    curto_tri = linha[44:51]
                    curto_bif = linha[58:65]
                    curto_barra.append(DadosBarra(barra_de,
                                                  curto_mono,
                                                  curto_tri,
                                                  curto_bif))
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
                        line_outs.append(DadosDisjuntor(barra_de,
                                                            barra_para,
                                                            curto_mono,
                                                            curto_tri,
                                                            curto_bif))

    return line_outs, curto_barra


def filtra_planilha(df: pd.DataFrame,
                    barras: List[DadosBarra]) -> pd.DataFrame:
    barras_de = set([b.barra_de for b in barras])
    bdf = None
    for b in barras_de:
        ibdf = df.loc[df["Barra DE"] == b, :]
        if bdf is None:
            bdf = ibdf
        else:
            bdf = pd.concat([bdf, ibdf])
    return bdf


if __name__ == "__main__":

    dir_base = "C:\\Users\\Joyce ONS\\Desktop\\Joyce ONS\\5- EGP\\Curto-Circuito"
    caminho_planilha = join(dir_base, "_automatizar processos\\_entrega final\\_META_LINE OUT 2021_R1.xlsx") # noqa
    caminho_relatorio = join(dir_base,"_automatiza ANAFAS\\relatorio anafas tres barras.rel")
    caminho_planilha_saida = ""
    line_outs, curto_barras = ler_relatorio_anafas(caminho_relatorio)
    df = pd.read_excel(caminho_planilha, "Dados Disjuntores", header=1)

    # Faz operações
    df_lineout = filtra_planilha(df, curto_barras)
    print(df_lineout)



    # Salva planilha
    # df.to_excel(join(dir_base, caminho_planilha_saida))

    # df.columns
    # disj_1257 = df.loc[(df["Barra DE"] == 1257) & (df["Barra PARA"] == 1219), "Monofásico (%)"]
    df.loc[(df["Barra DE"] == 1257) & (df["Barra PARA"] == 1219), "Monofásico (%)"]

