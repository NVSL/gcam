import svgwrite
import DXFVisitor
from Homogeneous2D import *

class DXFSVGVisitor(DXFVisitor.DXFVisitor):
    
    dwg = None

    def __init__(self, output, flipBoard, layer,mirrored):
        self.dwg = output
        DXFVisitor.DXFVisitor.__init__(self, output, flipBoard, layer,mirrored)
        
    def drawing_post(self, element):
        pass

    def renderLine(self, start, end):
        sp = tuple2D(self.currentTransform() * point2D(start))
        ep = tuple2D(self.currentTransform() * point2D(end))
        self.dwg.add(self.dwg.line(sp,ep, stroke="black", stroke_width="0.1mm"))

