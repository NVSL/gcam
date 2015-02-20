# To Run:
# gcam.py --brd /Users/Bonnie/Documents/MS\ Project/demo3.brd --output test-trinket.board.lc.svg --format PSVG --gcam /Users/Bonnie/Gadgets/test/Gadgets/Tools/gcam/pretty.gcam.py

# This file generates the laser cutting information to cut a board mockup.  
# So it includes the board outline and all the holes in the board, nothing else.

# Each CamPass() add attributes to tags according tho the 'default' argument.  
# to avoid name conflicts, it prefixes them with "cam_".  we also set the "cam_styled" attribute 
# on each tag we add attributes to so you can tell which ones have interesting styling information.

# setting "include" ensures that the visitor will visit this element.  
# This first pass just makes sure that visitor doesn't stop immediately.  
CamPass(board,
        paths=["./drawing", ".//element"],
        layers=[None],
        default=Style(include="1"))

# I'm not sure why we need this, but plain isn't visited if we don't have this
# CamPass(board,
#         paths=[".//plain"],
#         layers=[None],
#         default=Style(stroke_width="0.1", 
#                       fill="none", 
#                       stroke="black",
#                       stroke_linecap="round",
#                       include="1"))
# Next, grab everything in 'plain' in the Dimension layer, and add styling so it will render as thin, 
# black lines.
CamPass(board,
        paths=[".//plain", ".//plain/*"], 
        layers=[None, "Dimension"],
        default=Style(stroke_width="0.1", 
                      fill="#006600", 
                      fill_rule="evenodd",
                      stroke="black",
                      stroke_linecap="round",
                      include="1"),
        )

# Remember, we copied each package to be a child of the element tags, so we can now refer 
# to the holes and pads they contain.  These holes will be rendered in thin, black lines.

CamPass(board,
        paths=[".//element//*"], 
        layers=["tFaceplate"],
        default=Style(stroke_width="0.15", 
                      fill="blue", 
                      stroke="blue",
                      include="1")
        ) 