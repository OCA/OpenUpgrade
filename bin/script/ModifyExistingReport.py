

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
    database="test_001"
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

        self.win = DBModalDialog(60, 50, 180, 120, "Modify Existing Report")
        self.win.addFixedText("lblReport", 2, 3, 60, 15, "Report Selection")
        self.win.addComboListBox("lstReport", -1,15,178,80 , False,itemListenerProc=self.lstbox_selected)
        self.lstReport = self.win.getControl( "lstReport" )
        desktop=getDesktop()
        doc = desktop.getCurrentComponent()
        docinfo=doc.getDocumentInfo()

	self.userInfo = docinfo.getUserFieldValue(1)
	# Open a new connexion to the server
        sock = xmlrpclib.ServerProxy(docinfo.getUserFieldValue(0) +'/xmlrpc/object')

        ids = sock.execute(database, uid, self.userInfo, 'ir.module.module', 'search', [('name','=','base_report_designer'),('state', '=', 'installed')])
	if not len(ids):
	    ErrorDialog("Please Install base_report_designer module", "", "Module Uninstalled Error")
	    exit(1)

	ids = sock.execute(database, uid, self.userInfo, 'ir.actions.report.xml' ,  'search', [('report_xsl', '=', False),('report_xml', '=', False)])

        fields=['id', 'name','report_name','model']

        self.reports = sock.execute(database, uid, self.userInfo, 'ir.actions.report.xml', 'read', ids, fields)
	self.report_with_id = []
    
	for report in self.reports:
            if report['name']<>"":
                model_ids = sock.execute(database, uid, self.userInfo, 'ir.model' ,  'search', [('model','=', report['model'])])
                model_res_other = sock.execute(database, uid, self.userInfo, 'ir.model', 'read', model_ids, [ 'name', 'model' ] )
                if model_res_other <> []:
		    self.report_with_id.append( (report['id'], model_res_other[0]['name'] + " - " + report['name'] ) ) 
                else:
                    self.report_with_id.append( (report['id'], report['name'] + " - " + report['model'] ) )
	
	self.report_with_id.sort( lambda x, y: cmp( x[1], y[1] ) )	

	for id, report_name in self.report_with_id:
	    self.lstReport.addItem( report_name, self.lstReport.getItemCount() )

        self.win.addButton('btnSave',-2 ,-5,80,15,'Open Report' ,actionListenerProc = self.btnOkOrCancel_clicked )
        self.win.addButton('btnCancel',-2 -80 ,-5,45,15,'Cancel' ,actionListenerProc = self.btnOkOrCancel_clicked )

        self.win.doModalDialog("lstReport",self.reports[0]['name'])

    def lstbox_selected(self,oItemEvent):
        pass
        #print self.win.getListBoxSelectedItemPos("lstReport")
        #self.win.setEditText("lblModuleSelection1",tempfile.mktemp('.'+"sxw"))

    def btnOkOrCancel_clicked(self, oActionEvent):
        if oActionEvent.Source.getModel().Name == "btnSave":
            try:
                desktop=getDesktop()
                doc = desktop.getCurrentComponent()
                docinfo=doc.getDocumentInfo()
                sock = xmlrpclib.ServerProxy(docinfo.getUserFieldValue(0) +'/xmlrpc/object')
		selectedItemPos = self.win.getListBoxSelectedItemPos( "lstReport" )
		id = self.report_with_id[ selectedItemPos ][0]

                res = sock.execute(database, uid, self.userInfo, 'ir.actions.report.xml', 'report_get', id)
                fp_name = tempfile.mktemp('.'+"sxw")
                fp_name1="r"+fp_name
                fp_path=os.path.join(fp_name1).replace("\\","/") 
		fp_win=fp_path[1:]
                if res['report_sxw_content']:
                    data = base64.decodestring(res['report_sxw_content'])
                    if os.name=='nt':
                        fp = file(fp_win, 'wb')
                    else:                
                        fp = file(fp_name, 'wb')
                    fp.write(data)
                    fp.close()
                if os.name=='nt':                
                     url="file:///"+fp_win
                else:  
                     url="file:///"+fp_name   

                arr=Array(makePropertyValue("MediaType","application/vnd.sun.xml.writer"),)
                oDoc2 = desktop.loadComponentFromURL(url, "tiny", 55, arr)
                docinfo2=oDoc2.getDocumentInfo()
                docinfo2.setUserFieldValue(0,docinfo.getUserFieldValue(0))
                docinfo2.setUserFieldValue(1,self.userInfo)
                docinfo2.setUserFieldValue(2,id)
                docinfo2.setUserFieldValue(3,self.reports[selectedItemPos]['model'])
    
                oParEnum = oDoc2.getTextFields().createEnumeration()
                while oParEnum.hasMoreElements():
                    oPar = oParEnum.nextElement()
                    if oPar.supportsService("com.sun.star.text.TextField.DropDown"):
                        oPar.SelectedItem = oPar.Items[0]
                        oPar.update()
                if oDoc2.isModified():
                    if oDoc2.hasLocation() and not oDoc2.isReadonly():
                        oDoc2.store()

                ErrorDialog("Download is Completed","Your file has been placed here :\n"+ fp_name,"Download Message")
                self.win.endExecute()
            except Exception, e:
		ErrorDialog("Report has not been downloaded", "Report: %s\nDetails: %s" % ( fp_name, e ),"Download Message")
		self.win.endExecute()

        elif oActionEvent.Source.getModel().Name == "btnCancel":
                self.win.endExecute()

if __name__<>"package" and __name__=="__main__":
    ModifyExistingReport(None)
elif __name__=="package":
    g_ImplementationHelper.addImplementation( ModifyExistingReport, "org.openoffice.tiny.report.modifyreport", ("com.sun.star.task.Job",),)

