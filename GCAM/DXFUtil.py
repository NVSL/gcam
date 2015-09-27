
def insertCode(out, code, value):
    out.write(code + "\n" + value + "\n")

def addLine(out, sp, ep, layer, handle):
    insertCode(out,   '0', 'LINE' )
    insertCode(out,   '8', layer )
    insertCode(out,  '62', '4' )
    insertCode(out,   '5', '%x' % handle )
    insertCode(out, '100', 'AcDbEntity' )
    insertCode(out, '100', 'AcDbLine' )
    insertCode(out,  '10', '%f' % sp[0] )
    insertCode(out,  '20', '%f' % sp[1] )
    insertCode(out,  '30', '0.0' )
    insertCode(out,  '11', '%f' % ep[0] )
    insertCode(out,  '21', '%f' % ep[1] )
    insertCode(out,  '31', '0.0' )

