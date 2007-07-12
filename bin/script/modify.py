import re
import uno
import string
import unohelper
import xmlrpclib
from com.sun.star.task import XJobExecutor
if __name__<>"package":
    from lib.gui import *
    from Expression import Expression
    from Fields import Fields
    from Repeatln import RepeatIn
    from lib.error import *


class modify(unohelper.Base, XJobExecutor ):

    def __init__( self, ctx ):
        self.ctx     = ctx
        self.module  = "tiny_report"
        self.version = "0.1"
        self.win=None
        localContext = uno.getComponentContext()
        resolver = localContext.ServiceManager.createInstanceWithContext(
                        "com.sun.star.bridge.UnoUrlResolver", localContext )
        smgr = resolver.resolve( "uno:socket,host=localhost,port=2002;urp;StarOffice.ServiceManager" )
        remoteContext = smgr.getPropertyValue( "DefaultContext" )
        desktop = smgr.createInstanceWithContext( "com.sun.star.frame.Desktop",remoteContext)
        Doc =desktop.getCurrentComponent()
        self.oVC = Doc.CurrentController.getViewCursor()
        # Variable Declaration
        self.sObj=None
        self.count=0
        self.aItemList=[]
        self.aComponentAdd=[]
        self.aObjectList=[]
        desktop=getDesktop()
        doc =desktop.getCurrentComponent()
        docinfo=doc.getDocumentInfo()
        self.oMyObject=None
        if not docinfo.getUserFieldValue(0)=="":
            self.sMyHost= docinfo.getUserFieldValue(0)
        else:
            ErrorDialog("Please insert user define field Field-1","Just go to File->Properties->User Define \nField-1 Eg. http://localhost:8069")
            exit(1)
        # Check weather Field-4 is available or not otherwise exit from application
        if not docinfo.getUserFieldValue(3) == "" and not docinfo.getUserFieldValue(0)=="":
            if self.oVC.TextField:
                self.oCurObj=self.oVC.TextField
                self.oMyObject= self.getOperation(self.oVC.TextField.Items.__getitem__(1))
                if self.oMyObject.__getitem__(0) == "field":
                    Fields(self.oMyObject.__getitem__(1).__getslice__(0,self.oMyObject.__getitem__(1).find(".")),self.oMyObject.__getitem__(1).__getslice__(self.oMyObject.__getitem__(1).find("."),self.oMyObject.__getitem__(1).__len__()).replace(".","/"),self.oCurObj.Items[0],True)
                elif self.oMyObject.__getitem__(0) == "expression":
                    Expression(self.oMyObject.__getitem__(1),self.oCurObj.Items.__getitem__(0),True)
                elif self.oMyObject.__getitem__(0)=="repeatIn":
                    #RepeatIn(self,sObject="",sVariable="",sFields="",sDisplayName="",bFromModify=False):
                    RepeatIn(self.oMyObject.__getitem__(1).__getslice__(0,self.oMyObject.__getitem__(1).find(".")),self.oMyObject[2],self.oMyObject.__getitem__(1).__getslice__(self.oMyObject.__getitem__(1).find("."),self.oMyObject.__getitem__(1).__len__()).replace(".","/"),self.oCurObj.Items[0],True)
            else:
                ErrorDialog("Please place your cursor at begaining of field \nwhich you want to modify","")

        else:
            ErrorDialog("Please insert user define field Field-1 or Field-4","Just go to File->Properties->User Define \nField-1 Eg. http://localhost:8069 \nOR \nField-4 Eg. account.invoice")
            exit(1)

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

if __name__<>"package":
    modify(None)
else:
    g_ImplementationHelper.addImplementation( \
        modify,
        "org.openoffice.tiny.report.modify",
        ("com.sun.star.task.Job",),)

