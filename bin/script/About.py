

import uno
#import string
#import unohelper
#import xmlrpclib
#import base64, tempfile
from com.sun.star.task import XJobExecutor
#import os
#import sys
if __name__<>'package':
    from lib.gui import *
#    from lib.error import *
#    from LoginTest import *
#    from lib.functions import *

class About(unohelper.Base, XJobExecutor):
    def __init__(self,ctx):
        self.ctx     = ctx
        self.module  = "tiny_report"
        self.version = "0.1"
#        LoginTest()
#        if not loginstatus and __name__=="package":
#            exit(1)
##        else:
##            self.database="trunk_1"
#        desktop=getDesktop()
#        oDoc2 = desktop.getCurrentComponent()
#        docinfo=oDoc2.getDocumentInfo()
#        sock = xmlrpclib.ServerProxy(docinfo.getUserFieldValue(0) +'/xmlrpc/object')
#        fields=['name','report_name','model']
#        res_other = sock.execute(database, 3, docinfo.getUserFieldValue(1), 'ir.actions.report.xml', 'read',[docinfo.getUserFieldValue(2)] ,fields)
        self.win = DBModalDialog(60, 50, 225, 169, ".:: About Us !!! ::.")
        if __name__<>"package":
            self.win.addImageControl("imgAbout",0,0,225,169,sImagePath="file://About.jpg")
        else:
            self.win.addImageControl("imgAbout",0,0,225,169,sImagePath="file://images/About.jpg")
        self.win.doModalDialog("",None)

if __name__<>"package" and __name__=="__main__":
    About(None)
elif __name__=="package":
    g_ImplementationHelper.addImplementation( \
            About,
            "org.openoffice.tiny.report.about",
            ("com.sun.star.task.Job",),)

