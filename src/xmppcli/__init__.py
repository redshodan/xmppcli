def logEx(e):
    import traceback
    print
    print traceback.print_exc()
    print e


from .parser import Attr, Elem, DumbParser
from .interface import Interface, StanzaHandler
