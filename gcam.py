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

parser = argparse.ArgumentParser(description="Tool for auto-generating packages for breakout boards")

parser.add_argument("--brd", required=True,  type=str, nargs=1, dest='brdfile', help="brd file")
parser.add_argument("--output", required=True, type=str, nargs=1, dest='output', help="output svg file")
parser.add_argument("--gcam", required=True, type=str, nargs=1, dest='gcamfile', help="gcam file")
parser.add_argument("--draworigins", required=False, action='store_true', dest='draworigins', help="Draw origins for sub elments?")
parser.add_argument("--flip", action='store_true', dest='flipboard', help="flip the board")
#parser.add_argument("--mirror", action='store_true', dest='mirror', help="mirror the board")
parser.add_argument("--format", required=False, default="SVG", type=str, nargs=1, dest='format', help="output format")

args = parser.parse_args()

board = EagleBoard(args.brdfile[0])

board.instantiatePackages()

UtilVisitors.NamedLayers(EagleLayers(board.getLayers())).visit(board.getRoot())
UtilVisitors.FlipVisitor(EagleLayers(board.getLayers()), args.flipboard).visit(board.getRoot())

execfile(args.gcamfile[0])

if args.format[0].upper() == "SVG":
    SVGVisitor.SVGVisitor(args.draworigins, args.output[0], args.flipboard).visit(board.getRoot())
elif args.format[0].upper() == "DXFSVG":
    DXFSVGVisitor.DXFSVGVisitor(args.output[0], args.flipboard).visit(board.getRoot())
elif args.format[0].upper() == "DXF":
    DXFVisitor.DXFVisitor(args.output[0], args.flipboard).visit(board.getRoot())
else:
    print "Unkwon format: " + args.format[0]
