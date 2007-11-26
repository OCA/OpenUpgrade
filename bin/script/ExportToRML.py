
import uno
import unohelper
import string
import tempfile
import base64
from com.sun.star.task import XJobExecutor
if __name__<>"package":
    from lib.gui import *
    from LoginTest import *
    from lib.error import *
    database="test"
    uid = 3

class ExportToRML( unohelper.Base, XJobExecutor ):

    def __init__(self,ctx):
        self.ctx     = ctx
        self.module  = "tiny_report"
        self.version = "0.1"
        LoginTest()
        if not loginstatus and __name__=="package":
            exit(1)

        desktop=getDesktop()
        doc = desktop.getCurrentComponent()
        docinfo=doc.getDocumentInfo()

        # Read Data from sxw file
        tmpsxw = tempfile.mktemp('.'+"sxw")
        if not doc.hasLocation():
            mytype = Array(makePropertyValue("MediaType","application/vnd.sun.xml.writer"),)
            doc.storeAsURL("file://"+tmpsxw,mytype)
        url=doc.getURL().__getslice__(7,doc.getURL().__len__())
        fp = file(url, 'rb')
        data=fp.read()
        fp.close()

        #tmprml = tempfile.mktemp('.'+"rml")
        if docinfo.getUserFieldValue(2) == "":
            ErrorDialog("Please Save this file on server","Use Send To Server Option in Tiny Report Menu","Error")
            exit(1)
        tmprml = self.GetAFileName()
        if tmprml == None:
            exit(1)
        tmprml = tmprml.__getslice__(7,len(tmprml))

        sock = xmlrpclib.ServerProxy(docinfo.getUserFieldValue(0) +'/xmlrpc/object')
        res = sock.execute(database, uid, docinfo.getUserFieldValue(1), 'ir.actions.report.xml', 'sxwtorml',base64.encodestring(data))
        try:
            if res['report_rml_content']:
                data = res['report_rml_content']
                fp = file(tmprml, 'wb')
                fp.write(data)
                fp.close()
        except:
            pass
        #self.win.doModalDialog("",None)

    def GetAFileName(self):
        oFileDialog=None
        iAccept=None
        sPath=""
        InitPath=""
        oUcb=None
        sFilePickerArgs = Array(10)
        oFileDialog = createUnoService("com.sun.star.ui.dialogs.FilePicker")
        oUcb = createUnoService("com.sun.star.ucb.SimpleFileAccess")
        oFileDialog.initialize(sFilePickerArgs)
        oFileDialog.appendFilter("TinyReport File Save To ....","*.rml")
        oFileDialog.setCurrentFilter("Report Markup Language(rml)")
        f_path=tempfile.mktemp("","")
        f_path = "Tiny-"+f_path.__getslice__(f_path.rfind("/")+1,len(f_path))
        oFileDialog.setDefaultName(f_path)
        if InitPath == "":
            InitPath = tempfile.gettempdir()
        #End If
        if oUcb.exists(InitPath):
            oFileDialog.setDisplayDirectory(InitPath)
        #End If
        iAccept = oFileDialog.execute()
        if iAccept == 1:
            sPath = oFileDialog.Files[0]
        else:
            sPath = None
        oFileDialog.dispose()
        return sPath


if __name__<>"package" and __name__=="__main__":
    ExportToRML(None)
elif __name__=="package":
    g_ImplementationHelper.addImplementation( \
            ExportToRML,
            "org.openoffice.tiny.report.exporttorml",
            ("com.sun.star.task.Job",),)
