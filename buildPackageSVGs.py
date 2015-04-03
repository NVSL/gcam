#!/usr/bin/env python
import argparse
import os

from lxml import etree as ET
import svgwrite

from GadgetCAM import *
import GadgetronConfig as gtron

from EagleLibrary import *
from EagleLayers import *
import PSVGVisitor 
import UtilVisitors
import Dingo.Component



def buildPackageSVGs(library,outputDir,gcam,drawOrigins=False):
    
    # This step expand each 'element' tag to include a copy of the package from
    # the library.  Now, we can style/manipulate/etc. each of the instances
    # independently.

    # Replace layer numbers with names 
    UtilVisitors.NamedLayers(EagleLayers(library.getLayers())).visit(library.getRoot())  
    # flip everything, if we are rendering the backside of the library.
    
    # Change the Name and Value attribute tag for each element to text tags for display
    UtilVisitors.RetagNameAttribute(EagleLayers(library.getLayers())).visit(library.getRoot())
    UtilVisitors.RetagValueAttribute(EagleLayers(library.getLayers())).visit(library.getRoot())

    # Remove the Name and Value text tags from the library
    UtilVisitors.RemoveNameVariable(EagleLayers(library.getLayers())).visit(library.getRoot())
    UtilVisitors.RemoveValueVariable(EagleLayers(library.getLayers())).visit(library.getRoot())

    # Transforms the texts within the Elements that aren't part of tName or bName
    UtilVisitors.TranformElementText(EagleLayers(library.getLayers())).visit(library.getRoot())

    # Determines if layer is on the backside of library, and sets onBackside = True if it is
    UtilVisitors.TopBottomAttr(EagleLayers(library.getLayers())).visit(library.getRoot())

    board = library
    execfile(gcam) # execute the gcam file.

    for r in library.getRoot().findall("./drawing/library/packages/package"):
        print "Here"
        bbox = Dingo.Component.get_bounding_rectangle(r)

        out = svgwrite.Drawing(os.path.join(outputDir,(r.get("name")+".svg").replace("/","")),
                               size=(str(bbox.width), str(bbox.height)))
        PSVGVisitor.PSVGVisitor(drawOrigins, out, False, False).go(r)
        #Move the entire drawing so it fits within the bounding box
        #Viewboxes suck
        translation = "translate({0},{1})".format(-bbox.left(), -bbox.bot())
        move_group = svgwrite.container.Group(transform=translation)
        for e in out.elements:
            move_group.add(e)
        out.elements = [move_group]
        out.save()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Tool for auto-generating packages for packages in a library.  For each package named 'FOO', produce <output>/FOO.svg")
    parser.add_argument("--lbr", required=True,  type=str, nargs=1, dest='lbrfile', help="lbr file")
    parser.add_argument("--output", required=True, type=str, nargs=1, dest='output', help="output directory")
    parser.add_argument("--gcam", required=True, type=str, nargs=1, dest='gcamfile', help="gcam file")
    parser.add_argument("--draworigins", required=False, action='store_true', dest='draworigins', help="Draw origins for sub elements")
    args = parser.parse_args()
    library = EagleLibrary(args.lbrfile[0])


    buildPackageSVGs(library=library,
                     gcam=args.gcamfile[0],
                     outputDir=args.output[0],
                     drawOrigins=args.draworigins);
    
