#!/usr/bin/env python
import argparse
import argparse
from lxml import etree as ET
#from lxml import etree as ET;
import sys
from EagleLibrary import *
from EagleBoard import *
import pipes
import svgwrite
from EagleLayers import *
import svgwrite
import math
import SVGVisitor 
import DXFVisitor 
import DXFSVGVisitor 
import UtilVisitors
from GadgetCAM import *
import DXFTemplate 
import GadgetronConfig as gtron

def runGCAM(board,gcam,flipboard,format,output, layer, drawOrigins=False):

    board.instantiatePackages()

    UtilVisitors.NamedLayers(EagleLayers(board.getLayers())).visit(board.getRoot())
    UtilVisitors.FlipVisitor(EagleLayers(board.getLayers()), flipboard).visit(board.getRoot())


    execfile(gcam)

    if format.upper() == "SVG":
        SVGVisitor.SVGVisitor(drawOrigins, output, flipboard).visit(board.getRoot())
    elif format.upper() == "DXFSVG":
        DXFSVGVisitor.DXFSVGVisitor(output, flipboard, layer).visit(board.getRoot())
    elif format.upper() == "DXF":
        DXFVisitor.DXFVisitor(output, flipboard, layer).visit(board.getRoot())
    else:
        print "Unknownformaton format: " + format
        assert(False)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Tool for auto-generating packages for breakout boards")
    parser.add_argument("--brd", required=True,  type=str, nargs=1, dest='brdfile', help="brd file")
    parser.add_argument("--output", required=True, type=str, nargs=1, dest='output', help="output file")
    parser.add_argument("--gcam", required=True, type=str, nargs=1, dest='gcamfile', help="gcam file")
#    parser.add_argument("--draworigins", required=False, action='store_true', dest='draworigins', help="Draw origins for sub elments?")
    parser.add_argument("--flip", action='store_true', dest='flipboard', help="flip the board")
#parser.add_argument("--mirror", action='store_true', dest='mirror', help="mirror the board")
    parser.add_argument("--format", required=False, default="SVG", type=str, nargs=1, dest='format', help="output format")
    args = parser.parse_args()

    board = EagleBoard(args.brdfile[0])

    if args.format[0].upper() == "SVG" or args.format[0].upper() == "DXFSVG":
        out = svgwrite.Drawing(args.output[0],
                               size=(gtron.config.DEFAULT_SVG_WIDTH,
                                     gtron.config.DEFAULT_SVG_WIDTH), 
                               viewBox=gtron.config.DEFAULT_SVG_VIEWBOX)
    elif args.format[0].upper() == "DXF":
        out = open(args.output[0], "wb")
        out.write(DXFTemplate.r14_header)
    else:
        print "Unkwon format: " + args.format[0]
        assert(False)

    output = runGCAM(board=board,
                     gcam=args.gcamfile[0],
                     flipboard=args.flipboard,
                     format=args.format[0],
                     output=out,
                     layer="Layer0");
    
    if args.format[0].upper() == "SVG" or args.format[0].upper() == "DXFSVG":
        out.save()
    elif args.format[0].upper() == "DXF":
        out.write(DXFTemplate.r14_footer)
    else:
        print "Unkwon format: " + args.format[0]
        assert(False)
            
