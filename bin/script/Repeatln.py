import uno
import string
import unohelper
import xmlrpclib
from com.sun.star.task import XJobExecutor
if __name__<>"package":
    from lib.gui import *
    from lib.error import ErrorDialog
    from lib.functions import *


#class RepeatIn:
class RepeatIn( unohelper.Base, XJobExecutor ):
    def __init__(self,sObject="",sVariable="",sFields="",sDisplayName="",bFromModify=False):
        # Interface Design
        self.win = DBModalDialog(60, 50, 180, 250, "RepeatIn Builder")
        self.win.addFixedText("lblVariable", 2, 12, 60, 15, "Objects to loop on :")
        self.win.addComboBox("cmbVariable", 180-120-2, 10, 120, 15,True,
                            itemListenerProc=self.cmbVariable_selected)
        self.insVariable = self.win.getControl( "cmbVariable" )

        self.win.addFixedText("lblFields", 10, 32, 60, 15, "Field to loop on :")
        self.win.addComboListBox("lstFields", 180-120-2, 30, 120, 150, False,itemListenerProc=self.lstbox_selected)
        self.insField = self.win.getControl( "lstFields" )

        self.win.addFixedText("lblName", 12, 187, 60, 15, "Variable name :")
        self.win.addEdit("txtName", 180-120-2, 185, 120, 15,)

        self.win.addFixedText("lblUName", 8, 207, 60, 15, "Displayed name :")
        self.win.addEdit("txtUName", 180-120-2, 205, 120, 15,)


        self.win.addButton('btnOK',-2 ,-10,45,15,'Ok'
                      ,actionListenerProc = self.btnOkOrCancel_clicked )

        self.win.addButton('btnCancel',-2 - 45 - 5 ,-10,45,15,'Cancel'
                      ,actionListenerProc = self.btnOkOrCancel_clicked )
        # Variable Declaration
        self.sValue=None
        self.sObj=None
        self.aSectionList=[]
        self.sGVariable=sVariable
        self.sGDisplayName=sDisplayName
        self.aItemList=[]
        self.aComponentAdd=[]
        self.aObjectList=[]
        self.aListRepeatIn=[]
        # Call method to perform Enumration on Report Document
        EnumDocument(self.aItemList,self.aComponentAdd)
        # Perform checking that Field-1 and Field - 4 is available or not alos get Combobox
        # filled if condition is true
        desktop=getDesktop()
        doc =desktop.getCurrentComponent()
        docinfo=doc.getDocumentInfo()
        # Check weather Field-1 is available if not then exit from application
        self.sMyHost= ""
        if not docinfo.getUserFieldValue(3) == "" and not docinfo.getUserFieldValue(0)=="":
            self.sMyHost= docinfo.getUserFieldValue(0)
            self.count=0
            oParEnum = doc.getTextFields().createEnumeration()
            while oParEnum.hasMoreElements():
                oPar = oParEnum.nextElement()
                if oPar.supportsService("com.sun.star.text.TextField.DropDown"):
                    self.count += 1
            getList(self.aObjectList, self.sMyHost,self.count)
            cursor = doc.getCurrentController().getViewCursor()
            text=cursor.getText()
            tcur=text.createTextCursorByRange(cursor)

            for j in range(self.aObjectList.__len__()):
                if self.aObjectList[j].__getslice__(0,self.aObjectList[j].find(" ")) == "List":
                    self.insVariable.addItem(self.aObjectList[j],1)
            for i in range(self.aItemList.__len__()):
                if self.aComponentAdd[i]=="Document":
                    sLVal=self.aItemList[i].__getitem__(1).__getslice__(self.aItemList[i].__getitem__(1).find(",'")+2,self.aItemList[i].__getitem__(1).find("')"))
                    for j in range(self.aObjectList.__len__()):
                        if self.aObjectList[j].__getslice__(0,self.aObjectList[j].find("(")) == sLVal:
                            self.insVariable.addItem(self.aObjectList[j],1)
                if tcur.TextSection:
                    getRecersiveSection(tcur.TextSection,self.aSectionList)
                    #for k in range(self.aSectionList.__len__()):
                    if self.aComponentAdd[i] in self.aSectionList:
                        sLVal=self.aItemList[i].__getitem__(1).__getslice__(self.aItemList[i].__getitem__(1).find(",'")+2,self.aItemList[i].__getitem__(1).find("')"))
                        for j in range(self.aObjectList.__len__()):
                            if self.aObjectList[j].__getslice__(0,self.aObjectList[j].find("(")) == sLVal:
                                self.insVariable.addItem(self.aObjectList[j],1)

                if tcur.TextTable:
                    if not self.aComponentAdd[i] == "Document" and self.aComponentAdd[i].__getslice__(self.aComponentAdd[i].rfind(".")+1,self.aComponentAdd[i].__len__())== tcur.TextTable.Name:
                        VariableScope(tcur,self.insVariable,self.aObjectList,self.aComponentAdd,self.aItemList,self.aComponentAdd[i])
            self.bModify=bFromModify
            if self.bModify==True:
                if sObject=="":
                    self.insVariable.setText("List of "+docinfo.getUserFieldValue(3))
                    self.insField.addItem("objects",self.win.getListBoxItemCount("lstFields"))
#                    self.win.setEditText("txtName", sVariable)
#                    self.win.setEditText("txtUName",sDisplayName)
                    self.sValue= "objects"
                else:
                    sItem=""
                    i=0
                    for i in range(self.aObjectList.__len__()):
                        if self.aObjectList[i].__getslice__(0,self.aObjectList[i].find("("))==sObject:
                            sItem= self.aObjectList[i]
                            self.insVariable.setText(sItem)
                    genTree(sItem.__getslice__(sItem.find("(")+1,sItem.find(")")), self.aListRepeatIn, self.insField, self.sMyHost, 2, ending=['one2many','many2many'], recur=['one2many','many2many'])
#                    self.win.setEditText("txtName", sVariable)
#                    self.win.setEditText("txtUName",sDisplayName)
                    self.sValue= self.win.getListBoxItem("lstFields",self.aListRepeatIn.index(sFields))
            self.win.doModalDialog("lstFields",self.sValue)
        else:
            ErrorDialog("Please insert user define field Field-1 or Field-4","Just go to File->Properties->User Define \nField-1 Eg. http://localhost:8069 \nOR \nField-4 Eg. account.invoice")
            self.win.endExecute()




    def getSection(self,oParEnum,oCurrentSection):
        while oParEnum.hasMoreElements():
            oPar = oParEnum.nextElement()
            if oPar.supportsService("com.sun.star.text.TextContent"):
                if oPar.TextSection:
                    if oPar.TextSection.Name==oCurrentSection.Name:
                        oInsideEnum=oPar.createEnumeration()
                        while oInsideEnum.hasMoreElements():
                            oInside=oInsideEnum.nextElement()
                            if oInside.supportsService("com.sun.star.text.TextPortion"):
                                if oInside.TextField:
                                    print oInside.TextField.Items
    def lstbox_selected(self,oItemEvent):
        sItem=self.win.getListBoxSelectedItem("lstFields")
        sMain=self.aListRepeatIn[self.win.getListBoxSelectedItemPos("lstFields")]
        if self.bModify==True:
            self.win.setEditText("txtName", self.sGVariable)
            self.win.setEditText("txtUName",self.sGDisplayName)
        else:
            self.win.setEditText("txtName",sMain.__getslice__(sMain.rfind("/")+1,sMain.__len__()))
            self.win.setEditText("txtUName","|-."+sItem.__getslice__(sItem.rfind("/")+1,sItem.__len__())+".-|")
    def cmbVariable_selected(self,oItemEvent):
        if self.count > 0 :
            sock = xmlrpclib.ServerProxy(self.sMyHost + '/xmlrpc/object')
            desktop=getDesktop()
            doc =desktop.getCurrentComponent()
            docinfo=doc.getDocumentInfo()
            self.win.removeListBoxItems("lstFields", 0, self.win.getListBoxItemCount("lstFields"))
            sItem=self.win.getComboBoxText("cmbVariable")
            self.aListRepeatIn=[]
            if sItem.__getslice__(sItem.rfind(" ")+1,sItem.__len__()) == docinfo.getUserFieldValue(3):
                genTree(docinfo.getUserFieldValue(3), self.aListRepeatIn, self.insField,self.sMyHost, 2, ending=['one2many','many2many'], recur=['one2many','many2many'])
            else:
                genTree(sItem.__getslice__(sItem.find("(")+1,sItem.find(")")), self.aListRepeatIn, self.insField,self.sMyHost,2,ending=['one2many','many2many'], recur=['one2many','many2many'])
            self.win.selectListBoxItemPos("lstFields", 0, True )

        else:
            sItem=self.win.getComboBoxText("cmbVariable")
            self.win.setEditText("txtName",sItem.__getslice__(sItem.rfind(".")+1,sItem.__len__()))
            self.win.setEditText("txtUName","|-."+sItem.__getslice__(sItem.rfind(".")+1,sItem.__len__())+".-|")
            self.insField.addItem("objects",self.win.getListBoxItemCount("lstFields"))
            self.win.selectListBoxItemPos("lstFields", 0, True )

    def btnOkOrCancel_clicked(self, oActionEvent):
        if oActionEvent.Source.getModel().Name == "btnOK":
            desktop=getDesktop()
            doc = desktop.getCurrentComponent()
            text = doc.Text
            cursor = doc.getCurrentController().getViewCursor()
            if self.win.getListBoxSelectedItem("lstFields") != "" and self.win.getEditText("txtName") != "" and self.win.getEditText("txtUName") != "" :
                sObjName=""
                if self.bModify==True:
                    oCurObj=cursor.TextField
                    if self.win.getListBoxSelectedItem("lstFields") == "objects":
                        sKey=u""+ self.win.getEditText("txtUName")
                        sValue=u"[[ repeatIn(" + self.win.getListBoxSelectedItem("lstFields") + ",'" + self.win.getEditText("txtName") + "') ]]"
                        oCurObj.Items = (sKey,sValue)
                        oCurObj.update()
                    else:
                        sObjName=self.win.getComboBoxText("cmbVariable")
                        sObjName=sObjName.__getslice__(0,sObjName.find("("))
                        sKey=u""+ self.win.getEditText("txtUName")
                        sValue=u"[[ repeatIn(" + sObjName + self.aListRepeatIn[self.win.getListBoxSelectedItemPos("lstFields")].replace("/",".") + ",'" + self.win.getEditText("txtName") +"') ]]"
                        oCurObj.Items = (sKey,sValue)
                        oCurObj.update()
                else:
                    oInputList = doc.createInstance("com.sun.star.text.TextField.DropDown")
                    if self.win.getListBoxSelectedItem("lstFields") == "objects":
                        sKey=u""+ self.win.getEditText("txtUName")
                        sValue=u"[[ repeatIn(" + self.win.getListBoxSelectedItem("lstFields") + ",'" + self.win.getEditText("txtName") + "') ]]"
                        oInputList.Items = (sKey,sValue)
                        text.insertTextContent(cursor,oInputList,False)
                    else:
                        sObjName=self.win.getComboBoxText("cmbVariable")
                        sObjName=sObjName.__getslice__(0,sObjName.find("("))
                        if cursor.TextTable==None:
                            sKey=u""+ self.win.getEditText("txtUName")
                            sValue=u"[[ repeatIn(" + sObjName + self.aListRepeatIn[self.win.getListBoxSelectedItemPos("lstFields")].replace("/",".") + ",'" + self.win.getEditText("txtName") +"') ]]"
                            oInputList.Items = (sKey,sValue)
                            text.insertTextContent(cursor,oInputList,False)
                        else:
                            oTable = cursor.TextTable
                            oCurCell = cursor.Cell
                            tableText = oTable.getCellByName( oCurCell.CellName )
                            sKey=u""+ self.win.getEditText("txtUName")
                            sValue=u"[[ repeatIn(" + sObjName + self.aListRepeatIn[self.win.getListBoxSelectedItemPos("lstFields")].replace("/",".") + ",'" + self.win.getEditText("txtName") +"') ]]"
                            oInputList.Items = (sKey,sValue)
                            tableText.insertTextContent(cursor,oInputList,False)
                self.win.endExecute()
            else:
                ErrorDialog("Please Fill appropriate data in Object Field or Name field \nor select perticular value from the list of fields")
        elif oActionEvent.Source.getModel().Name == "btnCancel":
            self.win.endExecute()

if __name__<>"package" and __name__=="__main__":
    RepeatIn()
elif __name__=="package":
    g_ImplementationHelper = unohelper.ImplementationHelper()
    g_ImplementationHelper.addImplementation( \
            RepeatIn,
            "org.openoffice.tiny.report.repeatln",
            ("com.sun.star.task.Job",),)

