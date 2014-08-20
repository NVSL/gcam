CamPass(board,
        paths=["./drawing", ".//element"],
        layers=[None],
        default=Style(include="1"))

CamPass(board,
        paths=[".//element/package/*", ".//plain/*"], 
        layers=["tFaceplate", "Dimension"],
        default=Style(stroke_width="0.1", 
                      fill="none", 
                      stroke="black",
                      stroke_linecap="round",
                      include="1"))

