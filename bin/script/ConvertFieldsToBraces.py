

import uno
import unohelper
import string
import re
from com.sun.star.task import XJobExecutor
if __name__<>"package":
    from lib.gui import *
    from LoginTest import *
    database="test"
    uid = 3

class ConvertFieldsToBraces( unohelper.Base, XJobExecutor ):

    def __init__(self,ctx):

        self.ctx     = ctx
        self.module  = "tiny_report"
        self.version = "0.1"
        LoginTest()
        if not loginstatus and __name__=="package":
            exit(1)
        self.aReportSyntex=[]
        self.getFields()


    def getFields(self):
        desktop=getDesktop()
        doc = desktop.getCurrentComponent()

        count=0
        try:
            oParEnum = doc.getTextFields().createEnumeration()
            while oParEnum.hasMoreElements():
                oPar = oParEnum.nextElement()
                if oPar.supportsService("com.sun.star.text.TextField.DropDown"):
                    oPar.getAnchor().Text.insertString(oPar.getAnchor(),oPar.Items[1],False)
                    oPar.dispose()
        except:
            pass




if __name__<>"package":
    ConvertFieldsToBraces(None)
else:
    g_ImplementationHelper.addImplementation( \
        ConvertFieldsToBraces,
        "org.openoffice.tiny.report.convertFB",
        ("com.sun.star.task.Job",),)



