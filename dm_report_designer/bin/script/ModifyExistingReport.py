

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
        self.module  = "openerp_report"
        self.version = "0.1"

        LoginTest()
        if not loginstatus and __name__=="package":
            exit(1)

        self.win = DBModalDialog(60, 50, 180, 120, "Modify Existing Report")
        self.win.addFixedText("lblReport", 2, 3, 60, 15, "Report Selection")
        self.win.addComboListBox("lstReport", -1,15,178,80 , False )
        self.lstReport = self.win.getControl( "lstReport" )

        desktop=getDesktop()
        doc = desktop.getCurrentComponent()
        docinfo=doc.getDocumentInfo()

        self.hostname = docinfo.getUserFieldValue(0)
        global passwd
        self.password = passwd
        # Open a new connexion to the server
        sock = xmlrpclib.ServerProxy( self.hostname +'/xmlrpc/object')

        ids = sock.execute(database, uid, self.password, 'ir.module.module', 'search', [('name','=','base_report_designer'),('state', '=', 'installed')])
        if not len(ids):
            ErrorDialog("Please Install base_report_designer module", "", "Module Uninstalled Error")
            exit(1)

        ids = sock.execute(database, uid, self.password, 'ir.actions.report.xml', 'search', [('report_xsl', '=', False),('report_xml', '=', False),('model','=','dm.offer.document')])

        fields=['id', 'name','report_name','model' , 'actual_model']

        self.reports = sock.execute(database, uid, self.password, 'ir.actions.report.xml', 'read', ids, fields)
        self.report_with_id = []

        for report in self.reports:
            if report['name']<>"":
                model_ids = sock.execute(database, uid, self.password, 'ir.model' ,  'search', [('model','=', report['model'])])
                model_res_other = sock.execute(database, uid, self.password, 'ir.model', 'read', model_ids, [ 'name', 'model' ] )
                if model_res_other <> []:
                    name = model_res_other[0]['name'] + " - " + report['name']
                else:
                    name = report['name'] + " - " + report['model']
                self.report_with_id.append( (report['id'], name, report['model'], report['actual_model'] ) )

        self.report_with_id.sort( lambda x, y: cmp( x[1], y[1] ) )

        for id, report_name, model_name, actual_model in self.report_with_id:
            self.lstReport.addItem( report_name, self.lstReport.getItemCount() )

        self.win.addButton('btnSave',10,-5,50,15,'Open Report' ,actionListenerProc = self.btnOk_clicked )
        self.win.addButton('btnCancel',-10 ,-5,50,15,'Cancel' ,actionListenerProc = self.btnCancel_clicked )
        self.win.addButton('btnDelete',15 -80 ,-5,50,15,'Delete Report',actionListenerProc = self.btnDelete_clicked)
        self.win.doModalDialog("lstReport",self.report_with_id[0][1] )

    def btnOk_clicked(self, oActionEvent):
        try:
            desktop=getDesktop()
            doc = desktop.getCurrentComponent()
            docinfo=doc.getDocumentInfo()
            sock = xmlrpclib.ServerProxy( self.hostname +'/xmlrpc/object')
            selectedItemPos = self.win.getListBoxSelectedItemPos( "lstReport" )
            id = self.report_with_id[ selectedItemPos ][0]

            res = sock.execute(database, uid, self.password, 'ir.actions.report.xml', 'report_get', id)

            fp_name = tempfile.mktemp('.'+"sxw")
            fp_name1="r"+fp_name
            fp_path=os.path.join(fp_name1).replace("\\","/")
            fp_win=fp_path[1:]

            filename = ( os.name == 'nt' and fp_win or fp_name )
            if res['report_sxw_content']:
                write_data_to_file( filename, base64.decodestring(res['report_sxw_content']))
            url = "file:///%s" % filename

            arr=Array(makePropertyValue("MediaType","application/vnd.sun.xml.writer"),)
            oDoc2 = desktop.loadComponentFromURL(url, "openerp", 55, arr)
            docinfo2=oDoc2.getDocumentInfo()
            docinfo2.setUserFieldValue(0, self.hostname)
            docinfo2.setUserFieldValue(1,self.password)
            docinfo2.setUserFieldValue(2,id)
            model = self.report_with_id[selectedItemPos][3]  or self.report_with_id[selectedItemPos][2]
            docinfo2.setUserFieldValue(3,model)

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
        except Exception, e:
            ErrorDialog("Report has not been downloaded", "Report: %s\nDetails: %s" % ( fp_name, e ),"Download Message")
        self.win.endExecute()

    def btnCancel_clicked( self, oActionEvent ):
        self.win.endExecute()

    def btnDelete_clicked( self, oActionEvent ):
         desktop=getDesktop()
         doc = desktop.getCurrentComponent()
         docinfo=doc.getDocumentInfo()
         sock = xmlrpclib.ServerProxy( self.hostname +'/xmlrpc/object')
         selectedItemPos = self.win.getListBoxSelectedItemPos( "lstReport" )
         name=self.win.getListBoxSelectedItem ("lstReport")
         id = self.report_with_id[ selectedItemPos ][0]
         temp = sock.execute(database, uid, self.password, 'ir.actions.report.xml', 'unlink', id,)
         str_value='ir.actions.report.xml,'+str(id)
         ids = sock.execute(database, uid, self.password, 'ir.values' ,  'search',[('value','=',str_value)])
         if ids:
              rec = sock.execute(database, uid, self.password, 'ir.values', 'unlink', ids,)
         else :
            pass
         if temp:
              ErrorDialog("Report","Report has been Delete:\n "+name,"Message")
         else:
             ErrorDialog("Report","Report has not Delete:\n"+name," Message")
         self.win.endExecute()



if __name__<>"package" and __name__=="__main__":
    ModifyExistingReport(None)
elif __name__=="package":
    g_ImplementationHelper.addImplementation( ModifyExistingReport, "org.openoffice.openerp.report.modifyreport", ("com.sun.star.task.Job",),)

