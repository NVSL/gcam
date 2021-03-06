#!/usr/bin/env python
import argparse

import svgwrite

import DXFSVGVisitor
import DXFTemplate
import DXFVisitor
import SVGVisitor
import UtilVisitors
from GadgetCAM import *
from Gadgetron.Gadgetron import GadgetronConfig as gtron


def runGCAM(board,gcam,flipboard,format,output, layer, mirrored, drawOrigins=False):
    
    # This step expand each 'element' tag to include a copy of the package from
    # the library.  Now, we can style/manipulate/etc. each of the instances
    # independently.
    board.instantiatePackages()

    UtilVisitors.NamedLayers(EagleLayers(board.getLayers())).visit(board.getRoot())  # Replace layer numbers with names 
    UtilVisitors.FlipVisitor(EagleLayers(board.getLayers()), flipboard).visit(board.getRoot()) # flip everything, if we are rendering the backside of the board.


    execfile(gcam) # execute the gcam file.

    # At this point the the board is full of styling attributes.  Now, we can
    # convert it to the output format using the appropriate visitor.
    if format.upper() == "SVG":
        SVGVisitor.SVGVisitor(drawOrigins, output, flipboard, mirrored).visit(board.getRoot())
    elif format.upper() == "DXFSVG":
        DXFSVGVisitor.DXFSVGVisitor(output, flipboard, layer,mirrored).visit(board.getRoot())
    elif format.upper() == "DXF":
        DXFVisitor.DXFVisitor(output, flipboard, layer,mirrored).visit(board.getRoot())
    else:
        print "Unknownformaton format: " + format
        assert(False)
def main(argv=None):
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
                     layer="Layer0",
                     mirrored=args.mirror);
    
    if args.format[0].upper() == "SVG" or args.format[0].upper() == "DXFSVG":
        out.save()
    elif args.format[0].upper() == "DXF":
        out.write(DXFTemplate.r14_footer)
    else:
        print "Unkwon format: " + args.format[0]
        assert(False)

if __name__ == "__main__":
    main()
