from lxml import etree as ET
from EagleUtil.EagleVisitor import *
from GadgetCAM import *
import svgwrite
import math
import numpy as np

class PSVGVisitor(EagleVisitor):
    groupStack = []
    backside_elementStack = []
    dtg = None
    _drawOrigins = False
    _dimension_wires = []
    _dimension_path = None
    _dimension_element = None

    _front_wire = None
    _back_wire = None
    _baseboard = None
    _backside = None

    _top_wires = []
    _top_path = None
    _bottom_wires = []
    _bottom_path = None

    _tFaceplate = None
    _holes = []
    
    def __init__(self, drawOrigins, output, flipBoard, mirrored, tFaceplate=None):
        self.groupStack = []  #these groups represent a stack of coordinate systems we will render items into.
        self.backside_groupStack = []
        self.dwg = output #output drawing
        self._drawOrigins = drawOrigins  # flag to draw origins (for debugging)
        self.flipBoard = flipBoard  # flag if we are drawing the back side of the board
        self._mirrored = mirrored   # flag if we the output should be mirrored.
        self._dimension_wires = [] # these hold the stack of wires that draw the outline of the board
        self._dimension_path = None
        self._dimension_element = None

        self._front_wire = None
        self._back_wire = None
        self._baseboard = None # group that holds the base board
        self._backside = None # group that holds all things that belong on the back of the basboard

        self._top_wires = [] # these hold the stack of wires from top electrical wiring layer
        self._top_path = self.dwg.path(d="M 0,0")
        self._bottom_wires = [] # these hold the stack of wires from bottom electrical wiring layer
        self._bottom_path = self.dwg.path(d="M 0,0")

        # === holes related things ===
        self._tFaceplate = tFaceplate # this is a collection of board paths for tFaceplate 
        self._holes = [] # these hold the stack of holes that need to be drawn on the board

    def pushGroup(self, g, group_stack=None):
        if group_stack is None:
            group_stack = self.groupStack

        if len(group_stack) > 0:
            group_stack[-1].add(g)
        group_stack.append(g)

    def currentGroup(self, group_stack=None):
        if group_stack is None:
            group_stack = self.groupStack
        return group_stack[-1]

    def popGroup(self, group_stack=None):
        if group_stack is None:
            group_stack = self.groupStack
        group_stack.pop()

    def flattenGroup(self, x=None, y=None, group_stack=None):
        if group_stack is None:
            group_stack = self.groupStack

        first = True
        matrices = []
        f = 1
        if x is not None and y is not None:
            xt = x
            yt = y
        else:
            xt = yt = 0

        # answer = np.matrix([[0],[0],[1]])
        for x in range(1, len(group_stack)-1):
            # this is going from the bottom up excluding the last scale(1,-1)
            all_transform = group_stack[-x]['transform']
            
            # must do the rotate transformation first, then the translate
            for transform in all_transform.strip(" ").split(" ")[::-1]:
                transform_type = transform[0:transform.index("(")]

                if transform_type == "translate":
                    # retrieve the values and split by the commas
                    value = transform[transform.index("(") + 1:transform.rindex(")")].split(",")

                    # add the information into the matrix
                    m = np.zeros(shape=(3,3))
                    m[0][2] = float(value[0])
                    m[1][2] = float(value[1])
                    if not first:
                        f = f + m
                    else:
                        f = np.dot(f, m)
                        first = False

                elif transform_type == "rotate":
                    value = transform[transform.index("(") + 1:transform.rindex(")")].split(",")

                    m = np.zeros(shape=(3,3))
                    m[2][2] = 1
                    v = math.radians(float(value[0]))
                    m[0][0] = math.cos(v)
                    m[0][1] = -math.sin(v)
                    m[1][0] = math.sin(v)
                    m[1][1] = math.cos(v)

                    f = np.dot(m, f)
                    first = False

                elif transform_type == "scale" :
                    value = transform[transform.index("(") + 1:transform.rindex(")")].split(",")
                    m = np.zeros(shape=(3,3))
                    m[2][2] = 1
                    sx = float(value[0])
                    sy = float(value[1])
                    m[0][0] = sx
                    m[1][1] = sy

                    f = np.dot(m, f)
                    first = False


        base = np.matrix([[xt],[yt],[1]])
        answer = np.dot(f, base)
        return (float(answer[0][0]), float(answer[1][0]))


    def targeted(self, element):  
        if element.get("camstyled") and element.get("camstyled") == "1":
            if element.get("cam_include"):
                return element.get("cam_include") == "1"
            else:
                return True
        else:
            return False

    def decendFilter(self,element):  
        # this is inhereted from XML visitor.  It is 
        # a predicate that returns true if we should
        # decend into this tag.
        
        return True;
    
    def visitFilter(self, element):
        # this is inhereted from XML visitor.  It is a predicate that returns
        # true if we should visit the element (it is possible to decend into
        # the element without visiting it).
        return self.targeted(element)

    def computeSVGRotation(self, e):
        # else/default
        scale = ""
        r = "0"

        if e.get("rot") is not None:
            # SMR###
            if e.get("rot")[0] == "S":
                if e.get("rot")[1] == "M":
                    r = -1*float(e.get("rot")[3:])
                    if r != '0' or r != '-0':
                        scale = "scale(-1,1)"
                else:
                    r = e.get("rot")[2:]
            # MR###
            elif e.get("rot")[0] == "M":
                r = -1*math.fabs(float(e.get("rot")[2:]))
                scale = "scale(-1,1)"
                if math.fabs(float(r)) >= 180:
                    if e.tag == "text":
                        if e.get('align') is None:
                            e.set('align', 'right')
                        if e.get("element_text")!="True":
                            r = str(float(r) - 180)
            # R###
            else:
                r = str(float(e.get("rot")[1:]))
                scale = ""
                if float(r) >= 180:
                    if e.tag == "text":
                        if e.get('align') is None:
                            e.set('align', 'right')
                        if e.get("element_text")!="True":
                            r = str(float(r) - 180)

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

    def pushPadArc(self, curve, x, y, d, path):
        sweep = "+" if curve > 0 else "-"
        curve = -curve if curve < 0 else curve
        radius = d/(2*math.sin(math.radians(curve)/2))
        path.push_arc((x,y), 0, (radius,radius), False, sweep, True)

    def pushCirclePath(self, p, x, y, r):
        p.push("M " + str(x) + " " + str(y))
        p.push("m " + str(-r) + " " + str(0))
        p.push("a " + str(r) + "," + str(r) + " 0 1, 1 " + str(2*r) + " ,0")
        p.push("a " + str(r) + "," + str(r) + " 0 1, 1 " + str(-2*r) + " ,0")

    def preTransform(self, element, x=None, y=None):
        rotate = self.computeSVGRotation(element)
        translate = self.computeSVGTranslation(element, x, y)
        if rotate != "" and translate != "":
            self.pushGroup(self.dwg.g(transform=translate +  " " + rotate))
            self.pushGroup(self.dwg.g(transform=translate +  " " + rotate), group_stack=self.backside_groupStack)
        elif rotate != "":
            self.pushGroup(self.dwg.g(transform=rotate))
            self.pushGroup(self.dwg.g(transform=rotate), group_stack=self.backside_groupStack)
        elif translate != "":
            self.pushGroup(self.dwg.g(transform=translate))
            self.pushGroup(self.dwg.g(transform=translate), group_stack=self.backside_groupStack)


    def postTransform(self, element, x=None, y=None):
        rotate = self.computeSVGRotation(element)
        translate = self.computeSVGTranslation(element, x, y)
        if rotate != "" or translate != "":
            self.popGroup()
            self.popGroup(group_stack=self.backside_groupStack)

    def preTextTransform(self, element, x=None, y=None):
        rotate = self.computeSVGRotation(element)
        translate = self.computeSVGTranslation(element, x, y)
        if rotate != "" and translate != "":
            self.pushGroup(self.dwg.g(transform=translate +  " " + rotate))
            self.pushGroup(self.dwg.g(transform=translate +  " " + rotate), group_stack=self.backside_groupStack)
        elif rotate != "":
            self.pushGroup(self.dwg.g(transform=rotate))
            self.pushGroup(self.dwg.g(transform=rotate), group_stack=self.backside_groupStack)
        elif translate != "":
            self.pushGroup(self.dwg.g(transform=translate))
            self.pushGroup(self.dwg.g(transform=translate), group_stack=self.backside_groupStack)

    def postTextTransform(self, element,x=None, y=None):
        rotate = self.computeSVGRotation(element)
        translate = self.computeSVGTranslation(element, x, y)
        if rotate != "" or translate != "":
            self.popGroup()
            self.popGroup(group_stack=self.backside_groupStack)

    def styleAndAttach(self, element, drawingPiece):
        drawingPiece.update(CamAttributes(element))
        if element.get("onBackside")=="True":
            self.currentGroup(group_stack=self.backside_groupStack).add(drawingPiece)
        else:
            self.currentGroup().add(drawingPiece)
        
    def drawOrigin(self):
        if self._drawOrigins:
            l1 = self.dwg.line(start=(-1,0), end=(1,0), stroke="red", stroke_width="0.1")
            l2 = self.dwg.line(start=(0,-1), end=(0,1), stroke="red", stroke_width="0.1")
            self.currentGroup().add(l1)
            self.currentGroup().add(l2)

    def drawWirePath(self, e, wires, attached=False, attached_element=None):
        index = {}
        dimension_layer = False

        # creates dictionary of wires
        for wire in wires:
            key = "%s, %s" % (float(wire.get("x1")), float(wire.get("y1")))
            if key not in index.keys():
                value = []
                value.append(wire)
                index[key] = value
            else:
                value = index[key]
                value.append(wire)
                index[key] = value

        p = None
        while len(index)>0:
            # we need to do this otherwise it'll throw a TypeError where '' is not 
            # a valid value for attribute 'd'

            if p is None:
                p = self.dwg.path(d="M 0,0")

            value = index[index.keys()[0]]
            next = value[0]
            del value[0]

            # add styling if needed for the wire
            style = []
            if next.get("layer") == "Dimension":
                dimension_layer = True
            elif next.get("layer")=="Top":
                style.append(["stroke", "#D3D3D3"]) #D3D3D3 pale silver
            elif next.get("layer")=="Bottom":
                style.append(["stroke", "#D3D3D3"]) 

            for key in CamAttributes(e).keys():
                adjusted_key = key.replace("_","-")
                if adjusted_key == "stroke-width":
                    if float(next.get("width"))>0:
                        style.append(["stroke-width", next.get("width")])
                    else:
                        style.append([adjusted_key, CamAttributes(e)[key]])
                else:
                    style.append([adjusted_key, CamAttributes(e)[key]])
            if len(style)>0:
                p.update({"style": ";".join(map(lambda x:":".join(x), style))})

            # start adding wiring to path
            x1 = float(next.get("x1"))
            x2 = float(next.get("x2"))
            y1 = float(next.get("y1"))
            y2 = float(next.get("y2"))
            # dict bookkeeping
            key = "%s, %s" % (x1, y1)
            if len(value)==0: 
                del index[key]
            key = "%s, %s" % (x2, y2) # change key to the end of the wire

            # draw out the first wire
            p.push("M" + str(x1) + " " + str(y1))
            # actually draw the wire path
            if next.get("curve") and next.get("curve") != "0": # check if curved line
                # magical math convert eagle arcs into SVG arcs.
                curve = float(next.get("curve"))
                sweep = "+" if curve > 0 else "-"
                # curve = -curve if curve < 0 else curve
                curve = math.fabs(curve)
                large_arc = True if curve >= 180 else False
                diag = math.hypot((x2-x1), (y2-y1))
                radius = diag/(2*math.sin(math.radians(curve)/2))

                p.push_arc((x2,y2), 0, (radius,radius), large_arc, sweep, True)

            else:
                p.push("L" + str(x2) + " " + str(y2))
            

            # do the same thing with the rest of the wires
            while(index.has_key(key)):

                # fetch info from dict and do some bookkeeping
                value = index[key] # fetch entry in dict with matching start point
                next = value[0] # get the first entry in returned value
                del value[0] # remove that wire from dict
                if len(value)==0: # remove the key from dict if no more wires in value
                    del index[key]

                # actually draw the wire path
                if next.get("curve") and next.get("curve") != "0": # check if curved line
                    x1 = float(next.get("x1"))
                    x2 = float(next.get("x2"))
                    y1 = float(next.get("y1"))
                    y2 = float(next.get("y2"))

                    # magical math convert eagle arcs into SVG arcs.
                    curve = float(next.get("curve"))
                    sweep = "+" if curve > 0 else "-"
                    # curve = -curve if curve < 0 else curve
                    curve = math.fabs(curve)
                    large_arc = True if curve >= 180 else False
                    diag = math.hypot((x2-x1), (y2-y1))
                    radius = diag/(2*math.sin(math.radians(curve)/2))

                    p.push_arc((x2,y2), 0, (radius,radius), large_arc, sweep, True)
                    key = "%s, %s" % (x2, y2)

                else:
                    x1 = float(next.get("x1"))
                    x2 = float(next.get("x2"))
                    y1 = float(next.get("y1"))
                    y2 = float(next.get("y2"))
                    p.push("L" + str(x2) + " " + str(y2))
                    key = "%s, %s" % (x2, y2)
            # end while loop
            if attached:
                # self.styleAndAttach(attached_element, p)
                attached_element.add(p)
            else:
                self.styleAndAttach(e, p)

            if not dimension_layer:
                p = self.dwg.path(d="M 0,0")

        # draw holes later in if Dimension
        if dimension_layer:
            self._dimension_path = p
            self._dimension_element = e

        # if p is not None and not attached:
        #     self.styleAndAttach(e, p)


    def drawHoles(self):
        p = self._dimension_path
        # e = self._dimension_element
        if p:
            for hole_attr in self._holes:
                x = hole_attr["x"]
                y = hole_attr["y"]
                r = hole_attr["radius"]
                if self._mirrored:
                    p.push("M " + str(-x) + " " + str(y))
                else:
                    p.push("M " + str(x) + " " + str(y))
                p.push("m " + str(-r) + " " + str(0))
                p.push("a " + str(r) + "," + str(r) + " 0 1, 1 " + str(2*r) + " ,0")
                p.push("a " + str(r) + "," + str(r) + " 0 1, 1 " + str(-2*r) + " ,0")
        # we don't need to styleAndAttach here because we already did that in drawWire for dimension_wires
        # self.styleAndAttach(e, p)

    def drawBackside(self, group_stack):
        while len(group_stack)>0 :
            element = group_stack.pop()
            self._backside.add(element)

    #########################################

    def setup(self):
        #print "starting drawing_pre"
        self.pushGroup(self.dwg)
        self.pushGroup(self.dwg, group_stack=self.backside_groupStack)
        if self.flipBoard:
            self._backside = self.dwg.g(transform="scale(-1,-1)")
            self.pushGroup(self._backside, group_stack=self.backside_groupStack)
            self.pushGroup(self.dwg.g(transform="scale(-1,-1)"))
            
        else:
            self._backside = self.dwg.g(transform="scale(1,-1)")
            self.pushGroup(self._backside, group_stack=self.backside_groupStack)
            self.pushGroup(self.dwg.g(transform="scale(1,-1)"))

        if self._mirrored:
            self._backside = self.dwg.g(transform="scale(-1,1)")
            self.pushGroup(self._backside, group_stack=self.backside_groupStack)
            self.pushGroup(self.dwg.g(transform="scale(-1,1)"))

        self.drawOrigin()
        
    # *_post functions are called after decending into it and visiting all its decedents.   If you just define _post functions, you'll get a post-order traversal.
    def teardown(self):
        self.drawHoles()
        # last save
        self.dwg.save()
        #print "finished drawing"

    #########################################

    def element_pre(self, e):
        print "drawing element: name = %s" % (e.get("name"))
        # print ET.tostring(e)
        self.preTransform(e)
        # self.drawOrigin()

    def element_post(self, e):
        self.postTransform(e)

    #########################################

    def attribute_pre(self, e):
        self.drawOrigin()

    def attribute_post(self, e):
        pass

    #########################################

    def hole_pre(self, e):
        self.preTransform(e)
        xt, yt = self.flattenGroup() # both are float type
        attr = {}
        attr["x"] = xt
        attr["y"] = yt
        attr["radius"] = float(e.get("drill"))/2
        self._holes.append(attr)
        # here, we are only going to draw the outline of the hole as a path
        c = self.dwg.circle(center=(0,0),r=str(float(e.get("drill"))/2))
        self.styleAndAttach(e,c)
        self.postTransform(e)

    #########################################

    def circle_pre(self, e):
        self.preTransform(e)
        c = self.dwg.circle(center=(0,0),
                            r=e.get("radius"))
        self.styleAndAttach(e,c)
        if self._tFaceplate is not None and (e.get("layer")=="tFaceplate" or e.get("layer")=="bFaceplate"):
            print "circle tFaceplate"
            r = float(e.get("radius"))
            xt, yt = self.flattenGroup()
            self._tFaceplate.push("M " + str(xt) + " " + str(yt))
            self._tFaceplate.push("m " + str(-r) + " " + str(0))
            self._tFaceplate.push("a " + str(r) + "," + str(r) + " 0 1, 1 " + str(2*r) + " ,0")
            self._tFaceplate.push("a " + str(r) + "," + str(r) + " 0 1, 1 " + str(-2*r) + " ,0")
        self.postTransform(e)

    #########################################

    def via_pre(self, e):
        self.preTransform(e)
        xt, yt = self.flattenGroup() # both are float type
        attr = {}
        attr["x"] = xt
        attr["y"] = yt
        r = float(e.get("drill"))/2*1.5 # the size for the radius is purely guestimated by eyeballing it
        attr["radius"] = r
        self._holes.append(attr)
        
        p = self.dwg.path(d="M 0,0")
        self.pushCirclePath(p, 0, 0, r)
        self.pushCirclePath(p, 0, 0, r/2)
        p.push("Z") 

        self.styleAndAttach(e,p)
        self.postTransform(e)

    ########################################

    def pad_pre(self, e):
        self.preTransform(e)

        if e.get("shape") == "octagon":
            if e.get("diameter"):
                diameter = float(e.get("diameter"))
            else:
                drill = float(e.get("drill"))
                diameter = 0.351 + 1.251*drill

            r = diameter/2
            x = 0
            y = 0
            n = 8

            # starting point of octagon
            i = 0
            temp_x = r * math.cos(2 * math.pi * i / n)
            temp_y = r * math.sin(2 * math.pi * i / n)
            p = self.dwg.path(transform="rotate(22.5)")
            # p = self.dwg.path(d="M 0,0")

            p.push("M " + str(temp_x) + " " + str(temp_y))
            i+=1
            while i < n+1:
                temp_x = r * math.cos(2 * math.pi * i / n)
                temp_y = r * math.sin(2 * math.pi * i / n)
                p.push("L " + str(temp_x) + " " + str(temp_y))
                i+=1
            p.push("Z") 

            # draw the inner circle
            r = float(e.get("drill"))/2
            inner_radius = r
            self.pushCirclePath(p, x, y, r)
            p.push("Z") 

        elif e.get("shape") == "square":
            if e.get("diameter"):
                diameter = float(e.get("diameter"))
            else:
                drill = float(e.get("drill"))
                diameter = 0.351 + 1.251*drill

            # draw the outer square
            r = diameter/2
            x = 0
            y = 0
            p = self.dwg.path(d="M 0,0")
            # starting point
            p.push("M " + str(x-r) + " " + str(y+r))
            # top side
            p.push("h " + str(2*r))
            # left side
            p.push("v " + str(-2*r))
            # bottom side
            p.push("h " + str(-2*r))
            # right arc
            p.push("v " + str(2*r))

            # draw the inner circle
            r = float(e.get("drill"))/2
            inner_radius = r
            self.pushCirclePath(p, x, y, r)
            # close path
            p.push("Z") 
            
        elif e.get("shape") == "long":
            if e.get("diameter"):
                diameter = float(e.get("diameter"))
            else:
                drill = float(e.get("drill"))
                diameter = 0.351 + 1.251*drill

            # draw the outer oval shape
            r = diameter/2
            x = 0
            y = 0
            p = self.dwg.path(d="M 0,0")
            # starting point
            p.push("M " + str(x-r) + " " + str(y+r))
            # top side
            p.push("h " + str(2*r))
            # left arc
            self.pushPadArc(-180, (x+r), (y-r), diameter, p)
            # bottom side
            p.push("h " + str(-2*r))
            # right arc
            self.pushPadArc(-180, (x-r), (y+r), diameter, p)
            p.push("Z") 

            # draw the inner circle
            r = float(e.get("drill"))/2
            inner_radius = r
            self.pushCirclePath(p, x, y, r)
            # close path
            p.push("Z") 

        # default pad shape is "round"
        else:
            if e.get("diameter"):
                diameter = float(e.get("diameter"))
            else:
                drill = float(e.get("drill"))
                diameter = 0.351 + 1.251*drill

            # draw the outer circle
            r = diameter/2
            x = 0
            y = 0
            p = self.dwg.path(d="M 0,0")
            self.pushCirclePath(p, x, y, r)

            # draw the inner circle
            r = float(e.get("drill"))/2
            inner_radius = r
            self.pushCirclePath(p, x, y, r)

            # close path
            p.push("Z") 

        # add pad's hole to hole list
        xt, yt = self.flattenGroup() # both are float type
        attr = {}
        attr["x"] = xt
        attr["y"] = yt
        attr["radius"] = inner_radius
        self._holes.append(attr)

        self.styleAndAttach(e,p)
        self.postTransform(e)

    ########################################

    def wire_pre(self, e):        

        if e.get("layer")=="Top":
            # drawingPiece = self.dwg.path(d="M 0,0")
            # drawingPiece.push("M0 0")
            # drawingPiece.update(CamAttributes(e))
            # print CamAttributes(e)
            self._top_wires.append(e)

        elif e.get("layer")=="Bottom":
            self._bottom_wires.append(e)

        elif e.get("layer")=="Dimension":
            self._dimension_wires.append(e)

        elif e.get("curve") and e.get("curve") != "0":

            x1 = float(e.get("x1"))
            x2 = float(e.get("x2"))
            y1 = float(e.get("y1"))
            y2 = float(e.get("y2"))

            # magical math convert eagle arcs into SVG arcs.
            curve = float(e.get("curve"))
            sweep = "+" if curve > 0 else "-"
            # curve = -curve if curve < 0 else curve
            curve = math.fabs(curve)
            large_arc = True if curve >= 180 else False
            diag = math.hypot((x2-x1), (y2-y1))
            radius = diag/(2*math.sin(math.radians(curve)/2))

            path = self.dwg.path(d="M 0,0")
            path.push("M " + str(x1) + " " + str(y1))
            path.push_arc((x2,y2), 0, (radius,radius), large_arc, sweep, True)

            style = []
            if float(e.get("width"))>0:
                style.append(["stroke-width", e.get("width")])
                path.update({"style": ";".join(map(lambda x:":".join(x), style))})
            self.styleAndAttach(e, path)

        else:
            line = self.dwg.line(start=(e.get("x1"), e.get("y1")),
                                 end=(e.get("x2"), e.get("y2")))

            style = []
            if float(e.get("width"))>0:
                style.append(["stroke-width", e.get("width")])
                line.update({"style": ";".join(map(lambda x:":".join(x), style))})
            self.styleAndAttach(e, line)

        # self.postTransform(e)

    ########################################

    def smd_pre(self, e):
        x = float(e.get("x"))
        y = float(e.get("y"))
        dx = float(e.get("dx"))
        dy = float(e.get("dy"))
        r = 0
        if e.get("roundness"):
            r = float(e.get("roundness"))
        
        hx = dx/2
        hy = dy/2
        self.preTransform(e)
        rect = self.dwg.rect(insert=(-hx,-hy),
                             size=(dx, dy), 
                             rx=r,
                             ry=r)
        self.styleAndAttach(e, rect)
        self.postTransform(e)
       
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
        x = math.fabs((x2-x1))
        y = math.fabs((y2-y1))
        hx = (x2-x1)/2
        hy = (y2-y1)/2
        self.preTransform(e, str(x1 + hx), str(y1 + hy))
        rect = self.dwg.rect(insert=(-hx,-hy),
                             size=(x2-x1, y2-y1))
        self.styleAndAttach(e, rect)
        self.postTransform(e,str(x1 - hx), str(y1 - hy))

        if self._tFaceplate is not None and (e.get("layer")=="tFaceplate" or e.get("layer")=="bFaceplate"):
            print "rectangle tFaceplate"
            self.preTransform(e, str(x1), str(y1))
            xt, yt = self.flattenGroup()
            self.postTransform(e,str(x1), str(y1))

            self.preTransform(e, str(x1), str(y1+y))
            x_tl, y_tl = self.flattenGroup()
            self.postTransform(e,str(x1), str(y1+y))

            self.preTransform(e, str(x1+x), str(y1+y))
            x_tr, y_tr = self.flattenGroup()
            self.postTransform(e, str(x1+x), str(y1+y))

            self.preTransform(e, str(x1+y), str(y1))
            x_br, y_br = self.flattenGroup()
            self.postTransform(e,str(x1+y), str(y1))

            self._tFaceplate.push("M " + str(xt) + "," + str(yt))
            self._tFaceplate.push("L " + str(x_tl) + "," + str(y_tl))
            self._tFaceplate.push("L " + str(x_tr) + "," + str(y_tr))
            self._tFaceplate.push("L " + str(x_br) + "," + str(y_br))
            self._tFaceplate.push("L " + str(xt) + "," + str(yt))
        
    ########################################

    def plain_pre(self, e):
        if self._tFaceplate is None:
            self._tFaceplate = self.dwg.path(d="M 0,0")
            self._tFaceplate['id'] = 'gtron-tFaceplate'
            self._tFaceplate['visibility'] = 'hidden'
        self.currentGroup().add(self._tFaceplate)

        self._baseboard = self.dwg.g()
        self.currentGroup().add(self._baseboard)

    def plain_post(self, e):
        print "drawing dimension"
        self.preTransform(e)
        self.drawWirePath(e, self._dimension_wires, attached=True, attached_element=self._baseboard)

        self._back_wire = self.dwg.g()
        self._front_wire = self.dwg.g()
        # get rid of the fill rule that comes with the dimension layer
        style = []
        style.append(["fill", "none"])
        self._front_wire.update({"style": ";".join(map(lambda x:":".join(x), style))})
        self._back_wire.update({"style": ";".join(map(lambda x:":".join(x), style))})
        self.currentGroup().add(self._front_wire)
        self.currentGroup(group_stack=self.backside_groupStack).add(self._back_wire)

        self.postTransform(e)

    ########################################

    def signals_pre(self, e):
        pass

    def signals_post(self, e):
        self.preTransform(e)
        print "drawing front electrical wiring"
        self.drawWirePath(e, self._top_wires, attached=True, attached_element=self._front_wire)
        print "drawing back electrical wiring"
        self.drawWirePath(e, self._bottom_wires, attached=True, attached_element=self._back_wire)
        self.postTransform(e)

    ########################################

    def polygon_pre(self, e):
        vertices=[]
        if self._tFaceplate is not None and e.get("layer")=="tFaceplate":
            xt, yt = self.flattenGroup()
            self._tFaceplate.push("M " + str(xt) + " " + str(yt))

        for v in e.findall("vertex"):
            vertices.append((v.get("x"), v.get("y")))
            if self._tFaceplate is not None and (e.get("layer")=="tFaceplate" or e.get("layer")=="bFaceplate"):
                self._tFaceplate.push("L " + str(float(v.get("x")) + xt) + " " + str(float(v.get("y")) + yt))
            
        poly = self.dwg.polygon(points=vertices)
        self.styleAndAttach(e, poly)

    ########################################

    def text_pre(self, e):
        self.preTextTransform(e)
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

        if e.get("align") == "right":
            ratio = 100
            if e.get("ratio"):
                ratio = float(e.get("ratio"))
            width = float(e.get("size")) * ratio/100
            text = self.dwg.text(e.text,
                                 insert=(0,str(float(e.get("size"))/1.5)),
                                 transform="scale(1.25,-1.25)"
                                 )
        
        elif e.get("align") == "center":
            ratio = 100
            if e.get("ratio"):
                ratio = float(e.get("ratio"))
            width = float(e.get("size")) * ratio/100
            text = self.dwg.text(e.text,
                                 insert=(str(width/2),str(float(e.get("size"))/4)),
                                 transform="scale(1.25,-1.25)"
                                 )

        else:
            text = self.dwg.text(e.text,
                                 transform="scale(1.25,-1.25)"
                                 )

        text.update({"style": ";".join(map(lambda x:":".join(x), style))})
        self.styleAndAttach(e, text)

        self.postTextTransform(e)
