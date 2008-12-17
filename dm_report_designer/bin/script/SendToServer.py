
import uno
import string
import unohelper
import random
import xmlrpclib
import base64, tempfile
from com.sun.star.task import XJobExecutor
import os
import sys
if __name__<>'package':
    from lib.gui import *
    from lib.error import *
    from lib.functions import *
    from lib.tools import * 
    from LoginTest import *
    database="dm"
    uid = 1
#
#
class SendtoServer(unohelper.Base, XJobExecutor):
    Kind = {
        'PDF' : 'pdf',
        'OpenOffice': 'sxw',
        'HTML' : 'html'
    }

    def __init__(self,ctx):
        self.ctx     = ctx
        self.module  = "openerp_report"
        self.version = "0.1"
        LoginTest()
        if not loginstatus and __name__=="package":
            exit(1)

        global passwd
        self.password = passwd
        self.password = 'admin'

        desktop=getDesktop()
        oDoc2 = desktop.getCurrentComponent()
        docinfo=oDoc2.getDocumentInfo()
        sock = xmlrpclib.ServerProxy(docinfo.getUserFieldValue(0) +'/xmlrpc/object')
        self.ids = sock.execute(database, uid, self.password, 'ir.module.module', 'search', [('name','=','base_report_designer'),('state', '=', 'installed')])
        if not len(self.ids):
            ErrorDialog("Please Install base_report_designer module", "", "Module Uninstalled Error")
            exit(1)

        report_name = ""
        name=""
        if docinfo.getUserFieldValue(2)<>"" :
            try:
                fields=['name','report_name']
                self.res_other = sock.execute(database, uid, self.password, 'ir.actions.report.xml', 'read', [docinfo.getUserFieldValue(2)],fields)
                name = self.res_other[0]['name']
                report_name = self.res_other[0]['report_name']
            except:
                pass
        elif docinfo.getUserFieldValue(3) <> "":
            name = ""
            result =  "rnd"
            for i in range(5):
                result =result + random.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890')

            report_name = docinfo.getUserFieldValue(3) + "." + result
        else:
            ErrorDialog("Please select appropriate module...","Note: use OpenERP Report -> Open a new Report", "Module selection ERROR");
            exit(1)

        self.win = DBModalDialog(60, 50, 180, 100, "Send To Server")
        self.win.addFixedText("lblName",10 , 9, 40, 15, "Report Name :")
        self.win.addEdit("txtName", -5, 5, 123, 15,name)
        self.win.addFixedText("lblReportName", 2, 30, 50, 15, "Technical Name :")
        self.win.addEdit("txtReportName", -5, 25, 123, 15,report_name)
        self.win.addCheckBox("chkHeader", 51, 45, 70 ,15, "Corporate Header")
        self.win.addFixedText("lblResourceType", 2 , 60, 50, 15, "Select Rpt. Type :")
        self.win.addComboListBox("lstResourceType", -5, 58, 123, 15,True,itemListenerProc=self.lstbox_selected)
        self.lstResourceType = self.win.getControl( "lstResourceType" )

        for kind in self.Kind.keys(): 
            self.lstResourceType.addItem( kind, self.lstResourceType.getItemCount() )

        self.win.addButton( "btnSend", -5, -5, 80, 15, "Send Report to Server", actionListenerProc = self.btnOk_clicked)
        self.win.addButton( "btnCancel", -5 - 80 -5, -5, 40, 15, "Cancel", actionListenerProc = self.btnCancel_clicked)

        self.win.doModalDialog("lstResourceType", self.Kind.keys()[0])

    def lstbox_selected(self,oItemEvent):
        pass

    def btnCancel_clicked( self, oActionEvent ):
        self.win.endExecute()

    def btnOk_clicked(self, oActionEvent):
        if self.win.getEditText("txtName") <> "" and self.win.getEditText("txtReportName") <> "":
            desktop=getDesktop()
            oDoc2 = desktop.getCurrentComponent()
            docinfo=oDoc2.getDocumentInfo()
            self.getInverseFieldsRecord(1)
            fp_name = tempfile.mktemp('.'+"sxw")
            global dm_data            
            if not oDoc2.hasLocation():
                oDoc2.storeAsURL("file://"+fp_name,Array(makePropertyValue("MediaType","application/vnd.sun.xml.writer"),))
            sock = xmlrpclib.ServerProxy(docinfo.getUserFieldValue(0) +'/xmlrpc/object')
            if docinfo.getUserFieldValue(2)=="":
                id=self.getID()
                docinfo.setUserFieldValue(2,id)
                model = docinfo.getUserFieldValue(3)
                if dm_data :
                    model ='dm.offer.document'
                rec = { 
                    'name': self.win.getEditText("txtReportName"), 
                    'key': 'action', 
                    'model': model,
                    'value': 'ir.actions.report.xml,'+str(id),
                    'key2': 'client_print_multi',
                    'object': True 
                }
            else:
                id = docinfo.getUserFieldValue(2)
                rec = { 'name': self.win.getEditText("txtReportName") }
            oDoc2.store()
            data = read_data_from_file( get_absolute_file_path( oDoc2.getURL()[7:] ) )
            self.getInverseFieldsRecord(0)
            res = sock.execute(database, uid, self.password, 'ir.actions.report.xml', 'upload_report', int(docinfo.getUserFieldValue(2)),base64.encodestring(data),{'actual_model' : model[1]})
            params = {
                'name': self.win.getEditText("txtName"),
                'model': docinfo.getUserFieldValue(3),
                'report_name': self.win.getEditText("txtReportName"),
                'header': (self.win.getCheckBoxState("chkHeader") <> 0),
                'report_type': self.Kind[self.win.getListBoxSelectedItem("lstResourceType")],
            }
            if dm_data : 
                params['model'] ='dm.offer.document'
                params['actual_model'] = dm_data['model']
                params['document_id'] = dm_data['document_id']
            res = sock.execute(database, uid, self.password, 'ir.actions.report.xml', 'write', int(docinfo.getUserFieldValue(2)), params)
#            res = sock.execute(database, uid, self.password, 'ir.actions.report.xml', 'upload_report', int(docinfo.getUserFieldValue(2)),base64.encodestring(data))
            self.win.endExecute()
        else:
            ErrorDialog("Either Report Name or Technical Name is blank !!!\nPlease specify appropriate Name","","Blank Field ERROR")

    def getID(self):
        desktop=getDesktop()
        doc = desktop.getCurrentComponent()
        docinfo=doc.getDocumentInfo()
        params = {
            'name': self.win.getEditText("txtName"),
            'model': docinfo.getUserFieldValue(3),
            'report_name': self.win.getEditText('txtReportName')
        }

        sock = xmlrpclib.ServerProxy(docinfo.getUserFieldValue(0) +'/xmlrpc/object')
        id=sock.execute(database, uid, self.password, 'ir.actions.report.xml' ,'create', params)
        return id

    def getInverseFieldsRecord(self,nVal):
        desktop=getDesktop()
        doc = desktop.getCurrentComponent()
        count=0
        oParEnum = doc.getTextFields().createEnumeration()
        while oParEnum.hasMoreElements():
            oPar = oParEnum.nextElement()
            if oPar.supportsService("com.sun.star.text.TextField.DropDown"):
                oPar.SelectedItem = oPar.Items[nVal]
                if nVal==0:
                    oPar.update()

if __name__<>"package" and __name__=="__main__":
    SendtoServer(None)
elif __name__=="package":
    g_ImplementationHelper.addImplementation( SendtoServer, "org.openoffice.openerp.report.sendtoserver", ("com.sun.star.task.Job",),)