CamPass(board,
        paths=["./drawing", ".//element"],
        layers=[None],
        default=Style(include="1"))

CamPass(board,
        paths=[".//plain/*"], 
        layers=["Dimension"],
        default=Style(stroke_width="0.1", 
                      fill="none", 
                      stroke="black",
                      stroke_linecap="round",
                      include="1"))

CamPass(board,
        paths=[".//element//hole", ".//element//pad"], 
        layers=[None],
        default=Style(stroke_width="0.1", 
                      fill="none", 
                      stroke="black",
                      include="1"))

if False:
    CamPass(board,
            paths=[".//element/package/*", ".//plain/*"], 
            layers=["tPlace", "tDocu"],
            default=Style(stroke_width="0.1", 
                          fill="none", 
                          stroke="red",
                          stroke_linecap="round",
                          include="1"),
            refinements={"rectangle" : Style(stroke="none",
                                             fill="red"),
                         "text" : Style(stroke="none",
                                        fill="red")}
            )

