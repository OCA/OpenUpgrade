
import uno
import unohelper
import xmlrpclib
import base64
from com.sun.star.task import XJobExecutor
if __name__<>"package":
    from lib.gui import *
    from lib.error import ErrorDialog
    from LoginTest import *
    database="test"
    uid = 3

class AddAttachment(unohelper.Base, XJobExecutor ):
    Kind = {
	'PDF' : 'pdf',
	'OpenOffice': 'sxw',
    }
    def __init__(self,ctx):
        self.ctx     = ctx
        self.module  = "tiny_report"
        self.version = "0.1"
        LoginTest()
        if not loginstatus and __name__=="package":
            exit(1)

        self.aSearchResult = []
        desktop=getDesktop()
        oDoc2 = desktop.getCurrentComponent()
        docinfo=oDoc2.getDocumentInfo()

        if docinfo.getUserFieldValue(2) <> "" and docinfo.getUserFieldValue(3) <> "":
            self.win = DBModalDialog(60, 50, 180, 70, "Add Attachment to Server")
            self.win.addFixedText("lblResourceType", 2 , 5, 100, 10, "Select Appropriate Resource Type:")
            self.win.addComboListBox("lstResourceType", -2, 25, 176, 15,True,itemListenerProc=self.lstbox_selected)
            self.win.addButton('btnOk1', -2 , -5, 25 , 15,'OK' ,actionListenerProc = self.btnOkOrCancel_clicked )
        else:
            self.win = DBModalDialog(60, 50, 180, 190, "Add Attachment to Server")
            self.win.addFixedText("lblModuleName",2 , 9, 42, 20, "Select Module:")
            self.win.addComboListBox("lstmodel", -2, 5, 134, 15,True,itemListenerProc=self.lstbox_selected)
            self.lstModel = self.win.getControl( "lstmodel" )
            self.dModel={"Parner":'res.partner',
                         "Case":"crm.case",
                         "Sale Order":"sale.order",
                         "Purchase Order":"purchase.order",
                         "Analytic Account":"account.analytic.account",
                         "Project":"project.project",
                         "Tasks":"project.task",
                         "Employee":"hr.employee"
                         }

	    for item in self.dModel.keys():
		self.lstModel.addItem(item, self.lstModel.getItemCount())

            self.win.addFixedText("lblSearchName",2 , 25, 60, 10, "Enter Search String:")
            self.win.addEdit("txtSearchName", 2, 35, 149, 15,)
            self.win.addButton('btnSearch', -2 , 35, 25 , 15,'Search' ,actionListenerProc = self.btnOkOrCancel_clicked )

            self.win.addFixedText("lblSearchRecord", 2 , 55, 60, 10, "Search Result:")
            self.win.addComboListBox("lstResource", -2, 65, 176, 70, False, itemListenerProc=self.lstbox_selected)
            self.lstResource = self.win.getControl( "lstResource" )

            self.win.addFixedText("lblResourceType", 2 , 137, 100, 20, "Select Appropriate Resource Type:")
            self.win.addComboListBox("lstResourceType", -2, 147, 176, 15,True,itemListenerProc=self.lstbox_selected)

            self.win.addButton('btnOk', -2 , -5, 25 , 15,'OK' ,actionListenerProc = self.btnOkOrCancel_clicked )

	self.lstResourceType = self.win.getControl( "lstResourceType" )
	for kind in self.Kind.keys(): 
	    self.lstResourceType.addItem( kind, self.lstResourceType.getItemCount() )
	self.win.addButton('btnCancel', -2 - 27 , -5 , 30 , 15, 'Cancel' ,actionListenerProc = self.btnOkOrCancel_clicked )
	self.win.doModalDialog("",None)

    def lstbox_selected(self,oItemEvent):
        pass

    def btnOkOrCancel_clicked(self,oActionEvent):
        desktop=getDesktop()
        oDoc2 = desktop.getCurrentComponent()
        docinfo=oDoc2.getDocumentInfo()
        if oActionEvent.Source.getModel().Name == "btnSearch":
            if self.win.getListBoxSelectedItem("lstmodel") <> "":
                desktop=getDesktop()
                oDoc2 = desktop.getCurrentComponent()
                docinfo=oDoc2.getDocumentInfo()

                sock = xmlrpclib.ServerProxy(docinfo.getUserFieldValue(0) +'/xmlrpc/object')
                res = sock.execute( database, uid, docinfo.getUserFieldValue(1), self.dModel[self.win.getListBoxSelectedItem("lstmodel")], 'name_search', self.win.getEditText("txtSearchName"))
                self.win.removeListBoxItems("lstResource", 0, self.win.getListBoxItemCount("lstResource"))
                self.aSearchResult = res
                if self.aSearchResult <> []:
                    for result in self.aSearchResult:
                        self.lstResource.addItem(result[1],result[0])
                else:
                    ErrorDialog("No Search Result Found !!!","","Search ERROR")
        elif oActionEvent.Source.getModel().Name == "btnOk1":
            if self.win.getListBoxSelectedItem("lstResourceType") <> "":
                if oDoc2.getURL() <> "":
                    if self.Kind[self.win.getListBoxSelectedItem("lstResourceType")] == "pdf":
			url = self.doc2pdf(oDoc2.getURL()[7:])
                    else:
                        url= oDoc2.getURL()
                    if url <> None:
			fp = file(url[7:], 'rb')
                        data=fp.read()
                        fp.close()
                        sock = xmlrpclib.ServerProxy(docinfo.getUserFieldValue(0) +'/xmlrpc/object')
                        value={
			    'name': url[url.rfind('/')+1:],
                            'datas': base64.encodestring(data),
                            'res_model': docinfo.getUserFieldValue(3),
                            'res_id': docinfo.getUserFieldValue(2)
                            }
                        res = sock.execute(database, uid, docinfo.getUserFieldValue(1), 'ir.attachment' , 'create' , value )
                        self.win.endExecute()
                    else:
                        ErrorDialog("Problem in Creating PDF","","PDF ERROR")
                else:
                    ErrorDialog("Please Save Your File","","Saving ERROR")
            else:
                ErrorDialog("Please Select Resource Type","","Selection ERROR")
        elif oActionEvent.Source.getModel().Name == "btnOk":
            if self.win.getListBoxSelectedItem("lstResourceType") <> "":
                if self.win.getListBoxSelectedItem("lstResource") <> "" and self.win.getListBoxSelectedItem("lstmodel") <> "":
                    if oDoc2.getURL() <> "":
                        if self.Kin[self.win.getListBoxSelectedItem("lstResourceType")] == "pdf":
			    url = self.doc2pdf(oDoc2.getURL()[7:])
                        else:
                            url= oDoc2.getURL()
                        if url <> None:
			    fp = file(url[7:], 'rb')
                            data=fp.read()
                            fp.close()
                            sock = xmlrpclib.ServerProxy(docinfo.getUserFieldValue(0) +'/xmlrpc/object')
                            resourceid = None
                            for s in self.aSearchResult:
                                if s[1] == self.win.getListBoxSelectedItem("lstResource"):
                                    resourceid = s[0]
                            if resourceid <> None:
                                value={
				    'name': url[url.rfind('/')+1:],
                                    'datas': base64.encodestring(data),
                                    'res_model': self.dModel[self.win.getListBoxSelectedItem("lstmodel")],
                                    'res_id': resourceid
                                    }
                                res = sock.execute(database, uid, docinfo.getUserFieldValue(1), 'ir.attachment' , 'create' , value )
                                self.win.endExecute()
                            else:
                                ErrorDialog("No Resource Selected !!!","","Resource ERROR")
                        else:
                            ErrorDialog("Problem in Creating PDF","","PDF ERROR")
                    else:
                        ErrorDialog("Please Save Your File","","Saving ERROR")
                else:
                    ErrorDialog("Please select Model and Resource","","Selection ERROR")
            else:
                ErrorDialog("Please Select Resource Type","","Selection ERROR")
        elif oActionEvent.Source.getModel().Name == "btnCancel":
            self.win.endExecute()

    def doc2pdf(self, strFile):
       oDoc = None
       strFilterSubName = ''

       strUrl = convertToURL( strFile )
       desktop = getDesktop()
       oDoc = desktop.loadComponentFromURL( strUrl, "_blank", 0, Array(self._MakePropertyValue("Hidden",True)))
       if oDoc:
          strFilterSubName = ""
          # select appropriate filter
          if oDoc.supportsService("com.sun.star.presentation.PresentationDocument"):
             strFilterSubName = "impress_pdf_Export"
          elif oDoc.supportsService("com.sun.star.sheet.SpreadsheetDocument"):
             strFilterSubName = "calc_pdf_Export"
          elif oDoc.supportsService("com.sun.star.text.WebDocument"):
             strFilterSubName = "writer_web_pdf_Export"
          elif oDoc.supportsService("com.sun.star.text.GlobalDocument"):
             strFilterSubName = "writer_globaldocument_pdf_Export"
          elif oDoc.supportsService("com.sun.star.text.TextDocument"):
             strFilterSubName = "writer_pdf_Export"
          elif oDoc.supportsService("com.sun.star.drawing.DrawingDocument"):
             strFilterSubName = "draw_pdf_Export"
          elif oDoc.supportsService("com.sun.star.formula.FormulaProperties"):
             strFilterSubName = "math_pdf_Export"
          elif oDoc.supportsService("com.sun.star.chart.ChartDocument"):
             strFilterSubName = "chart_pdf_Export"
          else:
              pass
          #EndIf
       #EndIf

       if len(strFilterSubName) > 0:
          oDoc.storeToURL( convertToURL( strFile + ".pdf" ), Array(self._MakePropertyValue("FilterName", strFilterSubName ),self._MakePropertyValue("CompressMode", "1" )))
          return convertToURL( strFile + ".pdf" )
       #EndIf
       return None
       oDoc.close(True)
    #End Sub

    def _MakePropertyValue(self, cName = "", uValue = u"" ):
       oPropertyValue = createUnoStruct( "com.sun.star.beans.PropertyValue" )
       if cName:
          oPropertyValue.Name = cName
       #EndIf
       if uValue:
          oPropertyValue.Value = uValue
       #EndIf
       return oPropertyValue
    #End Function


if __name__<>"package" and __name__=="__main__":
    AddAttachment(None)
elif __name__=="package":
    g_ImplementationHelper.addImplementation( \
            AddAttachment,
            "org.openoffice.tiny.report.addattachment",
            ("com.sun.star.task.Job",),)
