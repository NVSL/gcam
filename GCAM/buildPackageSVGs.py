#!/usr/bin/env python
import argparse
import os
import sys

from lxml import etree as ET
import svgwrite

from GadgetCAM import *
import GadgetronConfig as gtron

from EagleUtil.EagleLibrary import *
from EagleUtil.EagleLayers import *
import PSVGVisitor 
import UtilVisitors
import Dingo.DingoComponent as Component
import Dingo
from io import StringIO

def preprocessLibrary(libname, gcam):
    library = EagleLibrary(libname)
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
    return library

def getSVGForPackage(library, drawOrigins, package, filename):
    r = library.getRoot().find("./drawing/library/packages/package[@name='{}']".format(package))
    assert r is not None
    bbox = Dingo.DingoComponent.get_bounding_rectangle(r)
    if bbox is None:
        sys.stderr.write("{0} has no bounding box\n".format(package))
        return
    out = svgwrite.Drawing(filename, size=(str(bbox.width) + "mm", str(bbox.height) + "mm"))
    out.viewbox(bbox.left(), bbox.top(), bbox.width, bbox.height)

    PSVGVisitor.PSVGVisitor(drawOrigins, out, False, False).go(r)
    move_group = svgwrite.container.Group()
    move_group.attribs["class"]= "gtron_package_template";
    for e in out.elements:
        move_group.add(e)
    out.elements = [move_group]
    svg_data = out.tostring()

    xml_data = ET.parse(StringIO(svg_data))
    xml_data.getroot().set("eagle_library",library.name)
    xml_data.getroot().set("eagle_package",r.get("name"))
    for i in xml_data.getroot().xpath("//svg:g[@class='gtron_package_template']",
                                      namespaces={'svg': 'http://www.w3.org/2000/svg'}):
        i.set("{http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd}insensitive","true")

    ET.SubElement(xml_data.getroot(), "{http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd}namedview",
                  {"showborder":"false"})
    open(filename,"w").write(ET.tostring(xml_data));


def buildPackageSVGs(libname,outputDir,gcam,drawOrigins=False):
    
    # This step expand each 'element' tag to include a copy of the package from
    # the library.  Now, we can style/manipulate/etc. each of the instances
    # independently.

    library = preprocessLibrary(libname, gcam);

    for r in library.getRoot().findall("./drawing/library/packages/package"):
        name = os.path.join(outputDir,(r.get("name")+".svg").replace("/",""))
        data = getSVGForPackage(library, drawOrigins, r.get("name"), name);
        

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tool for auto-generating packages for packages in a library.  For each package named 'FOO', produce <output>/FOO.svg")
    parser.add_argument("--lbr", required=True,  type=str, nargs=1, dest='lbrfile', help="lbr file")
    parser.add_argument("--output", required=True, type=str, nargs=1, dest='output', help="output directory")
    parser.add_argument("--gcam", required=True, type=str, nargs=1, dest='gcamfile', help="gcam file")
    parser.add_argument("--draworigins", required=False, action='store_true', dest='draworigins', help="Draw origins for sub elements")
    args = parser.parse_args()


    buildPackageSVGs(libname=args.lbrfile[0],
                     gcam=args.gcamfile[0],
                     outputDir=args.output[0],
                     drawOrigins=args.draworigins);
    
