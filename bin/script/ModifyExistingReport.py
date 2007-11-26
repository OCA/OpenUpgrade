

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
    database="test"
    uid = 3

#

class ModifyExistingReport(unohelper.Base, XJobExecutor):
    def __init__(self,ctx):
        self.ctx     = ctx
        self.module  = "tiny_report"
        self.version = "0.1"

        LoginTest()
        if not loginstatus and __name__=="package":
            exit(1)

        self.win=DBModalDialog(60, 50, 180, 120, "Modify Existing Report")
        self.win.addFixedText("lblReport", 2, 3, 60, 15, "Report Selection")
        self.win.addComboListBox("lstReport", -1,15,178,80 , False,itemListenerProc=self.lstbox_selected)
        self.lstReport = self.win.getControl( "lstReport" )
        desktop=getDesktop()
        doc = desktop.getCurrentComponent()
        docinfo=doc.getDocumentInfo()
        sock = xmlrpclib.ServerProxy(docinfo.getUserFieldValue(0) +'/xmlrpc/object')
        self.ids = sock.execute(database, uid, docinfo.getUserFieldValue(1), 'ir.module.module' ,  'search', [('name','=','base_report_designer')])
        fields=['name','state']
        self.res_other = sock.execute(database, uid, docinfo.getUserFieldValue(1), 'ir.module.module', 'read', self.ids,fields)
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
        self.ids = sock.execute(database, uid, docinfo.getUserFieldValue(1), 'ir.actions.report.xml' ,  'search', [('report_sxw_content','<>',False)])
        #res_sxw = sock.execute(docinfo.getUserFieldValue(2), 3, docinfo.getUserFieldValue(1), 'ir.actions.report.xml', 'report_get', ids[0])
        fields=['name','report_name','model']
        self.res_other = sock.execute(database, uid, docinfo.getUserFieldValue(1), 'ir.actions.report.xml', 'read', self.ids,fields)

        for i in range(self.res_other.__len__()):
            if self.res_other[i]['name']<>"":
                self.lstReport.addItem(self.res_other[i]['name'],self.lstReport.getItemCount())

        #self.win.addFixedText("lblModuleSelection1", 2, 98, 178, 15, "Module Selection")
        self.win.addButton('btnSave',-2 ,-5,80,15,'Save to Temp Directory'
                      ,actionListenerProc = self.btnOkOrCancel_clicked )
        self.win.addButton('btnCancel',-2 -80 ,-5,45,15,'Cancel'
                      ,actionListenerProc = self.btnOkOrCancel_clicked )

        self.win.doModalDialog("lstReport",self.res_other[0]['name'])

    def lstbox_selected(self,oItemEvent):
        pass
        #print self.win.getListBoxSelectedItemPos("lstReport")
        #self.win.setEditText("lblModuleSelection1",tempfile.mktemp('.'+"sxw"))
    def btnOkOrCancel_clicked(self, oActionEvent):
        if oActionEvent.Source.getModel().Name == "btnSave":
            desktop=getDesktop()
            doc = desktop.getCurrentComponent()
            docinfo=doc.getDocumentInfo()
            sock = xmlrpclib.ServerProxy(docinfo.getUserFieldValue(0) +'/xmlrpc/object')
            res = sock.execute(database, uid, docinfo.getUserFieldValue(1), 'ir.actions.report.xml', 'report_get', self.ids[self.win.getListBoxSelectedItemPos("lstReport")])
            fp_name = tempfile.mktemp('.'+"sxw")
            if res['report_sxw_content']:
                data = base64.decodestring(res['report_sxw_content'])
                fp = file(fp_name, 'wb')
                fp.write(data)
                fp.close()
            url="file://"+fp_name
            arr=Array(makePropertyValue("MediaType","application/vnd.sun.xml.writer"),)
            oDoc2 = desktop.loadComponentFromURL(url, "tiny", 55, arr)
            docinfo2=oDoc2.getDocumentInfo()
            docinfo2.setUserFieldValue(2,self.ids[self.win.getListBoxSelectedItemPos("lstReport")])
            docinfo2.setUserFieldValue(1,docinfo.getUserFieldValue(1))
            docinfo2.setUserFieldValue(0,docinfo.getUserFieldValue(0))
            docinfo2.setUserFieldValue(3,self.res_other[self.win.getListBoxSelectedItemPos("lstReport")]['model'])

#            desktop=getDesktop()
#            doc = desktop.getCurrentComponent()
            #try:
            oParEnum = oDoc2.getTextFields().createEnumeration()
            while oParEnum.hasMoreElements():
                oPar = oParEnum.nextElement()
                if oPar.supportsService("com.sun.star.text.TextField.DropDown"):
                    oPar.SelectedItem = oPar.Items[0]
                    oPar.update()
            #except:
            #    pass

            if oDoc2.isModified():
                if oDoc2.hasLocation() and not oDoc2.isReadonly():
                    oDoc2.store()
                #End If
            #End If
            #os.system( "`which ooffice` '-accept=socket,host=localhost,port=2002;urp;'")
            ErrorDialog("Download is Completed","Your file has been placed here :\n"+ fp_name,"Download Message")
            self.win.endExecute()
        elif oActionEvent.Source.getModel().Name == "btnCancel":
            self.win.endExecute()

if __name__<>"package" and __name__=="__main__":
    ModifyExistingReport(None)
elif __name__=="package":
    g_ImplementationHelper.addImplementation( \
            ModifyExistingReport,
            "org.openoffice.tiny.report.modifyreport",
            ("com.sun.star.task.Job",),)

