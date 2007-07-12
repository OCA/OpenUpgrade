import uno
import string
import unohelper
import xmlrpclib
from com.sun.star.task import XJobExecutor

if __name__<>"package":
    from lib.gui import *
    from lib.error import ErrorDialog
    from lib.functions import *

class ServerParameter( unohelper.Base, XJobExecutor ):
    def __init__(self,ctx):
        self.ctx     = ctx
        self.module  = "tiny_report"
        self.version = "0.1"
        self.win=DBModalDialog(60, 50, 180, 250, "Server Parameters")
        self.win.addFixedText("lblVariable", 8, 12, 60, 15, "Server Connection")
        self.win.addEdit("txtHost",-34,9,85,15)
        self.win.addButton('btnChange',-2 ,9,30,15,'Change'
                      ,actionListenerProc = self.btnChange_clicked )
        self.win.addFixedText("lblReportName", 22, 31, 60, 15, "Report Name")
        self.win.addEdit("txtReportName",-2,28,117,15)
        self.win.addFixedText("lblLoginName", 26, 51, 60, 15, "Login Name")
        self.win.addEdit("txtLoginName",-2,48,117,15)
        self.win.addFixedText("lblPassword", 32, 70, 60, 15, "Password")
        self.win.addEdit("txtPassword",-2,67,117,15)
        self.win.addFixedText("lblModule", 12, 88, 60, 15, "Module Selection")
        self.win.addEdit("txtModule",-2,85,117,15)
        self.win.doModalDialog()

    def btnChange_clicked(self,oActionEvent):
        print "Hello change"

if __name__<>"package" and __name__=="__main__":
    ServerParameter(None)
elif __name__=="package":
    g_ImplementationHelper.addImplementation( \
            ServerParameter,
            "org.openoffice.tiny.report.serverparam",
            ("com.sun.star.task.Job",),)