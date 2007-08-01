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

class ModifyExistingReport(unohelper.Base, XJobExecutor):
    def __init__(self,ctx):
        self.ctx     = ctx
        self.module  = "tiny_report"
        self.version = "0.1"
        LoginTest()
        if not loginstatus and __name__=="package":
            exit(1)
        self.win=DBModalDialog(60, 50, 180, 115, "Modify Existing Report")
        self.win.addFixedText("lblReport", 2, 3, 60, 15, "Report Selection")
        self.win.addComboListBox("lstReport", -1,15,178,80 , False,itemListenerProc=self.lstbox_selected)
        self.lstReport = self.win.getControl( "lstReport" )
        desktop=getDesktop()
        doc = desktop.getCurrentComponent()
        docinfo=doc.getDocumentInfo()
        sock = xmlrpclib.ServerProxy(docinfo.getUserFieldValue(0) +'/xmlrpc/object')
        self.ids = sock.execute(docinfo.getUserFieldValue(2), 3, docinfo.getUserFieldValue(1), 'ir.actions.report.xml' ,  'search', [('report_sxw_content','<>',False)])
        #res_sxw = sock.execute(docinfo.getUserFieldValue(2), 3, docinfo.getUserFieldValue(1), 'ir.actions.report.xml', 'report_get', ids[0])
        fields=['name','report_name']
        res_other = sock.execute(docinfo.getUserFieldValue(2), 3, docinfo.getUserFieldValue(1), 'ir.actions.report.xml', 'read', self.ids,fields)
        for i in range(res_other.__len__()):
            if res_other[i]['name']<>"":
                self.lstReport.addItem(res_other[i]['name'],self.lstReport.getItemCount())

        #self.win.addFixedText("lblModuleSelection1", 2, 98, 60, 15, "Module Selection")

        #os.system( "oowriter /home/hjo/Desktop/aaa.sxw &" )

        self.win.doModalDialog("",None)

    def lstbox_selected(self,oItemEvent):
        print self.win.getListBoxSelectedItemPos("lstReport")
        desktop=getDesktop()
        doc = desktop.getCurrentComponent()
        docinfo=doc.getDocumentInfo()
        sock = xmlrpclib.ServerProxy(docinfo.getUserFieldValue(0) +'/xmlrpc/object')

        res = sock.execute(docinfo.getUserFieldValue(2), 3, docinfo.getUserFieldValue(1), 'ir.actions.report.xml', 'report_get', self.ids[self.win.getListBoxSelectedItemPos("lstReport")])

        if res['report_sxw_content']:
            data = base64.decodestring(res['report_sxw_content'])
            fp_name = tempfile.mktemp('.'+"sxw")
            fp = file(fp_name, 'wb+')
            fp.write(data)
            fp.close()
#           file('/tmp/data.sxw', 'w').write(data)

if __name__<>"package" and __name__=="__main__":
    ModifyExistingReport(None)
elif __name__=="package":
    g_ImplementationHelper.addImplementation( \
            ModifyExistingReport,
            "org.openoffice.tiny.report.modifyreport",
            ("com.sun.star.task.Job",),)