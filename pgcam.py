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
import math
import SVGVisitor 
import PSVGVisitor 
import DXFVisitor 
import DXFSVGVisitor 
import UtilVisitors
from GadgetCAM import *
import DXFTemplate 
import GadgetronConfig as gtron

def runGCAM(board,gcam,flipboard,format,output, layer, mirrored, drawOrigins=False):
    
    # This step expand each 'element' tag to include a copy of the package from
    # the library.  Now, we can style/manipulate/etc. each of the instances
    # independently.
    board.instantiatePackages()

    # Replace layer numbers with names 
    UtilVisitors.NamedLayers(EagleLayers(board.getLayers())).visit(board.getRoot())  
    # flip everything, if we are rendering the backside of the board.
    UtilVisitors.FlipVisitor(EagleLayers(board.getLayers()), flipboard).visit(board.getRoot()) 
    
    # Change the Name and Value attribute tag for each element to text tags for display
    UtilVisitors.RetagNameAttribute(EagleLayers(board.getLayers())).visit(board.getRoot())
    UtilVisitors.RetagValueAttribute(EagleLayers(board.getLayers())).visit(board.getRoot())

    # Remove the Name and Value text tags from the library
    UtilVisitors.RemoveNameVariable(EagleLayers(board.getLayers())).visit(board.getRoot())
    UtilVisitors.RemoveValueVariable(EagleLayers(board.getLayers())).visit(board.getRoot())

    # Transforms the texts within the Elements that aren't part of tName or bName
    UtilVisitors.TranformElementText(EagleLayers(board.getLayers())).visit(board.getRoot())

    execfile(gcam) # execute the gcam file.

    # At this point the the board is full of styling attributes.  Now, we can
    # convert it to the output format using the appropriate visitor.
    output_tree = board.getET()
    output_tree.write("testoutput.txt", encoding="UTF-8")

    if format.upper() == "SVG":
        SVGVisitor.SVGVisitor(drawOrigins, output, flipboard, mirrored).visit(board.getRoot())
    elif format.upper() == "DXFSVG":
        DXFSVGVisitor.DXFSVGVisitor(output, flipboard, layer,mirrored).visit(board.getRoot())
    elif format.upper() == "DXF":
        DXFVisitor.DXFVisitor(output, flipboard, layer,mirrored).visit(board.getRoot())
    elif format.upper() == "PSVG":
        PSVGVisitor.PSVGVisitor(drawOrigins, output, flipboard, mirrored).visit(board.getRoot())
    else:
        print "Unknown formaton format: " + format
        assert(False)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Tool for auto-generating packages for breakout boards")
    parser.add_argument("--brd", required=True,  type=str, nargs=1, dest='brdfile', help="brd file")
    parser.add_argument("--output", required=True, type=str, nargs=1, dest='output', help="output file")
    parser.add_argument("--gcam", required=True, type=str, nargs=1, dest='gcamfile', help="gcam file")
#    parser.add_argument("--draworigins", required=False, action='store_true', dest='draworigins', help="Draw origins for sub elments?")
    parser.add_argument("--flip", action='store_true', dest='flipboard', help="flip the board")
    parser.add_argument("--mirror", action='store_true', dest='mirror', help="output the data flip horizontally")
    parser.add_argument("--format", required=False, default="SVG", type=str, nargs=1, dest='format', help="output format")
    args = parser.parse_args()
    board = EagleBoard(args.brdfile[0])

    if args.format[0].upper() == "SVG" or args.format[0].upper() == "PSVG" or args.format[0].upper() == "DXFSVG":
        out = svgwrite.Drawing(args.output[0],
                               size=(gtron.config.DEFAULT_SVG_WIDTH,
                                     gtron.config.DEFAULT_SVG_WIDTH), 
                               viewBox=gtron.config.DEFAULT_SVG_VIEWBOX)
    elif args.format[0].upper() == "DXF":
        out = open(args.output[0], "wb")
        out.write(DXFTemplate.r14_header)
    else:
        print "Unknwon format: " + args.format[0]
        assert(False)

    output = runGCAM(board=board,
                     gcam=args.gcamfile[0],
                     flipboard=args.flipboard,
                     format=args.format[0],
                     output=out,
                     layer="Layer0",
                     mirrored=args.mirror);
    
    if args.format[0].upper() == "SVG" or args.format[0].upper() == "PSVG" or args.format[0].upper() == "DXFSVG":
        out.save()
    elif args.format[0].upper() == "DXF":
        out.write(DXFTemplate.r14_footer)
    else:
        print "Unknwon format: " + args.format[0]
        assert(False)
            
