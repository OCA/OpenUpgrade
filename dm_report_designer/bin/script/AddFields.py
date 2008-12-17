import uno
import string
import unohelper
import xmlrpclib
from com.sun.star.task import XJobExecutor
if __name__<>"package":
    from lib.gui import *
    from lib.functions import *
    from lib.error import ErrorDialog
    from LoginTest import *
    database="dm"
    uid = 1
    
class AddFields(unohelper.Base, XJobExecutor ):
    def __init__(self,sVariable="",sFields="",sDisplayName="",bFromModify=False):
        LoginTest()
        if not loginstatus and __name__=="package":
            exit(1)
        self.win = DBModalDialog(60, 50, 200, 225, "Field Builder")

        self.win.addFixedText("lblVariable", 27, 12, 60, 15, "Variable :")
        self.win.addComboBox("cmbVariable", 180-120-2, 10, 130, 15,True, itemListenerProc=self.cmbVariable_selected)
        self.insVariable = self.win.getControl( "cmbVariable" )

        self.win.addFixedText("lblFields", 10, 32, 60, 15, "Variable Fields :")
        self.win.addComboListBox("lstFields", 180-120-2, 30, 130, 150, False,True,itemListenerProc=self.lstbox_selected)
        self.insField = self.win.getControl( "lstFields" )

        self.win.addFixedText("lblUName", 8, 187, 60, 15, "Displayed name :")
        self.win.addEdit("txtUName", 180-120-2, 185, 130, 15,)

        self.win.addButton('btnOK',-5 ,-5,45,15,'Ok' ,actionListenerProc = self.btnOk_clicked )
        self.win.addButton('btnCancel',-5 - 45 - 5 ,-5,45,15,'Cancel' ,actionListenerProc = self.btnCancel_clicked )

        global passwd
        self.password = passwd

        self.sValue=None
        self.sObj=None
        self.aSectionList=[]
        self.sGDisplayName=sDisplayName
        self.aItemList=[]
        self.aComponentAdd=[]
        self.aObjectList=[]
        self.aListFields=[]
        self.aVariableList=[]
        EnumDocument(self.aItemList,self.aComponentAdd)
        desktop=getDesktop()
        doc =desktop.getCurrentComponent()
        docinfo=doc.getDocumentInfo()
        self.sMyHost= ""

        if not docinfo.getUserFieldValue(3) == "" and not docinfo.getUserFieldValue(0)=="":
            self.sMyHost = docinfo.getUserFieldValue(0)
            self.count = 0
            oParEnum = doc.getTextFields().createEnumeration()

            while oParEnum.hasMoreElements():
                oPar = oParEnum.nextElement()
                if oPar.supportsService("com.sun.star.text.TextField.DropDown"):
                    self.count += 1

            getList(self.aObjectList, self.sMyHost,self.count)
            cursor = doc.getCurrentController().getViewCursor()
            text = cursor.getText()
            tcur = text.createTextCursorByRange(cursor)
            self.aVariableList.extend( filter( lambda obj: obj[:obj.find("(")] == "Objects", self.aObjectList ) )
            for i in range(len(self.aItemList)):
                anItem = self.aItemList[i][1]
                component = self.aComponentAdd[i]
                if component == "Document":
                    sLVal = anItem.split("'")[-2]
                    self.aVariableList.extend( filter( lambda obj: obj[:obj.find("(")] == sLVal, self.aObjectList ) )
                if tcur.TextSection:
                    getRecersiveSection(tcur.TextSection,self.aSectionList)
                    if component in self.aSectionList:
                        sLVal = anItem[anItem.find(",'") + 2:anItem.find("')")]
                        self.aVariableList.extend( filter( lambda obj: obj[:obj.find("(")] == sLVal, self.aObjectList ) )
                if tcur.TextTable:
                    if not component == "Document" and component[component.rfind(".")+1:] == tcur.TextTable.Name:
                        VariableScope(tcur, self.aVariableList, self.aObjectList, self.aComponentAdd, self.aItemList, component)

            self.bModify=bFromModify
            if self.bModify==True:
                sItem=""
                for anObject in self.aObjectList:
                    if anObject[:anObject.find("(")] == sVariable:
                        sItem = anObject
                        self.insVariable.setText(sItem)
                genDmTree(
                    sItem[sItem.find("(")+1:sItem.find(")")],
                    self.aListFields,
                    self.insField,
                    self.sMyHost,
                    2,
                    ending_excl=['one2many','many2one','many2many','reference'],
                    recur=['many2one']
                )
                self.sValue= self.win.getListBoxItem("lstFields",self.aListFields.index(sFields))
            for var in self.aVariableList:
                    sock = xmlrpclib.ServerProxy(self.sMyHost + '/xmlrpc/object')
                    self.model_ids = sock.execute(database, uid, self.password, 'ir.model' ,  'search', [('model','=',var[var.find("(")+1:var.find(")")])])
                    fields=['name','model']
                    self.model_res = sock.execute(database, uid, self.password, 'ir.model', 'read', self.model_ids,fields)
                    if self.model_res <> []:
                        self.insVariable.addItem(var[:var.find("(")+1] + self.model_res[0]['name'] + ")" ,self.insVariable.getItemCount())
                    else:
                        self.insVariable.addItem(var ,self.insVariable.getItemCount())

            self.win.doModalDialog("lstFields",self.sValue)
        else:
            ErrorDialog("You have not selected document and model for \n the report.Please select it first from \n Direct Marketing Reporting ->Select Document")
            self.win.endExecute()

    def lstbox_selected(self,oItemEvent):
        try:
            sock = xmlrpclib.ServerProxy(self.sMyHost + '/xmlrpc/object')
            desktop=getDesktop()
            doc =desktop.getCurrentComponent()
            docinfo=doc.getDocumentInfo()
            sItem= self.win.getComboBoxText("cmbVariable")
            for var in self.aVariableList:
                if var[:var.find("(")+1]==sItem[:sItem.find("(")+1]:
                    sItem = var
            sMain=self.aListFields[self.win.getListBoxSelectedItemPos("lstFields")]
            sObject=self.getRes(sock,sItem[sItem.find("(")+1:-1],sMain[1:])
            ids = sock.execute(database, uid, self.password, sObject ,  'search', [])
            if ids:
                res = sock.execute(database, uid, self.password, sObject , 'read',[ids[0]])
                self.win.setEditText("txtUName",res[0][sMain[sMain.rfind("/")+1:]])
        except:
            import traceback;traceback.print_exc()
            self.win.setEditText("txtUName","TTT")
        if self.bModify:
            self.win.setEditText("txtUName",self.sGDisplayName)

    def getRes(self,sock ,sObject,sVar):
        desktop=getDesktop()
        doc =desktop.getCurrentComponent()
        docinfo=doc.getDocumentInfo()
        res = sock.execute(database, uid, self.password, sObject , 'fields_get')
        key = res.keys()
        key.sort()
        myval=None
        if not sVar.find("/")==-1:
            myval=sVar[:sVar.find("/")]
        else:
            myval=sVar
        if myval in key:
            if (res[myval]['type'] in ['many2one']):
                sObject = res[myval]['relation']
                return self.getRes(sock,res[myval]['relation'], sVar[sVar.find("/")+1:])
            else:
                return sObject

    def cmbVariable_selected(self,oItemEvent):
        if self.count > 0 :
            try:
                desktop=getDesktop()
                doc =desktop.getCurrentComponent()
                docinfo=doc.getDocumentInfo()
                self.win.removeListBoxItems("lstFields", 0, self.win.getListBoxItemCount("lstFields"))
                self.aListFields=[]
                tempItem = self.win.getComboBoxText("cmbVariable")
                for var in self.aVariableList:
                    if var[:var.find("(")] == tempItem[:tempItem.find("(")]:
                        sItem=var

                genDmTree(
                    sItem[sItem.find("(")+1:sItem.find(")")],
                    self.aListFields,
                    self.insField,
                    self.sMyHost,
                    2,
                    ending_excl=['one2many','many2one','many2many','reference'],
                    recur=['many2one']
                )
            except:
                import traceback;traceback.print_exc()

    def btnOk_clicked( self, oActionEvent ):
        desktop=getDesktop()
        doc = desktop.getCurrentComponent()
        cursor = doc.getCurrentController().getViewCursor()
        for i in self.win.getListBoxSelectedItemsPos("lstFields"):
                itemSelected = self.aListFields[i]
                itemSelectedPos = i
                txtUName=self.win.getEditText("txtUName")
                sKey=u""+txtUName
                if itemSelected != "" and txtUName != "" and self.bModify==True :
                    txtUName=self.sGDisplayName
                    sKey=u""+txtUName
                    txtUName=self.sGDisplayName
                    oCurObj=cursor.TextField
                    sObjName=self.insVariable.getText()
                    sObjName=sObjName[:sObjName.find("(")]
                    sValue=u"[[ " + sObjName + self.aListFields[itemSelectedPos].replace("/",".") + " ]]"
                    oCurObj.Items = (sKey,sValue)
                    oCurObj.update()
                    self.win.endExecute()
                elif itemSelected != "" and txtUName != "" :

                    oInputList = doc.createInstance("com.sun.star.text.TextField.DropDown")
                    sObjName=self.win.getComboBoxText("cmbVariable")
                    sObjName=sObjName[:sObjName.find("(")]

                    widget = ( cursor.TextTable and cursor.TextTable.getCellByName( cursor.Cell.CellName ) or doc.Text )

                    sValue = u"[[ " + sObjName + self.aListFields[itemSelectedPos].replace("/",".") + " ]]"
                    oInputList.Items = (sKey,sValue)
                    widget.insertTextContent(cursor,oInputList,False)
                    self.win.endExecute()
                else:
                        ErrorDialog("Please Fill appropriate data in Name field \nor select perticular value from the list of fields")

    def btnCancel_clicked( self, oActionEvent ):
        self.win.endExecute()

if __name__<>"package" and __name__=="__main__":
    AddFields()
elif __name__=="package":
    g_ImplementationHelper.addImplementation( AddFields, "org.openoffice.openerp.report.addfields", ("com.sun.star.task.Job",),)
