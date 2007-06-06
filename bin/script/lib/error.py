from gui import *
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