import uno
import string
import unohelper
from com.sun.star.task import XJobExecutor
from lib.gui import *
from lib.error import ErrorDialog
from lib.functions import *
import xmlrpclib


class Expression(unohelper.Base, XJobExecutor ):
    def __init__(self,sExpression="",sName="", bFromModify=False):
        self.win = DBModalDialog(60, 50, 180, 65, "Expression Builder")
        print "Expression"
        self.win.addFixedText("lblExpression",17 , 10, 35, 15, "Expression :")
        self.win.addEdit("txtExpression", -5, 5, 123, 15)
        self.win.addFixedText("lblName", 2, 30, 50, 15, "Displayed Name :")
        self.win.addEdit("txtName", -5, 25, 123, 15)
        self.win.addButton( "btnOK", -5, -5, 40, 15, "OK",
                        actionListenerProc = self.btnOkOrCancel_clicked )
        self.win.addButton( "btnCancel", -5 - 40 -5, -5, 40, 15, "Cancel",
                        actionListenerProc = self.btnOkOrCancel_clicked )
        self.bModify=bFromModify
        if self.bModify==True:
            self.win.setEditText("txtExpression",sExpression)
            self.win.setEditText("txtName",sName)
        self.win.doModalDialog()

    def getDesktop(self):
        localContext = uno.getComponentContext()
        resolver = localContext.ServiceManager.createInstanceWithContext(
                        "com.sun.star.bridge.UnoUrlResolver", localContext )
        smgr = resolver.resolve( "uno:socket,host=localhost,port=2002;urp;StarOffice.ServiceManager" )
        remoteContext = smgr.getPropertyValue( "DefaultContext" )
        desktop = smgr.createInstanceWithContext( "com.sun.star.frame.Desktop",remoteContext)
        return desktop

    def btnOkOrCancel_clicked( self, oActionEvent ):
        #Called when the OK or Cancel button is clicked.
        if oActionEvent.Source.getModel().Name == "btnOK":
            desktop=self.getDesktop()
            doc = desktop.getCurrentComponent()
            text = doc.Text
            cursor = doc.getCurrentController().getViewCursor()
            if self.bModify==True:
                oCurObj=cursor.TextField
                sKey=u""+self.win.getEditText("txtName")
                sValue=u"[[ " + self.win.getEditText("txtExpression") + " ]]"
                oCurObj.Items = (sKey,sValue)
                oCurObj.update()
                self.win.endExecute()
            else:
                oInputList = doc.createInstance("com.sun.star.text.TextField.DropDown")
                if self.win.getEditText("txtName")!="" and self.win.getEditText("txtExpression")!="":
                    sKey=u""+self.win.getEditText("txtName")
                    sValue=u"[[ " + self.win.getEditText("txtExpression") + " ]]"
                    if cursor.TextTable==None:
                        oInputList.Items = (sKey,sValue)
                        text.insertTextContent(cursor,oInputList,False)
                    else:
                        oTable = cursor.TextTable
                        oCurCell = cursor.Cell
                        tableText = oTable.getCellByName( oCurCell.CellName )
                        oInputList.Items = (sKey,sValue)
                        tableText.insertTextContent(cursor,oInputList,False)
                    self.win.endExecute()
                else:
                    ErrorDialog("Please Fill appropriate data in Name field or \nExpression field")
        elif oActionEvent.Source.getModel().Name == "btnCancel":
            self.win.endExecute()

if __name__=="__main__":
    Expression()
#else:
#    g_ImplementationHelper.addImplementation( \
#        Expression,
#        "org.openoffice.tiny.report.expression",
#        ("com.sun.star.task.Job",),)

