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

class AddAttachment(unohelper.Base, XJobExecutor ):
    def __init__(self):
        LoginTest()
        if not loginstatus and __name__=="package":
            exit(1)
        desktop=getDesktop()
        oDoc2 = desktop.getCurrentComponent()
        docinfo=oDoc2.getDocumentInfo()
        if docinfo.getUserFieldValue(2) <> "" and docinfo.getUserFieldValue(3) <> "":

            url = self.doc2pdf(oDoc2.getURL().__getslice__(7,oDoc2.getURL().__len__()))
            if url <> None:
                fp = file(url.__getslice__(7,url.__len__()), 'rb')
                data=fp.read()
                fp.close()
                sock = xmlrpclib.ServerProxy(docinfo.getUserFieldValue(0) +'/xmlrpc/object')
                res = sock.execute(database, 3, docinfo.getUserFieldValue(1), 'ir.attachment' , 'upload_attachment', url.__getslice__(url.rfind('/')+1,url.__len__()), base64.encodestring(data), docinfo.getUserFieldValue(3), docinfo.getUserFieldValue(2))
            else:
                ErrorDialog("Problem in Creating PDF","","PDF ERROR")
        else:
            self.win = DBModalDialog(60, 50, 180, 225, "Add Attachment to Server")
            self.win.addFixedText("lblModuleName",2 , 9, 176, 20, "Select Module:")
            self.win.addComboListBox("lstFields", 2, 22, 176, 80, False,itemListenerProc=self.lstbox_selected)
            #self.
            #sock = xmlrpclib.ServerProxy(docinfo.getUserFieldValue(0) +'/xmlrpc/object')
            #res = sock.execute(database, 3, docinfo.getUserFieldValue(1), 'orm' , 'name_search', )
            self.win.doModalDialog("",None)

    def lstbox_selected(self, oItemEvent):
        pass
# Woman was created from the rib of man: Not from his head to be thought of only, nor from his hand to be owned, nor from his foot to be beneath, but from under his arm to be protected, from his side to be equal, and from his heart to be loved.."
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
    AddAttachment()
elif __name__=="package":
    g_ImplementationHelper.addImplementation( \
            AddAttachment,
            "org.openoffice.tiny.report.addattachment",
            ("com.sun.star.task.Job",),)


