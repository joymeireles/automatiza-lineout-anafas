class DadosCurtoCircuito:
    """
    """
    def __init__(self,
                 barra_de: str,
                 barra_para: str,
                 curto_mono: str,
                 curto_tri: str,
                 curto_bif: str) -> None:
        self.barra_de = int(barra_de.strip())
        self.barra_para = int(barra_para.strip())
        self.curto_mono = float(curto_mono.strip().replace(",", "."))
        self.curto_tri = float(curto_tri.strip().replace(",", "."))
        self.curto_bif = float(curto_bif.strip().replace(",", "."))