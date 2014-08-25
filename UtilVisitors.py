from EagleVisitor import *
from EagleError import *


class EchoVisitor(EagleVisitor):

    def package_pre(self, element):
        print "open " + element.tag
    def package_post(self, element):
        print "close " + element.tag

    def wire_pre(self, element):
        print element.tag

        
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
