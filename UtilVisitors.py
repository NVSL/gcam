from EagleVisitor import *
from EagleError import *
from copy import deepcopy


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
        else:
            if e.tag=="via":
                e.set("layer", "Vias")

    def layer_pre(self, e):
        pass
    def layer_post(self, e):
        pass

class RetagNameAttribute(EagleVisitor):
    _name = None
    _name_set = []

    def __init__(self, layers):
        self._name = ""
        _name_set = []

    def attribute_pre(self, e):
        if e.get("name") == "NAME" and self._name:
            text_node = ET.Element("text")
            for item in list(e.items()):
                if item[0]!='name':
                    text_node.set(item[0], item[1])
            # text_node.set('align', 'left')
            text_node.text = '%s' % self._name
            self._name_set.append(text_node)

    def element_pre(self, e):
        self._name = e.get("name")
    def element_post(self, e):
        self._name = ""

    def elements_pre(self, e):
        self._name_set = []
    def elements_post(self, e):
        if len(self._name_set)>0:
            for text_node in self._name_set:
                e.append(text_node)

class RetagValueAttribute(EagleVisitor):
    _value = None
    _value_set = []

    def __init__(self, layers):
        self._value = ""
        _value_set = []

    def attribute_pre(self, e):
        if e.get("name") == "VALUE" and self._value:
            text_node = ET.Element("text")
            for item in list(e.items()):
                if item[0]!='name':
                    text_node.set(item[0], item[1])
            text_node.text = '%s' % self._value
            self._value_set.append(text_node)

    def element_pre(self, e):
        self._value = e.get("value")
    def element_post(self, e):
        self._value = ""

    def elements_pre(self, e):
        self._value_set = []
    def elements_post(self, e):
        if len(self._value_set)>0:
            for text_node in self._value_set:
                e.append(text_node)

class RemoveNameVariable(EagleVisitor):
    _name = ""
    _name_attribute = ""

    def __init__(self, layers):
        self._name = None
        self._name_attribute = None

    def text_pre(self, e):
        if e.text == ">NAME":
            e.set('layer', 'None')

    def layer_pre(self, e):
        pass
    def layer_post(self, e):
        pass

    def attribute_pre(self, e):
        if e.get("name") == "NAME" and self._name:
            self._name_attribute = e
    def attribute_post(self, e):
        pass

    def element_pre(self, e):
        self._name = e.get("name")
    def element_post(self, e):
        self._name = ""
        self._name_attribute = ""

class RemoveValueVariable(EagleVisitor):
    _value = ""
    def __init__(self, layers):
        self._value = None

    def text_pre(self, e):
        if e.text == ">VALUE":
            e.set('layer', 'None')

    def layer_pre(self, e):
        pass
    def layer_post(self, e):
        pass

    def element_pre(self, e):
        self._value = e.get("value")
    def element_post(self, e):
        self._value = ""

class TranformElementText(EagleVisitor):
    _rot = ""
    _scale = ""
    _rotate = ""
    _text_set = []

    def __init__(self, layers):
        self._rot = ""
        self._scale = ""
        self._rotate = ""
        self._text_set = []

    def text_pre(self, e):
        if self._rot and (e.get("layer")=="tPlace" or e.get("layer")=="bPlace") :
            e.set("rot", self._rot)
            e.set("element_text", "True")
            self._text_set.append(deepcopy(e))

    def element_pre(self, e):
        if e.get("rot") is not None:
            # SMR###
            if e.get("rot")[0] == "S":
                if e.get("rot")[1] == "M":
                    self._rot = "R" + str(0)
                else:
                    self._rot = "R" + str(0)
            # MR###
            elif e.get("rot")[0] == "M":
                if float(e.get("rot")[2:]) > 90 and float(e.get("rot")[2:]) <= 270:
                    self._rot = "R" + str(180)
                else:
                    self._rot = "R" + str(0)

            # R###
            else:
                if float(e.get("rot")[1:]) > 90 and float(e.get("rot")[1:]) <= 270:
                    self._rot = "R" + str(180)
                else:
                    self._rot = "R" + str(0)

        else:
            self._rot = None

    def element_post(self, e):
        if len(self._text_set)>0:
            for text_node in self._text_set:
                e.append(text_node)

class TopBottomAttr(EagleVisitor):
    _layers = None
    def __init__(self, layers):
        self._layers = layers

    def default_pre(self, e):
        if e.get("layer"):
            if e.get("layer")[0]=='b' or e.get("layer")[0]=='_b' or e.get("layer")=="Bottom":
                e.set("onBackside", "True")
            else:
                e.set("onBackside", "False")

    def layer_pre(self, e):
        pass
    def layer_post(self, e):
        pass
