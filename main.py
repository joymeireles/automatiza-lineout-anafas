import numpy as np
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

def esvazia_curto_df(df: pd.DataFrame) -> pd.DataFrame:
    df.loc[:, "Monofásico (kA)"] = np.nan
    df.loc[:, "Trifásico (kA)"] = np.nan
    df.loc[:, "Bifásico-Terra (kA)"] = np.nan
    df.loc[:, "Monofásico (%)"] = np.nan
    df.loc[:, "Trifásico (%)"] = np.nan
    df.loc[:, "Bifásico-Terra (%)"] = np.nan
    df.loc[:, "Situação"] = np.nan
    return df

def calcula_percent(df: pd.DataFrame) -> pd.DataFrame:
    df["Monofásico (%)"] = 100*df["Monofásico (kA)"]/df["Capacidade de interrupção simétrica (kA)"]
    df["Trifásico (%)"] = 100*df["Trifásico (kA)"]/df["Capacidade de interrupção simétrica (kA)"]
    df["Bifásico-Terra (%)"] = 100*df["Bifásico-Terra (kA)"]/df["Capacidade de interrupção simétrica (kA)"]
    filtro_vago = df["Nome do Equipamento"] == ("Vago" or "vago")
    df.loc[filtro_vago, "Monofásico (%)"] = np.nan
    df.loc[filtro_vago, "Trifásico (%)"] = np.nan
    df.loc[filtro_vago, "Bifásico-Terra (%)"] = np.nan
    return df

def analisa_superacao(df: pd.DataFrame) -> pd.DataFrame:

    def _filtra_alerta(coluna: str) -> pd.Series:
        alerta_inferior = df[coluna] >= 90
        alerta_superior = df[coluna] < 100
        return alerta_inferior & alerta_superior

    def _condicao_alerta() -> pd.Series:
        alerta_mono = _filtra_alerta("Monofásico (%)")
        alerta_tri = _filtra_alerta("Trifásico (%)")
        alerta_bif = _filtra_alerta("Bifásico-Terra (%)")
        return alerta_mono | alerta_tri | alerta_bif

    def _filtra_superado(coluna: str) -> pd.Series:
        return df[coluna] >=100

    def _condicao_superado() -> pd.Series:
        superado_mono = _filtra_superado("Monofásico (%)")
        superado_tri = _filtra_superado("Trifásico (%)")
        superado_bif = _filtra_superado("Bifásico-Terra (%)")
        return superado_mono | superado_tri | superado_bif

    condicoes = [_condicao_superado(), _condicao_alerta()]
    status = ["Superado", "Alerta"]
    df["Situação"] = np.select(condicoes, status, default="Ok")
    return df

def atribui_curto(df: pd.DataFrame,
                  line_outs: List[DadosDisjuntor],
                  curto_barras: List[DadosBarra]) -> pd.DataFrame:

    df_lineout = esvazia_curto_df(df)

    for line_out in line_outs:
        filtro_de = (df_lineout["Barra DE"] == line_out.barra_de)
        filtro_para = (df_lineout["Barra PARA"] == line_out.barra_para)
        filtro = filtro_de & filtro_para
        df_lineout.loc[filtro,
                       "Monofásico (kA)"] = line_out.curto_mono
        df_lineout.loc[filtro,
                       "Trifásico (kA)"] = line_out.curto_tri
        df_lineout.loc[filtro,
                       "Bifásico-Terra (kA)"] = line_out.curto_bif
        
    for curto_barra in curto_barras:
        filtro_de = (df_lineout["Barra DE"] == curto_barra.barra_de)
        filtro_para = (df_lineout["Barra PARA"].isna())
        df_lineout.loc[filtro_de & filtro_para, "Monofásico (kA)"] = curto_barra.curto_mono
        df_lineout.loc[filtro_de & filtro_para, "Trifásico (kA)"] = curto_barra.curto_tri
        df_lineout.loc[filtro_de & filtro_para, "Bifásico-Terra (kA)"] = curto_barra.curto_bif

    df = calcula_percent(df_lineout)
    df = analisa_superacao(df)
 
    return df



if __name__ == "__main__":

    dir_base = "C:\\Users\\Joyce ONS\\Desktop\\Joyce ONS\\5- EGP\\Curto-Circuito"
    caminho_planilha = join(dir_base, "_automatizar processos\\_entrega final\\_META_LINE OUT 2026_R1.xlsx") # noqa
    caminho_relatorio = join(dir_base,"_automatiza ANAFAS\\lineout399_antes.rel")
    caminho_planilha_saida = "_automatiza ANAFAS\\lineout399_antes.xlsx"
    line_outs, curto_barras = ler_relatorio_anafas(caminho_relatorio)
    df = pd.read_excel(caminho_planilha, "Dados Disjuntores", header=1)

    # Faz operações
    df_lineout = filtra_planilha(df, curto_barras)
    df_saida = atribui_curto(df_lineout, line_outs, curto_barras)

    # Salva planilha
    df_saida.to_excel(join(dir_base, caminho_planilha_saida))

    # df.columns
    # disj_1257 = df.loc[(df["Barra DE"] == 1257) & (df["Barra PARA"] == 1219), "Monofásico (%)"]
    df.loc[(df["Barra DE"] == 1257) & (df["Barra PARA"] == 1219), "Monofásico (%)"]

