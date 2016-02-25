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
from lxml import etree as ET
import shapely.affinity as affinity

def package2svg(package):
    topCopper = package.get_geometry("Top")
    tPlace = package.get_geometry("tPlace")
    holes =  package.get_geometry("Holes")
    tStop = package.get_geometry(layer_query="tStop")

    topCopper = topCopper.difference(holes)

    mask = tStop
    
    #    tPlace = tPlace.difference(tStop)

    results = [
               polygon_as_svg(affinity.scale(topCopper, yfact=-1, origin=(0,0)), style="fill:#ffb600"),
               polygon_as_svg(affinity.scale(tPlace   , yfact=-1, origin=(0,0)), style="stroke:#000000; stroke-width:0.05mm;fill:none")]
    svg = """<g><g>{}</g><g>{}</g></g>""".format(results[0], results[1])
    return map(lambda x: ET.fromstring("<g>{}</g>".format(x)),results)
    
def go(argv=None):
    parser = argparse.ArgumentParser(description="Check a design for design rule violations.")
    parser.add_argument("--lbr", required=True,  type=str, help="library")
    parser.add_argument("--pack", required=True,  type=str, help="package")
    parser.add_argument("--model", required=True,  type=str, help="2Dmodel")
    parser.add_argument("-v", required=False,  action='store_const', const=1, default=0, dest="verbose", help="Be verbose")
    parser.add_argument("-vv", required=False,  action='store_const', const=2, default=0, dest="verbose", help="Be very verbose")
    parser.add_argument("-vvv", required=False,  action='store_const', const=3, default=0, dest="verbose", help="Be very, very, verbose")
    args = parser.parse_args(argv)

    if args.verbose >= 2:
        log.basicConfig(format="%(levelname)s: %(message)s", level=log.DEBUG)
    elif args.verbose >= 1:
        log.basicConfig(format="%(levelname)s: %(message)s", level=log.INFO)
                
    lbr = Swoop.ext.ShapelySwoop.ShapelySwoop.from_file(args.lbr)

    pack = lbr.get_library().get_package(args.pack)
    assert pack is not None, "Missing package {} in library {}".format(args.lbr, args.pack)

    svg = ET.parse(args.model)
    for i in package2svg(pack):
        svg.getroot().insert(0, i)
    #ET.dump(svg.getroot())
    
    #svg.write("test.svg")
    svg.write(args.model)
    
def main():
    r = go(sys.argv[1:])
    sys.exit(0)

if __name__ == "__main__":
    main()
