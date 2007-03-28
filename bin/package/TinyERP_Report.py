import uno
import string
import unohelper
from com.sun.star.task import XJobExecutor
from lib.gui import *


    #-----------------------------------------------------
    #  Implementaion of DBModalDialog Class
    #-----------------------------------------------------

class Fields( unohelper.Base, XJobExecutor ):
    def __init__( self, ctx ):
        self.ctx     = ctx
        self.module  = "tiny_report"
        self.version = "0.1"
        self.win=None
    def trigger( self, args ):
        self.win = DBModalDialog(60, 50, 140, 250, "Field Builder")
        self.win.addFixedText("lblName", 10, 12, 20, 15, "Name :")
        self.win.addEdit("txtName", 35, 10, 100, 15, "Enter Name",)
        self.win.addFixedText("lblVariable", 5, 32, 25, 15, "Variable :")
        self.win.addComboBox("cmbVariable", 35, 30, 100, 15,True,
                             itemListenerProc=self.cmbVariable_selected)
        self.insVariable = self.win.getControl( "cmbVariable" )
        self.win.addFixedText("lblFields", 11, 52, 25, 15, "Fields :")
        self.win.addComboListBox("lstFields", 35, 50, 100, 150, False)
        self.insField = self.win.getControl( "lstFields" )
        import xmlrpclib
        sock = xmlrpclib.ServerProxy('http://localhost:8069/xmlrpc/object')
        self.getModule(sock)
        self.win.addButton('btnOK',-5 ,-25,45,15,'Ok'
                      ,actionListenerProc = self.btnOkOrCancel_clicked )
        self.win.addButton('btnCancel',-5 - 45 - 5 ,-25,45,15,'Cancel'
                      ,actionListenerProc = self.btnOkOrCancel_clicked )
        self.win.doModalDialog()

    def cmbVariable_selected(self,oItemEvent):

        import xmlrpclib
        sock = xmlrpclib.ServerProxy('http://localhost:8069/xmlrpc/object')
        self.win.removeListBoxItems("lstFields", 0, self.win.getListBoxItemCount("lstFields"))
        self.genTree(sock, self.win.getComboBoxSelectedText("cmbVariable"),'', 0)

    def btnOkOrCancel_clicked( self, oActionEvent ):
        #Called when the OK or Cancel button is clicked.
        if oActionEvent.Source.getModel().Name == "btnOK":
            self.bOkay = True
            localContext = uno.getComponentContext()
            resolver = localContext.ServiceManager.createInstanceWithContext(
                        "com.sun.star.bridge.UnoUrlResolver", localContext )
            ctx = resolver.resolve( "uno:socket,host=localhost,port=2002;urp;StarOffice.ComponentContext" )
            smgr = ctx.ServiceManager
            desktop = smgr.createInstanceWithContext( "com.sun.star.frame.Desktop",ctx)
            model = desktop.getCurrentComponent()
            text = model.Text
            cursor = text.createTextCursor()
            if self.win.getListBoxSelectedItem("lstFields") != "":
                text.insertString( cursor,self.win.getEditText("txtName") + ": [[" + self.win.getListBoxSelectedItem("lstFields")+"]]" , 0 )
        elif oActionEvent.Source.getModel().Name == "btnCancel":
            self.win.endExecute()
    # this method will featch data from the database and place it in the combobox
    def genTree(self, oSocket, oTable, sParent ,nCount):

        # returieve metadata of pertucular table form the database
        res = oSocket.execute('terp', 3, 'admin', oTable, 'fields_view_get')
        for name in res['fields'].keys():

            # check for field type if many to one tehn execute code
            if res['fields'][name]['type'] == 'many2one':

                # add value in the combobox
                self.insField.addItem( sParent+'/'+name,0)

                # control the dupplication of data
                if not oTable==res['fields'][name]['relation']:
                    if nCount<3:
                        sParent=sParent+'/'+name
                        nCount=nCount+1
                        # call same function (recursion)
                        sParent=self.genTree(oSocket, res['fields'][name]['relation'], sParent ,nCount)
                    else:
                        nCount=nCount-1
                        sParent =  sParent.__getslice__(0,sParent.rfind('/'))
                        return sParent
                #End if
            else:

                # add value in the combobox
                self.insField.addItem(sParent+'/'+name,0)
            #End if
        nCount=nCount-1
        sParent =  sParent.__getslice__(0,sParent.rfind('/'))
        return sParent
    def getModule(self,oSocket):
        res = oSocket.execute('terp', 3, 'admin', 'ir.model', 'read',
                              [58, 13, 94, 40, 67, 12, 5, 32, 9, 21, 97, 30, 18, 112, 2, 46, 62, 3,
                               19, 92, 8, 1, 105, 49, 70, 96, 50, 47, 53, 42, 95, 43, 71, 72, 64, 73,
                               102, 103, 7, 75, 107, 76, 77, 74, 17, 79, 78, 80, 63, 81, 82, 14, 83,
                               84, 85, 86, 87, 26, 39, 88, 11, 69, 91, 57, 16, 89, 10, 101, 36, 66, 45,
                               54, 106, 38, 44, 60, 55, 25, 4, 51, 65, 109, 34, 33, 52, 61, 28, 41, 59,
                               108, 110, 31, 99, 104, 93, 56, 35, 37, 27, 98, 24, 100, 6, 15, 48, 90,
                               111, 20, 22, 23, 29, 68], ['name','model'],
                               {'active_ids': [57], 'active_id': 57})
        nIndex = 0
        while nIndex <= res.__len__()-1:
            self.insVariable.addItem(res[nIndex]['model'],0)
            nIndex += 1


g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationHelper.addImplementation( \
        Fields,
        "org.openoffice.tiny.report.fields",
        ("com.sun.star.task.Job",),)





class Expression( unohelper.Base, XJobExecutor ):
    def __init__( self, ctx ):
        self.ctx     = ctx
        self.module  = "tiny_report"
        self.version = "0.1"
        self.win=None
    def trigger( self, args ):
        self.win = DBModalDialog(60, 50, 140, 90, "Expression Builder")
        self.win.addFixedText("lblName", 5, 10, 20, 15, "Name :")
        self.win.addEdit("txtName", 30, 5, 100, 15, "Enter Name",)
        self.win.addFixedText("lblExpression",5 , 30, 25, 15, "Expression :")
        self.win.addEdit("txtExpression", 30, 25, 100, 15, "Enter Expression",)
        self.win.addButton( "btnOK", -10, -10, 30, 15, "OK",
                        actionListenerProc = self.btnOkOrCancel_clicked )
        self.win.addButton( "btnCancel", -10 - 30 -5, -10, 30, 15, "Cancel",
                        actionListenerProc = self.btnOkOrCancel_clicked )
        self.win.doModalDialog()
#        text.insertString(cursor, "7", 0 )

    def btnOkOrCancel_clicked( self, oActionEvent):
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

        elif oActionEvent.Source.getModel().Name == "btnCancel":
            self.win.endExecute()




g_ImplementationHelper.addImplementation( \
        Expression,
        "org.openoffice.tiny.report.expression",
        ("com.sun.star.task.Job",),)


class Repeatln( unohelper.Base, XJobExecutor ):
    def __init__( self, ctx ):
        self.ctx     = ctx
        self.module  = "tiny_report"
        self.version = "0.1"
        self.win=None
    def trigger( self, args ):
        self.win = DBModalDialog(60, 50, 140, 250, "Field Builder")
        self.win.addFixedText("lblName", 10, 12, 20, 15, "Name :")
        self.win.addEdit("txtName", 35, 10, 100, 15, "Enter Name",)
        self.win.addFixedText("lblVariable", 5, 32, 25, 15, "Variable :")
        self.win.addComboBox("cmbVariable", 35, 30, 100, 15,True,
                             itemListenerProc=self.cmbVariable_selected)
        self.insVariable = self.win.getControl( "cmbVariable" )
        self.win.addFixedText("lblFields", 11, 52, 25, 15, "Fields :")
        self.win.addComboListBox("lstFields", 35, 50, 100, 150, False)
        self.insField = self.win.getControl( "lstFields" )
        import xmlrpclib
        sock = xmlrpclib.ServerProxy('http://localhost:8069/xmlrpc/object')
        self.getModule(sock)
        self.win.addButton('btnOK',-5 ,-25,45,15,'Ok'
                      ,actionListenerProc = self.btnOkOrCancel_clicked )
        self.win.addButton('btnCancel',-5 - 45 - 5 ,-25,45,15,'Cancel'
                      ,actionListenerProc = self.btnOkOrCancel_clicked )
        self.win.doModalDialog()

    def cmbVariable_selected(self,oItemEvent):

        import xmlrpclib
        sock = xmlrpclib.ServerProxy('http://localhost:8069/xmlrpc/object')
        self.win.removeListBoxItems("lstFields", 0, self.win.getListBoxItemCount("lstFields"))
        self.genTree(sock, self.win.getComboBoxSelectedText("cmbVariable"),'', 0)

    def btnOkOrCancel_clicked( self, oActionEvent ):
        #Called when the OK or Cancel button is clicked.
        if oActionEvent.Source.getModel().Name == "btnOK":
            self.bOkay = True
            localContext = uno.getComponentContext()
            resolver = localContext.ServiceManager.createInstanceWithContext(
                        "com.sun.star.bridge.UnoUrlResolver", localContext )
            ctx = resolver.resolve( "uno:socket,host=localhost,port=2002;urp;StarOffice.ComponentContext" )
            smgr = ctx.ServiceManager
            desktop = smgr.createInstanceWithContext( "com.sun.star.frame.Desktop",ctx)
            model = desktop.getCurrentComponent()
            text = model.Text
            cursor = text.createTextCursor()
            if self.win.getListBoxSelectedItem("lstFields") != "":
                text.insertString( cursor,self.win.getEditText("txtName") + ": [[" + self.win.getListBoxSelectedItem("lstFields")+"]]" , 0 )
        elif oActionEvent.Source.getModel().Name == "btnCancel":
            self.win.endExecute()
    # this method will featch data from the database and place it in the combobox
    def genTree(self, oSocket, oTable, sParent ,nCount):

        # returieve metadata of pertucular table form the database
        res = oSocket.execute('terp', 3, 'admin', oTable, 'fields_view_get')
        for name in res['fields'].keys():

            # check for field type if many to one tehn execute code
            if res['fields'][name]['type'] == 'one2many':

                # add value in the combobox
                self.insField.addItem( sParent+'/'+name,0)

                # control the dupplication of data
                if not oTable==res['fields'][name]['relation']:
                    if nCount<3:
                        sParent=sParent+'/'+name
                        nCount=nCount+1
                        # call same function (recursion)
                        sParent=self.genTree(oSocket, res['fields'][name]['relation'], sParent ,nCount)
                    else:
                        nCount=nCount-1
                        sParent =  sParent.__getslice__(0,sParent.rfind('/'))
                        return sParent
                #End if
            else:

                # add value in the combobox
                self.insField.addItem(sParent+'/'+name,0)
            #End if
        nCount=nCount-1
        sParent =  sParent.__getslice__(0,sParent.rfind('/'))
        return sParent
    def getModule(self,oSocket):
        res = oSocket.execute('terp', 3, 'admin', 'ir.model', 'read',
                              [58, 13, 94, 40, 67, 12, 5, 32, 9, 21, 97, 30, 18, 112, 2, 46, 62, 3,
                               19, 92, 8, 1, 105, 49, 70, 96, 50, 47, 53, 42, 95, 43, 71, 72, 64, 73,
                               102, 103, 7, 75, 107, 76, 77, 74, 17, 79, 78, 80, 63, 81, 82, 14, 83,
                               84, 85, 86, 87, 26, 39, 88, 11, 69, 91, 57, 16, 89, 10, 101, 36, 66, 45,
                               54, 106, 38, 44, 60, 55, 25, 4, 51, 65, 109, 34, 33, 52, 61, 28, 41, 59,
                               108, 110, 31, 99, 104, 93, 56, 35, 37, 27, 98, 24, 100, 6, 15, 48, 90,
                               111, 20, 22, 23, 29, 68], ['name','model'],
                               {'active_ids': [57], 'active_id': 57})
        nIndex = 0
        while nIndex <= res.__len__()-1:
            self.insVariable.addItem(res[nIndex]['model'],0)
            nIndex += 1



g_ImplementationHelper.addImplementation( \
        Repeatln,
        "org.openoffice.tiny.report.repeatln",
        ("com.sun.star.task.Job",),)
