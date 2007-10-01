
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
    database="latest_server"
#
#
class SendtoServer(unohelper.Base, XJobExecutor):
    def __init__(self,ctx):
        self.ctx     = ctx
        self.module  = "tiny_report"
        self.version = "0.1"
        LoginTest()
        if not loginstatus and __name__=="package":
            exit(1)
        desktop=getDesktop()
        oDoc2 = desktop.getCurrentComponent()
        docinfo=oDoc2.getDocumentInfo()
        sock = xmlrpclib.ServerProxy(docinfo.getUserFieldValue(0) +'/xmlrpc/object')
        self.ids = sock.execute(database, 3, docinfo.getUserFieldValue(1), 'ir.module.module' ,  'search', [('name','=','base_report_designer')])
        fields=['name','state']
        self.res_other = sock.execute(database, 3, docinfo.getUserFieldValue(1), 'ir.module.module', 'read', self.ids,fields)
        bFlag = False
        if len(self.res_other) > 0:
            for r in self.res_other:
                if r['state'] == "installed":
                    bFlag = True
        else:
            exit(1)
        if bFlag <> True:
            ErrorDialog("Please Install base_report_designer module","","Module Uninstalled Error")
            exit(1)
        self.win = DBModalDialog(60, 50, 180, 85, "Send To Server")
        self.win.addFixedText("lblName",10 , 9, 40, 15, "Report Name :")
        self.win.addEdit("txtName", -5, 5, 123, 15)#,res_other[0]['name'])
        self.win.addFixedText("lblReportName", 2, 30, 50, 15, "Technical Name :")
        self.win.addEdit("txtReportName", -5, 25, 123, 15)#,res_other[0]['report_name'])
        self.win.addCheckBox("chkHeader", 51, 45, 70 ,15, "Corporate Header")
        self.win.addButton( "btnSend", -5, -5, 80, 15, "Send Report to Server",
                        actionListenerProc = self.btnOkOrCancel_clicked)
        self.win.addButton( "btnCancel", -5 - 80 -5, -5, 40, 15, "Cancel",
                        actionListenerProc = self.btnOkOrCancel_clicked)
        self.win.doModalDialog("",None)

    def btnOkOrCancel_clicked(self, oActionEvent):

        if oActionEvent.Source.getModel().Name == "btnSend":
            desktop=getDesktop()
            oDoc2 = desktop.getCurrentComponent()
            docinfo=oDoc2.getDocumentInfo()
            self.getInverseFieldsRecord(1)
            fp_name = tempfile.mktemp('.'+"sxw")
            if not oDoc2.hasLocation():
                oDoc2.storeAsURL("file://"+fp_name,Array())
            sock = xmlrpclib.ServerProxy(docinfo.getUserFieldValue(0) +'/xmlrpc/object')
            if docinfo.getUserFieldValue(2)=="":
                id=self.getID()
                docinfo.setUserFieldValue(2,id)
            else:
                id=docinfo.getUserFieldValue(2)
            rec={ 'name': self.win.getEditText("txtReportName"), 'key': 'action', 'model': docinfo.getUserFieldValue(3),'value': 'ir.actions.report.xml,'+str(id),'key2': 'client_print_multi','object': True }
            res=sock.execute(database, 3, docinfo.getUserFieldValue(1), 'ir.values' , 'create',rec)
            oDoc2.store()
            url=oDoc2.getURL().__getslice__(7,oDoc2.getURL().__len__())
            fp = file(url, 'rb')
            data=fp.read()
            fp.close()
            self.getInverseFieldsRecord(0)
            sock = xmlrpclib.ServerProxy(docinfo.getUserFieldValue(0) +'/xmlrpc/object')
            res = sock.execute(database, 3, docinfo.getUserFieldValue(1), 'ir.actions.report.xml', 'upload_report', int(docinfo.getUserFieldValue(2)),base64.encodestring(data),{})
            bHeader = True
            print self.win.getCheckBoxState("chkHeader")
            if self.win.getCheckBoxState("chkHeader")==0:
                print "false"
                bHeader = False
            res = sock.execute(database, 3, docinfo.getUserFieldValue(1), 'ir.actions.report.xml', 'write', int(docinfo.getUserFieldValue(2)),{"header":bHeader})
            self.win.endExecute()


        elif oActionEvent.Source.getModel().Name == "btnCancel":
            self.win.endExecute()

    def getID(self):
        desktop=getDesktop()
        doc = desktop.getCurrentComponent()
        docinfo=doc.getDocumentInfo()

        res = {}

        res['name'] =self.win.getEditText("txtName")

        res['model'] =docinfo.getUserFieldValue(3)

        res['report_name'] =self.win.getEditText("txtReportName")


        sock = xmlrpclib.ServerProxy(docinfo.getUserFieldValue(0) +'/xmlrpc/object')

        id=sock.execute(database, 3, docinfo.getUserFieldValue(1), 'ir.actions.report.xml' ,'create',res)

        return id

    def getInverseFieldsRecord(self,nVal):
        desktop=getDesktop()
        doc = desktop.getCurrentComponent()

        count=0
        try:
            oParEnum = doc.getTextFields().createEnumeration()
            while oParEnum.hasMoreElements():
                oPar = oParEnum.nextElement()
                if oPar.supportsService("com.sun.star.text.TextField.DropDown"):
                    oPar.SelectedItem = oPar.Items[nVal]
                    if nVal==0:
                        oPar.update()

        except:
            pass


if __name__<>"package" and __name__=="__main__":
    SendtoServer(None)
elif __name__=="package":
    g_ImplementationHelper.addImplementation( \
            SendtoServer,
            "org.openoffice.tiny.report.sendtoserver",
            ("com.sun.star.task.Job",),)


