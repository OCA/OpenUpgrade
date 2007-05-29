

# OOo's libraries
import uno
import string
import unohelper
from lib.gui import *
from com.sun.star.task import XJobExecutor
# Danny's libraries
#from OOo.OOoLib import createUnoService, createUnoStruct
#from OOo.ListenerProcAdapters import *
#from Danny.OOo.Listeners.TopWindowListener import TopWindowListener


#--------------------------------------------------
# Example of Dialog box built by subclassing the DBModalDialog class.

class ErrorDialog:
    def __init__(self,sErrorMsg, sErrorHelpMsg=""):
        self.win = DBModalDialog(50, 50, 150, 70, "Error Message")
        self.win.addFixedText("lblErrMsg", 5, 5, 190, 20, sErrorMsg)
        self.win.addFixedText("lblErrHelpMsg", 5, 20, 190, 35, sErrorHelpMsg)
        self.win.addButton('btnOK', 55,55,40,15,'Ok'
                     ,actionListenerProc = self.btnOkOrCancel_clicked )
        self.win.doModalDialog()
    def btnOkOrCancel_clicked( self, oActionEvent ):
        self.win.endExecute()


class Expression:
    def __init__(self):
        self.win = DBModalDialog(60, 50, 140, 80, "Expression Builder")
        self.win.addFixedText("lblName", 17, 10, 20, 15, "Name :")
        self.win.addEdit("txtName", 40, 5, 90, 15)
        self.win.addFixedText("lblExpression",5 , 30, 35, 15, "Expression :")
        self.win.addEdit("txtExpression", 40, 25, 90, 15)
        self.win.addButton( "btnOK", -10, -10, 30, 15, "OK",
                        actionListenerProc = self.btnOkOrCancel_clicked )
        self.win.addButton( "btnCancel", -10 - 30 -5, -10, 30, 15, "Cancel",
                        actionListenerProc = self.btnOkOrCancel_clicked )
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
            self.bOkay = True
            desktop=self.getDesktop()
            doc = desktop.getCurrentComponent()
            text = doc.Text
            cursor = doc.getCurrentController().getViewCursor()
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
                    #cursor = tableText.createTextCursor()
                    #cursor.gotoEndOfParagraph(True)
                    oInputList.Items = (sKey,sValue)
                    tableText.insertTextContent(cursor,oInputList,False)
                self.win.endExecute()
            else:
                ErrorDialog("Please Fill appropriate data in Name field or \nExpression field")
        elif oActionEvent.Source.getModel().Name == "btnCancel":
            self.win.endExecute()

Expression()
