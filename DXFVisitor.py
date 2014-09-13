from lxml import etree as ET
from EagleVisitor import *
from GadgetCAM import *
import svgwrite
from  math import *
import DXFVisitor
import DXFTemplate
from matrix import *
from Homogeneous2D import *
import StringIO
import EagleError
import DXFUtil

class DXFVisitor(EagleVisitor):
    transformStack = []
    dtg = None
    _layer = "Layer 1"
    _buffer = StringIO.StringIO()
    output = ""
    flipBoard = False
    def __init__(self, output, flipBoard):
        self.transformStack = []
        self.dwg = None
        self.output = output
        self.flipBoard = flipBoard
        self._handle = 255
        self._buffer = StringIO.StringIO()
        self._minCurveSideLength = 1.0


    def setLayer(self, l):
        self._layer = l
        
    def pushTransform(self, t):
        if len(self.transformStack) > 0:
            self.transformStack.append(self.transformStack[-1] * t)
        else:
            self.transformStack.append(t)

    def currentTransform(self):
        return self.transformStack[-1]

    def popTransform(self):
        self.transformStack.pop()

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

    def computeRotation(self, e):
        if e.get("rot") is not None:
            if e.get("rot")[0] == "M":
                r = float(e.get("rot")[2:])
                scale = scale2D(-1,1)
            else:
                r = -float(e.get("rot")[1:])
                scale = identity2D()
        else:
            scale = identity2D()
            r = 0

        return rotate2D(radians(r)) * scale
    
    def computeTranslation(self, e, x, y):
        if x is None:
            x = float(e.get("x"))
            y = float(e.get("y"))
        else:
            x = float(x)
            y = float(y)

        return translate2D(x,y)

    def preTransform(self, element, x=None, y=None):
        transform = self.computeTranslation(element, x, y)* self.computeRotation(element) 
        self.pushTransform(transform)

    def postTransform(self, element,x=None, y=None):
        self.popTransform()
        

    #########################################

    def drawing_pre(self, element):
        if self.flipBoard:
            self.pushTransform(scale2D(-1,1))
        else:
            self.pushTransform(identity2D())
        self.pushTransform(scale2D(1,-1))

    def drawing_post(self, element):
        #print self._buffer.getvalue()
        f = open(self.output, "wb")
        f.write(DXFTemplate.r14_header)
        f.write(self._buffer.getvalue())
        f.write(DXFTemplate.r14_footer)

    #########################################

    def element_pre(self, e):
        self.preTransform(e)

    def element_post(self, e):
        self.postTransform(e)

    #########################################

    def renderLine(self, start, end):
        # print [start,end]
        self._handle += 1
        # print self.currentTransform()
        sp = tuple2D(self.currentTransform() * point2D(start))
        ep = tuple2D(self.currentTransform() * point2D(end))
        # def dxf_line(self,layer,csp):

        DXFUtil.addLine(self._buffer, sp, ep, self._layer, self._handle)

        # print(  '10', '%f' % sp[0] ,"\n")
        # print(  '20', '%f' % sp[1] ,"\n")
        # print(  '11', '%f' % ep[0] ,"\n")
        # print(  '21', '%f' % ep[1] ,"\n")

        
    def renderCircle(self,center, radius):
        vertices = []
        
        c = 16.0;
        while (radius * hypot(1-cos(radians(360.0/c)), -sin(radians(360.0/c)))) > self._minCurveSideLength:
            # print c
            # print "r' =  " + str(hypot(1-cos(radians(360.0/c)), -sin(radians(360.0/c))))
            c = c * 2.0

        c = max(c, 16)
        # print "r = " + str(radius) + " c = " + str(c)
        # print "r' =  " + str(hypot(1-cos(radians(360.0/c)), -sin(radians(360.0/c))))
        # print c
        c = int(c) + 1
        for i in range(0,c+1):
            theta = i*(360.0/c)
            p = (radius * cos(radians(theta)), radius * sin(radians(theta)))
            vertices.append(p)
        self.renderPolyLine(vertices)

    def hole_pre(self, e):
        self.preTransform(e)
        self.renderCircle((0,0), float(e.get("drill"))/2)
        self.postTransform(e)

    #########################################

    def circle_pre(self, e):
        self.preTransform(e)
        self.renderCircle((0,0), float(e.get("radius")))
        self.postTransform(e)

    ########################################

    def pad_pre(self, e):
        self.preTransform(e)
        self.renderCircle((0,0), float(e.get("drill"))/2)
        self.postTransform(e)
        
    ########################################

    def wire_pre(self, e):
        if e.get("curve") and e.get("curve") != "0":
            x1 = float(e.get("x1"))
            x2 = float(e.get("x2"))
            y1 = float(e.get("y1"))
            y2 = float(e.get("y2"))

            curve = float(e.get("curve"))
           
            adj = atan2((y2-y1),(x2-x1))
#            print "adj = "  + str(degrees(adj))
            rotation = rotate2D(adj)
            rotationInv = rotate2D(-adj)
            (x1prime, y1prime) = tuple2D(rotation * point2D((x1,y1)))
            (x2prime, y2prime) = tuple2D(rotation * point2D((x2,y2)))

#            print [x1,y1,x2,y2,x1prime,y1prime,x2prime,y2prime]

            theta = curve/2.0
            l = hypot((x2-x1), (y2-y1))/2
            a = l * sin(radians(90-theta))/sin(radians(theta))
            cprime = ((x2prime-x1prime)/2 + x1prime,a+y1prime)
#            print "cprime = " + str(cprime)
            c = tuple2D(rotationInv * point2D(cprime))
            radius = hypot(c[0]-x1,c[1]-y1)
#            print "radius = " + str(radius)
#            print "center = " + str(c)

            steps = 16.0;
            while radius * hypot(1-cos(radians(curve/steps)), -sin(radians(curve/steps))) > self._minCurveSideLength:
                steps = steps * 2.0

            startAngle = degrees(atan2(y1-c[1], x1-c[0]))
            endAngle = degrees(atan2(y2-c[1], x2-c[0]))
#            print [startAngle, endAngle]
#            print str(endAngle - startAngle) + " " + str(curve)

            vertices = []
            steps = int(steps) + 1
            for i in range(0,steps + 1):
                theta = startAngle + i*(curve/steps)
                p = (radius * cos(radians(theta)) + c[0], radius * sin(radians(theta)) + c[1])
                vertices.append((round(p[0],3), round(p[1],3)))
           # print vertices
            
            self.renderPolyLine(vertices)
            
            # sweep = "+" if curve > 0 else "-"
            # curve = -curve if curve < 0 else curve

            # diag = math.hypot((x2-x1), (y2-y1))
            # radius = diag * math.sin((math.radians((180-curve)/2)))/math.sin(math.radians(curve))
            # path = self.dwg.path()
            # path.push("m " + str(x1) + " " + str(y1))
            # path.push_arc((x2,y2), 0, (radius,radius), False, sweep, True)
        else:
            self.renderLine((float(e.get("x1")), float(e.get("y1"))),
                            (float(e.get("x2")), float(e.get("y2"))))
       
    ########################################

    def rectangle_pre(self, e):
#        ET.dump(e)
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
        self.renderPolyLine([(-hx,-hy), (hx, -hy),  (hx,  hy), (-hx, hy),(-hx,-hy)])
        self.postTransform(e,str(x1 - hx), str(y1 - hy))
        
    ########################################

    def renderPolyLine(self, vertices):
        for i in range(0, len(vertices)-1):
            self.renderLine(vertices[i], vertices[i+1])

    def polygon_pre(self, e):
        self.renderPolyLine([(float(v.get("x")), float(v.get("y"))) for v in e.findall("vertex")])
        
#    def text_pre(self, e):
#        raise Exception("Can't render text in DXF")


