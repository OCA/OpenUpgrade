import uno
import string
import unohelper
import xmlrpclib
from com.sun.star.task import XJobExecutor
if __name__<>"package":
    from lib.gui import *
    from lib.error import ErrorDialog
    from lib.functions import *
    from LoginTest import *
#
#
# Start OpenOffice.org, listen for connections and open testing document
#

class NewReport(unohelper.Base, XJobExecutor):
    def __init__(self,ctx):
        self.ctx     = ctx
        self.module  = "tiny_report"
        self.version = "0.1"
        LoginTest()
        if not loginstatus and __name__=="package":
            exit(1)
        self.win=DBModalDialog(60, 50, 180, 115, "Open New Report")
        self.win.addFixedText("lblModuleSelection", 2, 12, 60, 15, "Module Selection")
        self.win.addComboListBox("lstModule", -2,9,123,80 , False)
        self.lstModule = self.win.getControl( "lstModule" )
        self.aModuleName=[]
        desktop=getDesktop()
        doc = desktop.getCurrentComponent()
        docinfo=doc.getDocumentInfo()
        print docinfo.getUserFieldValue(0)
        sock = xmlrpclib.ServerProxy(docinfo.getUserFieldValue(0) +'/xmlrpc/object')

        ids = sock.execute(docinfo.getUserFieldValue(2), 3, docinfo.getUserFieldValue(1), 'ir.model' , 'search',[])
        fields = [ 'model','name']
        res = sock.execute(docinfo.getUserFieldValue(2), 3, docinfo.getUserFieldValue(1), 'ir.model' , 'read', ids, fields)
        for i in range(res.__len__()):
            self.lstModule.addItem(res[i]['name'],self.lstModule.getItemCount())
            self.aModuleName.append(res[i]['model'])


        self.win.addButton('btnOK',-2 ,-5, 70,15,'Use Module in Report'
                      ,actionListenerProc = self.btnOkOrCancel_clicked )

        self.win.addButton('btnCancel',-2 - 70 - 5 ,-5, 35,15,'Cancel'
                      ,actionListenerProc = self.btnOkOrCancel_clicked )

        self.win.doModalDialog("",None)

    def btnOkOrCancel_clicked(self,oActionEvent):
        if oActionEvent.Source.getModel().Name=="btnOK":
            desktop=getDesktop()
            doc = desktop.getCurrentComponent()
            docinfo=doc.getDocumentInfo()
            print self.lstModule.getSelectedItemPos()
            docinfo.setUserFieldValue(3,self.aModuleName[self.lstModule.getSelectedItemPos()])
            self.win.endExecute()
        elif oActionEvent.Source.getModel().Name=="btnCancel":
            self.win.endExecute()

if __name__<>"package" and __name__=="__main__":
    NewReport(None)
elif __name__=="package":
    g_ImplementationHelper.addImplementation( \
            NewReport,
            "org.openoffice.tiny.report.opennewreport",
            ("com.sun.star.task.Job",),)


