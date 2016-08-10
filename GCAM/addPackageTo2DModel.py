#!/usr/bin/env python
import argparse
import sys

import Swoop
import shapely.affinity as affinity
from GadgetMaker2.OverlapCheck import *
from Swoop.ext.ShapelySwoop import polygon_as_svg
from lxml import etree as ET

from SVGUtil import InkscapeNS


def package2svg(package):
    topCopper = package.get_geometry("Top")
    tPlace = package.get_geometry("tPlace", apply_width=False)
    tValues = package.get_geometry("tValues", apply_width=False)
    tNames = package.get_geometry("tNames", apply_width=False)
    holes =  package.get_geometry("Holes")
    tStop = package.get_geometry(layer_query="tStop")

    topCopper = topCopper.difference(holes)

    mask = tStop

    results = [
        polygon_as_svg(affinity.scale(topCopper, yfact=-1, origin=(0,0)), style="fill:#ffb600"),
        polygon_as_svg(affinity.scale(tPlace   , yfact=-1, origin=(0,0)), style="stroke:white; stroke-width:0.05mm;stroke-linecap:round;fill:none"),
        polygon_as_svg(affinity.scale(tNames   , yfact=-1, origin=(0,0)), style="stroke:white; stroke-width:0.05mm;stroke-linecap:round;fill:none"),
        polygon_as_svg(affinity.scale(tValues   , yfact=-1, origin=(0,0)), style="stroke:white; stroke-width:0.05mm;stroke-linecap:round;fill:none")
    ]
    return map(lambda x: ET.fromstring("<g>{}</g>".format(x)),results)

def removePackageFromSVG(svg):
    # remove old artwork.
    for g in svg.getroot().xpath(".//svg:g[@class='gtron-package-artwork']",
                                 namespaces=InkscapeNS.namespaces):
        g.getparent().remove(g)
    for g in svg.getroot().xpath(".//svg:g[@class='gtron-package-silkscreen']",
                                 namespaces=InkscapeNS.namespaces):
        g.getparent().remove(g)

def addPackageToSVG(svg, package):

    #Add the current version.
    group = ET.Element("g")
    group.set("class", "gtron-package-silkscreen")
    for i in package2svg(package):
        group.insert(0, i)
    svg.getroot().insert(0, group)
    
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
    removePackageFromSVG(svg)
    addPackageToSVG(svg, pack)
    svg.write(args.model)
    
def main():
    r = go(sys.argv[1:])
    sys.exit(0)

if __name__ == "__main__":
    main()
