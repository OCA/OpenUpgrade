if __name__<>"package":
    from lib.gui import *
    from lib.functions import *

class Change:
    def __init__(self, aVal= None):
        self.win=DBModalDialog(60, 50, 120, 90, "Connect to Tiny ERP Server")

        self.win.addFixedText("lblVariable", 38, 12, 60, 15, "Server")
        self.win.addEdit("txtHost",-2,9,60,15)

        self.win.addFixedText("lblReportName",45 , 31, 60, 15, "Port")
        self.win.addEdit("txtPort",-2,28,60,15)

        self.win.addFixedText("lblLoginName", 2, 51, 60, 15, "Protocol Connection")

        self.win.addComboListBox("lstProtocol", -2, 48, 60, 15, True)
        self.lstProtocol = self.win.getControl( "lstProtocol" )

        self.lstProtocol.addItem( "XML-RPC", 0)
        self.lstProtocol.addItem( "XML-RPC secure", 1)
        self.lstProtocol.addItem( "NET-RPC (faster)", 2)

        self.win.addButton( 'btnOK', -2, -5, 30, 15, 'Ok'
                      , actionListenerProc = self.btnOkOrCancel_clicked )

        self.win.addButton( 'btnCancel', -2 - 30 - 5 ,-5, 30, 15, 'Cancel'
                      , actionListenerProc = self.btnOkOrCancel_clicked )
        self.aVal=aVal
        self.protocol={'XML-RPC': 'http://',
            'XML-RPC secure': 'https://',
            'NET-RPC (faster)': 'socket://',}
        self.win.doModalDialog( "lstProtocol", 0)

    def cmbProtocol_selected(self,oItemEvent):
        pass
    def btnOkOrCancel_clicked(self,oActionEvent):
        if oActionEvent.Source.getModel().Name == "btnOK":
            url = self.protocol[self.win.getListBoxSelectedItem("lstProtocol")]+self.win.getEditText("txtHost")+":"+self.win.getEditText("txtPort")
            res = getConnectionStatus(url)
            if res == -1:
                self.aVal.append("Sever Could not found")
                self.aVal.append(res)
            elif res == 0:
                self.aVal.append("No Database Available")
                self.aVal.append(res)
            else:
                self.aVal.append(url)
                self.aVal.append(res)
            #return self.aVal
            self.win.endExecute()
        elif oActionEvent.Source.getModel().Name =="btnCancel":
            self.win.endExecute()