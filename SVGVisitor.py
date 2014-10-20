from lxml import etree as ET
from EagleVisitor import *
from GadgetCAM import *
import svgwrite
import math

class SVGVisitor(EagleVisitor):
    groupStack = []
    dtg = None
    _drawOrigins = False
    
    def __init__(self, drawOrigins, output, flipBoard,mirror):
        self.groupStack = []
        self.dwg = output
        self._drawOrigins = drawOrigins
        self.flipBoard = flipBoard
        self._mirrored = mirrored

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
                assert(0) # this code is wrong but I don't know why.
                r = e.get("rot")[2:]
#                r = e.get("rot")[2:]
                scale = "scale(-1,1)"
            else:
                r = str(-float(e.get("rot")[1:]))
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
        self.pushGroup(self.dwg)
        if self.flipBoard:
            g = self.dwg.g(transform="scale(-1,-1)")
        else:
            g = self.dwg.g(transform="scale(1,-1)")
        self.pushGroup(g)

        if self._mirrored:
            g = self.dwg.g(transform="scale(-1,1)")
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
