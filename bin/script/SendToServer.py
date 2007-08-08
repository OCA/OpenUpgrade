

import uno
import string
import unohelper
import xmlrpclib
import base64, tempfile
from com.sun.star.task import XJobExecutor
import os
import sys
if __name__<>'package':
    from lib.gui import *
    from lib.error import *
    from LoginTest import *
    from lib.functions import *

class SendtoServer(unohelper.Base, XJobExecutor):
    def __init__(self,ctx):
        self.ctx     = ctx
        self.module  = "tiny_report"
        self.version = "0.1"
        LoginTest()
        if not loginstatus and __name__=="package":
            exit(1)
#        else:
#            self.database="trunk_1"
        desktop=getDesktop()
        oDoc2 = desktop.getCurrentComponent()
        docinfo=oDoc2.getDocumentInfo()
        sock = xmlrpclib.ServerProxy(docinfo.getUserFieldValue(0) +'/xmlrpc/object')
        fields=['name','report_name','model']
        res_other = sock.execute(database, 3, docinfo.getUserFieldValue(1), 'ir.actions.report.xml', 'read',[docinfo.getUserFieldValue(2)] ,fields)
        print res_other
        self.win = DBModalDialog(60, 50, 180, 65, "Send To Server")
        self.win.addFixedText("lblExpression",10 , 9, 40, 15, "Report Name :")
        self.win.addEdit("txtExpression", -5, 5, 123, 15,res_other[0]['name'])
        self.win.addFixedText("lblName", 2, 30, 50, 15, "Technical Name :")
        self.win.addEdit("txtName", -5, 25, 123, 15,res_other[0]['report_name'])
        self.win.addButton( "btnSend", -5, -5, 80, 15, "Send Report to Server",
                        actionListenerProc = self.btnOkOrCancel_clicked )
        self.win.addButton( "btnCancel", -5 - 80 -5, -5, 40, 15, "Cancel",
                        actionListenerProc = self.btnOkOrCancel_clicked )
        self.win.doModalDialog("",None)
    def btnOkOrCancel_clicked(self, oActionEvent):
        if oActionEvent.Source.getModel().Name == "btnSend":
            desktop=getDesktop()
            oDoc2 = desktop.getCurrentComponent()
            docinfo=oDoc2.getDocumentInfo()
            print "abc",oDoc2.isModified(),oDoc2.hasLocation()
            if oDoc2.isModified() and not oDoc2.hasLocation():
                ErrorDialog("Please Save your file in filesystem !!!","File->Save OR File->Save As")
            elif oDoc2.isModified() and oDoc2.hasLocation():
                oDoc2.store()
                url=oDoc2.getURL().__getslice__(7,oDoc2.getURL().__len__())
                fp = file(url, 'rb')
                data=fp.read()
                fp.close()
                sock = xmlrpclib.ServerProxy(docinfo.getUserFieldValue(0) +'/xmlrpc/object')
                res = sock.execute(database, 3, docinfo.getUserFieldValue(1), 'ir.actions.report.xml', 'upload_report', int(docinfo.getUserFieldValue(2)),base64.encodestring(data),{})
                self.win.endExecute()
        elif oActionEvent.Source.getModel().Name == "btnCancel":
            self.win.endExecute()
if __name__<>"package" and __name__=="__main__":
    SendtoServer(None)
elif __name__=="package":
    g_ImplementationHelper.addImplementation( \
            SendtoServer,
            "org.openoffice.tiny.report.sendtoserver",
            ("com.sun.star.task.Job",),)

