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
from EagleVisitor import *
import svgwrite
import math

parser = argparse.ArgumentParser(description="Tool for auto-generating packages for breakout boards")

parser.add_argument("--brd", required=True,  type=str, nargs=1, dest='brdfile', help="brd file")
parser.add_argument("--output", required=True, type=str, nargs=1, dest='output', help="output svg file")
parser.add_argument("--gcam", required=True, type=str, nargs=1, dest='gcamfile', help="gcam file")
parser.add_argument("--draworigins", required=False, action='store_true', dest='draworigins', help="Draw origins for sub elments?")
parser.add_argument("--flip", action='store_true', dest='flipboard', help="exclude vias and holes for pads.")

args = parser.parse_args()


def Style(**args):
    return args

def CamPass(brd, paths, layers, **args):
    layerMap = EagleLayers(brd.getLayers())
    root = brd.getRoot()
    for p in paths:
        for e in root.findall(p):
            name = None
            if e.get("layer") is not None:
                try:
                    name = layerMap.numberToName(e.get("layer"))
                except EagleError:
                    name = e.get("layer")
                    
            if name in layers or name is None and None in layers:
                e.set("camstyled", "1")
                for a in args["default"]:
                    e.set("cam_" + a, args["default"][a])
                if "refinements" in args and e.tag in args["refinements"]:
                    for a in args["refinements"][e.tag]:
                        e.set("cam_" + a, args["refinements"][e.tag][a])


def CamAttributes(element):
    r = {}
    for i in element.attrib:
        if i[0:4] == "cam_":
            r[i[4:]] = element.get(i)
#    print element.attrib
    del r["include"]
#    print r
    return r

class EchoVisitor(EagleVisitor):

    def package_pre(self, element):
        print "open " + element.tag
    def package_post(self, element):
        print "close " + element.tag

    def wire_pre(self, element):
        print element.tag

class SVGVisitor(EagleVisitor):
    groupStack = []
    dtg = None
    _drawOrigins = False
    def __init__(self, drawOrigins):
        self.groupStack = []
        self.dwg = None
        self._drawOrigins = drawOrigins

    def pushGroup(self, g):
        if len(self.groupStack) > 0:
            self.groupStack[-1].add(g)
        self.groupStack.append(g)
#        print "here " + str(g)

    def currentGroup(self):
        return self.groupStack[-1]

    def popGroup(self):
        self.groupStack.pop()

    def targeted(self, element):
        if element.get("camstyled") and element.get("camstyled") == "1":
            if element.get("cam_include"):
                return element.get("cam_include") == "1"
            else:
                return True
        else:
            return False

    def decendFilter(self,element):
        return True;
    
    def visitFilter(self, element):
        return self.targeted(element)

    def computeSVGRotation(self, e):
        if e.get("rot") is not None:
            if e.get("rot")[0] == "M":
                r = e.get("rot")[2:]
                scale = "scale(-1,1)"
            else:
                r = e.get("rot")[1:]
                scale = ""
        else:
            scale = ""
            r = "0"

        if r != "0":
            rotate ="rotate(" + str((float(r))) + ")"        
        else:
            rotate = ""

        if rotate == "" and scale == "":
            return ""
        else:
            return rotate + " " + scale
    
    def computeSVGTranslation(self, e, x, y):
        if x is None:
            x = e.get("x")
            y = e.get("y")

        if x is not None:
            return "translate("+ x + "," + y + ")"
        else:
            return ""

    def preTransform(self, element, x=None, y=None):
        rotate = self.computeSVGRotation(element)
        translate = self.computeSVGTranslation(element, x, y)
        if rotate != "" or translate != "":
            g = self.dwg.g(transform=translate +  " " + rotate)# + " " + translate)
            self.pushGroup(g)

    def postTransform(self, element,x=None, y=None):
        rotate = self.computeSVGRotation(element)
        translate = self.computeSVGTranslation(element, x, y)
        if rotate != "" or translate != "":
            self.popGroup()
        
    def styleAndAttach(self, element, drawingPiece):
        drawingPiece.update(CamAttributes(element))
        self.currentGroup().add(drawingPiece)
        
    def drawOrigin(self):
 #       print "here"
 #       print self.currentGroup()
        if self._drawOrigins:
            l1 = self.dwg.line(start=(-1,0), end=(1,0), stroke="red", stroke_width="0.1")
            l2 = self.dwg.line(start=(0,-1), end=(0,1), stroke="red", stroke_width="0.1")
            self.currentGroup().add(l1)
            self.currentGroup().add(l2)

    #########################################

    def drawing_pre(self, element):
        self.dwg = svgwrite.Drawing(args.output[0], size=("1000mm","1000mm"), viewBox="0 0 1000 1000")
        self.pushGroup(self.dwg)
        if args.flipboard:
            g = self.dwg.g(transform="scale(-1,-1)")
        else:
            g = self.dwg.g(transform="scale(1,-1)")
        self.pushGroup(g)

    def drawing_post(self, element):
        self.dwg.save()

    #########################################

    def element_pre(self, e):
        self.preTransform(e)
        self.drawOrigin()

    def element_post(self, e):
        self.postTransform(e)

    #########################################

    def hole_pre(self, e):
        self.preTransform(e)
        c = self.dwg.circle(center=(0,0),
                            r=str(float(e.get("drill"))/2))
        self.styleAndAttach(e,c)
        self.postTransform(e)

    #########################################

    def circle_pre(self, e):
        self.preTransform(e)
        c = self.dwg.circle(center=(0,0),
                            r=e.get("radius"))
        self.styleAndAttach(e,c)
        self.postTransform(e)

    ########################################

    def pad_pre(self, e):
        self.preTransform(e)
        p = self.dwg.circle(center=(0,0),
                            r=str(float(e.get("drill"))/2))
        self.styleAndAttach(e,p)
        self.postTransform(e)
        
    ########################################

    def wire_pre(self, e):
#        self.preTransform(e)
        if e.get("curve") and e.get("curve") != "0":
            x1 = float(e.get("x1"))
            x2 = float(e.get("x2"))
            y1 = float(e.get("y1"))
            y2 = float(e.get("y2"))

            curve = float(e.get("curve"))
            sweep = "+" if curve > 0 else "-"
            curve = -curve if curve < 0 else curve

            diag = math.hypot((x2-x1), (y2-y1))
            radius = diag * math.sin((math.radians((180-curve)/2)))/math.sin(math.radians(curve))
            path = self.dwg.path()
            path.push("m " + str(x1) + " " + str(y1))
            path.push_arc((x2,y2), 0, (radius,radius), False, sweep, True)
            self.styleAndAttach(e, path)
        else:
            line = self.dwg.line(start=(e.get("x1"), e.get("y1")),
                                 end=(e.get("x2"), e.get("y2")))
            self.styleAndAttach(e, line)
#        self.postTransform(e)
       
    ########################################

    def rectangle_pre(self, e):
        x1 = float(e.get("x1"))
        x2 = float(e.get("x2"))
        y1 = float(e.get("y1"))
        y2 = float(e.get("y2"))
        x1 = min(x1,x2)
        x2 = max(x1,x2)
        y1 = min(y1,y2)
        y2 = max(y1,y2)
        
        hx = (x2-x1)/2
        hy = (y2-y1)/2
        self.preTransform(e, str(x1 + hx), str(y1 + hy))
        rect = self.dwg.rect(insert=(-hx,-hy),
                             size=(x2-x1, y2-y1))
        self.styleAndAttach(e, rect)
        self.postTransform(e,str(x1 - hx), str(y1 - hy))
        
    ########################################

    def polygon_pre(self, e):
        vertices=[]
        for v in e.findall("vertex"):
            vertices.append((v.get("x"), v.get("y")))
            
        poly = self.dwg.polygon(points=vertices)
        self.styleAndAttach(e, poly)

    def text_pre(self, e):
        self.preTransform(e)
        # I'm not sure why its necessary to flip the text mannually, but wihtout it, the text renders upside down in both inkscape and chrome.
        text = self.dwg.text(e.text,
                             insert=(0,str(float(e.get("size"))/2)),
                             transform="scale(1,-1)")

        style = []
        style.append(["font-size", e.get("size")])

        if e.get("font") == "vector":
            style.append(["font","Arial"])
        elif e.get("font") == "proportonal":
            style.append(["font","Arial"])
        elif e.get("font") == "fixed":
            style.append(["font","Courier"])
        else:
            style.append(["font","Arial"])

        if e.get("align"):
            style.append(["text-align", e.get("align")])
            if e.get("align") == "center":
                style.append(["text-anchor", "middle"])
            elif e.get("align") == "left":
                style.append(["text-anchor", "start"])
            elif e.get("align") == "right":
                style.append(["text-anchor", "end"])
        

        text.update({"style": ";".join(map(lambda x:":".join(x), style))})
        self.styleAndAttach(e, text)
        self.postTransform(e)
        
class FlipVisitor(EagleVisitor):
    _flipped = False
    _layers = None
    def __init__(self, layers, flipped=False):
        self._flipped = flipped
        self._layers = layers

    def layer_pre(self, e):
        pass
    def layer_post(self, e):
        pass

    def default_pre(self, e):
        if self._flipped:
            if e.get("layer") is not None:
                try:
                    e.set("layer", self._layers.flipByNumber(e.get("layer")))
                except EagleError:
                    e.set("layer", self._layers.flipByName(e.get("layer")))

    def element_pre(self, e):
        if e.get("rot") is not None:
            if e.get("rot")[0] == "M":
                self._flipped = not self._flipped
    
    def element_post(self, e):
        if e.get("rot") is not None:
            if e.get("rot")[0] == "M":
                self._flipped = not self._flipped

class NamedLayers(EagleVisitor):
    _layers = None
    def __init__(self, layers):
        self._layers = layers

    def default_pre(self, e):
        if e.get("layer"):
            e.set("layer", self._layers.numberToName(e.get("layer")))

    def layer_pre(self, e):
        pass
    def layer_post(self, e):
        pass

board = EagleBoard(args.brdfile[0])

board.instantiatePackages()

NamedLayers(EagleLayers(board.getLayers())).visit(board.getRoot())
FlipVisitor(EagleLayers(board.getLayers()), args.flipboard).visit(board.getRoot())

execfile(args.gcamfile[0])

SVGVisitor(args.draworigins).visit(board.getRoot())
