#!/usr/bin/env python
import argparse
import pipes
import svgwrite
import math
import Swoop
from Swoop import From
from Swoop.ext.ShapelySwoop import GeometryDump as GeoDump
from Swoop.ext.ShapelySwoop import ShapelyEagleFilePart as SEFP
from Swoop.ext.ShapelySwoop import polygon_as_svg
from shapely.geometry import *
import sys
from OverlapCheck import *
import shapely.geometry as shapes

def go(argv=None):
    parser = argparse.ArgumentParser(description="Check a design for design rule violations.")
    parser.add_argument("--brd", required=True,  type=str, help="input board")
    parser.add_argument("-v", required=False,  action='store_const', const=1, default=0, dest="verbose", help="Be verbose")
    parser.add_argument("-vv", required=False,  action='store_const', const=2, default=0, dest="verbose", help="Be very verbose")
    parser.add_argument("-vvv", required=False,  action='store_const', const=3, default=0, dest="verbose", help="Be very, very, verbose")
    args = parser.parse_args(argv)

    if args.verbose >= 2:
        log.basicConfig(format="%(levelname)s: %(message)s", level=log.DEBUG)
    elif args.verbose >= 1:
        log.basicConfig(format="%(levelname)s: %(message)s", level=log.INFO)
                
    brd = Swoop.ext.ShapelySwoop.ShapelySwoop.from_file(args.brd)


    board = brd.get_geometry("Dimension", polygonize_wires=SEFP.POLYGONIZE_STRICT)
    topCopper = brd.get_geometry("Top")
    tPlace = brd.get_geometry("tPlace")
    holes =  brd.get_geometry("Holes")
    tStop = brd.get_geometry(layer_query="tStop")

    board = board.difference(holes)
    topCopper = topCopper.difference(holes)
    tPlace = tPlace.difference(tStop)
    
    mask = board.difference(tStop)
        
    results = [polygon_as_svg(board, style="fill:#fff49a"),
               polygon_as_svg(topCopper, style="fill:#ffb600"),
               polygon_as_svg(mask, style="fill:#00ff00; fill-opacity:0.5"),
               polygon_as_svg(tPlace, style="stroke:#ffffff; stroke-width:0.1mm;fill:none")]
               
    svg = """<svg><defs>
    <link href="my-style.css" type="text/css" rel="stylesheet" 
    xmlns="http://www.w3.org/1999/xhtml"/>
    </defs>{}</svg>""".format("".join(results))
    
    open("out.svg", "w").write(svg)
    
def main():
    r = go(sys.argv[1:])
    sys.exit(0)

if __name__ == "__main__":
    main()
