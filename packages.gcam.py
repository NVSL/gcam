# To Run:
# pgcam.py --brd /Users/Bonnie/Documents/MS\ Project/demo3.brd --output test-trinket.board.lc.svg --format PSVG --gcam /Users/Bonnie/Gadgets/test/Gadgets/Tools/gcam/pretty.gcam.py

# Each CamPass() add attributes to tags according tho the 'default' argument.  
# to avoid name conflicts, it prefixes them with "cam_".  we also set the "cam_styled" attribute 
# on each tag we add attributes to so you can tell which ones have interesting styling information.

# setting "include" ensures that the visitor will visit this element.  
# This first pass just makes sure that visitor doesn't stop immediately.  
CamPass(board,
        paths=["./drawing", ".//element"],
        layers=[None],
        default=Style(include="1"))

# Next, grab everything in 'plain' in the Dimension layer, and add styling so it will render as thin, 
# black lines.
CamPass(board,
        paths=[".//plain", ".//plain/*"], 
        layers=[None,
                "Dimension", 
                "tPlace", 
                "bPlace", 
                "tNames", 
                "bNames", 
                "tValue", 
                "bValue",
                "tDocu",
                "bDocu"
                      ],
        default=Style(stroke_width="0.1", 
                      fill="#006600", #175181 = adafruit blue
                      fill_rule="evenodd",
                      stroke="black",
                      stroke_linecap="round",
                      include="1"),
        refinements={"text" : Style(fill="#CFCFCF",
                                    stroke="#CFCFCF",
                                    stroke_width="0.1",
                                    ),
                    }
        ) 

CamPass(board,
        paths=[".//signal//via"], 
        layers=["Vias"],
        default=Style(stroke_width="0.01", 
                      fill="black", 
                      fill_rule="evenodd",
                      stroke="none",
                      include="1"))

# Find and draw top and bottom layer electric wiring
# CamPass(board,
#         paths=[".//signal"],
#         layers=[None],
#         default=Style(stroke_width="0.1", 
#                       stroke_opacity="0.4",
#                       stroke="red",
#                       fill="none",
#                       include="1"))

# the stroke color here is specified in the method drawWirePath() in PSVGVisitor.py
CamPass(board,
        paths=[".//signals", ".//signal//wire"], 
        layers=[None, "Top"], # "None" is needed here because <signals> doesn't have a layer attr
        default=Style(stroke_width="0.1", 
                      stroke_opacity="0.5",
                      stroke_linecap="round",
                      # stroke="red",
                      fill="none",
                      include="1"))
CamPass(board,
        paths=[".//signals", ".//signal//wire"], 
        layers=[None, "Bottom"],
        default=Style(stroke_width="0.1", 
                      stroke_opacity="0.5",
                      stroke_linecap="round",
                      # stroke="blue",
                      fill="none",
                      include="1"))

# Remember, we copied each package to be a child of the element tags, so we can now refer 
# to the holes and pads they contain.  These holes will be rendered in thin, black lines.
CamPass(board,
#        paths=[".//element//hole"],
        paths=[".//package//hole"],
        layers=[None],
        default=Style(stroke_width="0.1", 
                      fill="none",
                      stroke="black",
                      include="1"))

# Finds and draws pads for each element
CamPass(board,
#        paths=[".//package//pad"], 
        paths=[".//package//pad"], 
        layers=[None],
        default=Style(stroke_width="0.01", 
                      fill="#458545", 
                      fill_rule="evenodd",
                      stroke="none",
                      include="1"))

CamPass(board,
#        paths=[".//package//smd"], 
        paths=[".//package//smd"], 
        layers=["Top"],
        default=Style(fill="#CCCCCC", # CCCCCC = silver
                      fill_opacity="0.9",
                      include="1"))

# Find and draw the silk screen
CamPass(board,
#        paths=[".//package//*"], 
        paths=[".//package//*"], 
        layers=["tPlace", "bPlace", "tDocu", "bDocu"],
        default=Style(stroke_width="0.15", 
                      fill="none", 
                      stroke="#CFCFCF",
                      include="1"),
        refinements={"rectangle" : Style(stroke="none",
                                         fill="#CFCFCF"),
                     "text" : Style(fill="#CFCFCF",
                                    stroke="#CFCFCF",
                                    stroke_width="0.1",
                                    ),
                    }
        ) 
CamPass(board,
#        paths=[".//packages//text"], 
        paths=[".//packages//text"], 
        layers=["tNames", "bNames"],
        default=Style(fill="none", 
                      stroke="#CFCFCF",
                      include="0"),
        refinements={"text" : Style(stroke="none",
                                    fill="#CFCFCF")}
        )

CamPass(board,
#        paths=[".//packages//text"], 
        paths=[".//packages//text"], 
        layers=["tValues", "bValues"],
        default=Style(fill="none", 
                      stroke="#CFCFCF",
                      include="0"),
        refinements={"text" : Style(stroke="none",
                                    fill="#CFCFCF")}
        )

CamPass(board,
#        paths=[".//package//*"], 
        paths=[".//package//*"], 
        layers=["tDocu", "bDocu"],
        default=Style(stroke_width="0.15", 
                      fill="none", 
                      stroke="#CFCFCF",
                      include="0"),
        refinements={"rectangle" : Style(stroke="none",
                                         fill="#CFCFCF")}
        ) 

CamPass(board,
#        paths=[".//package//*"], 
        paths=[".//package//*"], 
        layers=["tFaceplate"],
        default=Style(stroke_width="0.15", 
                      fill="#add8e6", 
                      fill_opacity="0.5",
                      stroke="#add8e6",
                      include="1")
        ) 
