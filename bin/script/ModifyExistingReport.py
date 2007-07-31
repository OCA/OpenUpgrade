import uno
import string
import unohelper
import xmlrpclib
from com.sun.star.task import XJobExecutor
import os
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
        self.win.addComboListBox("lstReport", -1,15,178,80 , False)
        self.lstReport = self.win.getControl( "lstReport" )
        desktop=getDesktop()
        doc = desktop.getCurrentComponent()
        docinfo=doc.getDocumentInfo()
        sock = xmlrpclib.ServerProxy(docinfo.getUserFieldValue(0) +'/xmlrpc/object')

        ids = sock.execute(docinfo.getUserFieldValue(2), 3, docinfo.getUserFieldValue(1), 'ir.actions.report.xml' , 'search',[('report_sxw_content','<>',"''"),])
        print ids
        fields = ['name','report_name']
        print docinfo.getUserFieldValue(2),docinfo.getUserFieldValue(1)
        res = sock.execute(docinfo.getUserFieldValue(2), 3, docinfo.getUserFieldValue(1), 'ir.actions.report.xml' , 'read', ids, fields)
        for i in range(res.__len__()):
            if res[i]['name']<>"":
                self.lstReport.addItem(res[i]['name'],self.lstReport.getItemCount())
                #print res[i]['report_sxw_content']
                #self.aModuleName.append(res[i]['model'])

        #self.win.addFixedText("lblModuleSelection1", 2, 98, 60, 15, "Module Selection")
        self.lstModule = self.win.getControl( "lstModule" )

        #os.system( "oowriter /home/hjo/Desktop/aaa.sxw &" )

        self.win.doModalDialog("",None)

if __name__<>"package" and __name__=="__main__":
    ModifyExistingReport(None)
elif __name__=="package":
    g_ImplementationHelper.addImplementation( \
            ModifyExistingReport,
            "org.openoffice.tiny.report.modifyreport",
            ("com.sun.star.task.Job",),)