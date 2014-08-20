CamPass(board,
        paths=["./drawing", ".//element"],
        layers=[None],
        default=Style(include="1"))

CamPass(board,
        paths=[".//element/package/*", ".//plain/*"], 
        layers=["tPlace",  "tDocu", "Dimension", None],
        default=Style(stroke_width="0.1", 
                      fill="none", 
                      stroke="black",
                      stroke_linecap="round",
                      include="1"),
        refinements={"rectangle" : Style(stroke="none",
                                         fill="black"),
                     "text" : Style(stroke="none",
                                    fill="black")}
        )

