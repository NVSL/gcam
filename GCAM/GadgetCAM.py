from EagleUtil.EagleBoard import *
from EagleUtil.EagleLayers import *

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
