import uno
import re
#import Fields

class modify:
    def __init__(self):
        localContext = uno.getComponentContext()

        resolver = localContext.ServiceManager.createInstanceWithContext(
                        "com.sun.star.bridge.UnoUrlResolver", localContext )
        smgr = resolver.resolve( "uno:socket,host=localhost,port=2002;urp;StarOffice.ServiceManager" )
        remoteContext = smgr.getPropertyValue( "DefaultContext" )
        desktop = smgr.createInstanceWithContext( "com.sun.star.frame.Desktop",remoteContext)
        Doc =desktop.getCurrentComponent()
        oVC = Doc.CurrentController.getViewCursor()
        if oVC.TextField:
            oMyObject= self.getOperation(oVC.TextField.Items.__getitem__(1))

            if oMyObject.__getitem__(0) == "field":
                print oMyObject.__getitem__(1)
            elif oMyObject.__getitem__(0) == "expression":
                print oMyObject.__getitem__(1)
            elif oMyObject.__getitem__(1)=="repeatIn":
                print oMyObject.__getitem__(1)
    def getOperation(self, str):
        #str = "[[ RepeatIn(objects, 'variable') ]]" #repeatIn
        #str = "[[ saleorder.partner_id.name ]]" # field
        #str = "[[ some thing complex ]]" # expression

        method1 = lambda x: (u'repeatIn', x.group(1), x.group(2))
        method2 = lambda x: (u'field', x.group(1))
        method3 = lambda x: (u'expression', x.group(1))

        regexes = [
                ('\\[\\[ *repeatIn\\( *(.+)*, *\'([a-zA-Z0-9_]+)\' *\\) *\\]\\]', method1),
                ('\\[\\[ *([a-zA-Z0-9_\.]+) *\\]\\]', method2),
                ('\\[\\[ *(.+) *\\]\\]', method3)
        ]

        for (rule,method) in regexes:
                res= re.match(rule, str)
                if res:
                        return method(res)
                        break

modify()