

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


class Expression:
    def __init__(self):
        self.win = DBModalDialog(60, 50, 140, 90, "Expression Builder")
        self.win.addFixedText("lblName", 5, 10, 20, 15, "Name :")
        self.win.addEdit("txtName", 30, 5, 100, 15)
        self.win.addFixedText("lblExpression",5 , 30, 25, 15, "Expression :")
        self.win.addEdit("txtExpression", 30, 25, 100, 15)
        self.win.addButton( "btnOK", -10, -10, 30, 15, "OK",
                        actionListenerProc = self.btnOkOrCancel_clicked )
        self.win.addButton( "btnCancel", -10 - 30 -5, -10, 30, 15, "Cancel",
                        actionListenerProc = self.btnOkOrCancel_clicked )
        self.win.doModalDialog()
    def btnOkOrCancel_clicked( self, oActionEvent ):
        #Called when the OK or Cancel button is clicked.
        if oActionEvent.Source.getModel().Name == "btnOK":
            localContext = uno.getComponentContext()
            resolver = localContext.ServiceManager.createInstanceWithContext(
                        "com.sun.star.bridge.UnoUrlResolver", localContext )
            ctx = resolver.resolve( "uno:socket,host=localhost,port=2002;urp;StarOffice.ComponentContext" )
            smgr = ctx.ServiceManager
            desktop = smgr.createInstanceWithContext( "com.sun.star.frame.Desktop",ctx)
            model = desktop.getCurrentComponent()
            text = model.Text
            cursor = text.createTextCursor()
            text.insertString( cursor, self.win.getEditText("txtName") + " : " + self.win.getEditText("txtExpression"), 0 )
	    self.win.endExecute()

        elif oActionEvent.Source.getModel().Name == "btnCancel":
            self.win.endExecute()


Expression()
