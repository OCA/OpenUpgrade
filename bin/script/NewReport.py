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
        else:
            database="trunk_1"
        self.win=DBModalDialog(60, 50, 180, 135, "Open New Report")
        self.win.addFixedText("lblModuleSelection", 6, 12, 60, 15, "Module Selection")
        self.win.addComboListBox("lstModule", -2,9,123,80 , False)
        self.lstModule = self.win.getControl( "lstModule" )
        self.win.addFixedText("lblReportName", 17 ,95 , 60, 15, "Report Name")
        self.win.addEdit("txtReportName", -2, 92, 123, 15)
        self.aModuleName=[]
        desktop=getDesktop()
        doc = desktop.getCurrentComponent()
        docinfo=doc.getDocumentInfo()
        sock = xmlrpclib.ServerProxy(docinfo.getUserFieldValue(0) +'/xmlrpc/object')

        ids = sock.execute(database, 3, docinfo.getUserFieldValue(1), 'ir.model' , 'search',[])
        fields = [ 'model','name']
        res = sock.execute(database, 3, docinfo.getUserFieldValue(1), 'ir.model' , 'read', ids, fields)
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
            sock = xmlrpclib.ServerProxy(docinfo.getUserFieldValue(0) +'/xmlrpc/object')
            id=self.getID()
            print id
            rec={ 'name': self.win.getEditText("txtReportName"), 'key': 'action', 'model': self.aModuleName[self.lstModule.getSelectedItemPos()],'value': 'ir.actions.report.xml,'+str(id),'key2': 'client_print_multi','object': True }
            print "1",rec
            res=sock.execute(database, 3, docinfo.getUserFieldValue(1), 'ir.values' , 'create',rec)

            print res
            docinfo.setUserFieldValue(2,id)
            docinfo.setUserFieldValue(3,self.aModuleName[self.lstModule.getSelectedItemPos()])
            self.win.endExecute()
        elif oActionEvent.Source.getModel().Name=="btnCancel":
            self.win.endExecute()
    def getID(self):
        res = {}
        #res['name'] ='abc'
        res['model'] =self.aModuleName[self.lstModule.getSelectedItemPos()]
        res['report_name'] =self.win.getEditText("txtReportName")
        desktop=getDesktop()
        doc = desktop.getCurrentComponent()
        docinfo=doc.getDocumentInfo()
        sock = xmlrpclib.ServerProxy(docinfo.getUserFieldValue(0) +'/xmlrpc/object')
        id=sock.execute(database, 3, docinfo.getUserFieldValue(1), 'ir.actions.report.xml' ,'create',res)
        return id

if __name__<>"package" and __name__=="__main__":
    NewReport(None)
elif __name__=="package":
    g_ImplementationHelper.addImplementation( \
            NewReport,
            "org.openoffice.tiny.report.opennewreport",
            ("com.sun.star.task.Job",),)

#sock.execute(database, 3, docinfo.getUserFieldValue(1), 'ir.model.data' , 'ir_set','action','client_print_multi','report_name_string',['modelname'],'ir.actions.report.xml,'+str(id),replace=True,isobject=True)

#self.pool.get('ir.model.data').ir_set(cr, self.uid, 'action', keyword, res['name'], [res['model']], value, replace=replace, isobject=True, xml_id=xml_id)
#'action','client_print_multi','report_name_string',['modelname'],'ir.actions.report.xml,'+str(id),replace=True,isobject=True
#(04:58:49  IST) Fabien Pinckaers: Create the report and the ir_set
#(04:59:11  IST) Fabien Pinckaers: Call the method ir_set
#(04:59:18  IST) Fabien Pinckaers: on object ir.model.data
#(04:59:22  IST) Hardik Joshi: ok
#(04:59:44  IST) Hardik Joshi: i got idea
#(05:00:21  IST) Fabien Pinckaers: With arguments: 'action','client_print_multi','report_name_string',['modelname'],'ir.actions.report.xml,'+str(id),replace=True,isobject=True
#(05:00:41  IST) Fabien Pinckaers: Where id is the id of the ir.actions.report.xml object you created for this report.
#(05:00:56  IST) Fabien Pinckaers: See _tag_repot in tools/convert.py
#(05:01:05  IST) Hardik Joshi: ok
#(05:01:21  IST) Fabien Pinckaers: That creates reports when parsing .xml file for data loading at install.
