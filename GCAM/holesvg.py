#!/usr/bin/env python
import argparse

import svgwrite
from EagleBoard import *
from EagleLayers import *
from EagleLibrary import *

import DXFTemplate
import PSVGVisitor
import UtilVisitors
from GadgetCAM import *
from Gadgetron.Gadgetron import GadgetronConfig as gtron


def runGCAM(board,gcam,flipboard,format,output, layer, mirrored, drawOrigins=False, allBoardHoles=None, tFaceplate=None):
    
    # This step expand each 'element' tag to include a copy of the package from
    # the library.  Now, we can style/manipulate/etc. each of the instances
    # independently.
    board.instantiatePackages()

    # Replace layer numbers with names 
    UtilVisitors.NamedLayers(EagleLayers(board.getLayers())).visit(board.getRoot())  
    # flip everything, if we are rendering the backside of the board.
    UtilVisitors.FlipVisitor(EagleLayers(board.getLayers()), flipboard).visit(board.getRoot()) 

    execfile(gcam) # execute the gcam file.

    # At this point the the board is full of styling attributes.  Now, we can
    # convert it to the output format using the appropriate visitor.
    output_tree = board.getET()
    output_tree.write("testoutput.txt", encoding="UTF-8")

    PSVGVisitor.PSVGVisitor(drawOrigins, output, flipboard, mirrored, tFaceplate=tFaceplate).visit(board.getRoot())
    

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Tool for auto-generating packages for breakout boards")
    parser.add_argument("--brd", required=True,  type=str, nargs='+', dest='brdfile', help="brd file")
    parser.add_argument("--output", required=True, type=str, nargs=1, dest='output', help="output file")
    parser.add_argument("--gcam", required=True, type=str, nargs=1, dest='gcamfile', help="gcam file")
#    parser.add_argument("--draworigins", required=False, action='store_true', dest='draworigins', help="Draw origins for sub elments?")
    parser.add_argument("--flip", action='store_true', dest='flipboard', help="flip the board")
    parser.add_argument("--mirror", action='store_true', dest='mirror', help="output the data flip horizontally")
    parser.add_argument("--format", required=False, default="PSVG", type=str, nargs=1, dest='format', help="output format")
    args = parser.parse_args()
    
    
    holes_out = svgwrite.Drawing(args.output[0],
                               size=(gtron.config.DEFAULT_SVG_WIDTH,
                                     gtron.config.DEFAULT_SVG_WIDTH), 
                               viewBox=gtron.config.DEFAULT_SVG_VIEWBOX)
    tFaceplate = holes_out.path()
    # tFaceplate.push("M-50000,50000 L50000,50000 L50000,-50000 L-50000,-50000 Z") 
    tFaceplate.push("M 0,0") # This is so that we don't get a TypeError

    for brd_file in args.brdfile:
        board = EagleBoard(brd_file)

        out = svgwrite.Drawing(args.output[0],
                               size=(gtron.config.DEFAULT_SVG_WIDTH,
                                     gtron.config.DEFAULT_SVG_WIDTH), 
                               viewBox=gtron.config.DEFAULT_SVG_VIEWBOX)

        output = runGCAM(board=board,
                         gcam=args.gcamfile[0],
                         flipboard=args.flipboard,
                         format=args.format[0],
                         output=out,
                         layer="Layer0",
                         mirrored=args.mirror,
                         tFaceplate=tFaceplate);

    group = holes_out.g(transform="scale(1,-1)", style="fill:#add8e6; fill-rule:evenodd; fill-opacity:0.5; stroke: #add8e6;stroke-width: 0.1;")
    group.add(tFaceplate)
    holes_out.add(group)
    holes_out.save()
    print holes_out.tostring()

    if args.format[0].upper() == "SVG" or args.format[0].upper() == "PSVG" or args.format[0].upper() == "DXFSVG":
        holes_out.save()
    elif args.format[0].upper() == "DXF":
        holes_out.write(DXFTemplate.r14_footer)
    else:
        print "Unknwon format: " + args.format[0]
        assert(False)
            
