import re
import uno
import string
import unohelper
from com.sun.star.task import XJobExecutor
from lib.gui import *
#from lib.functions import *
#from lib.error import *
import xmlrpclib


class modify:

    def __init__(self):
        localContext = uno.getComponentContext()
        resolver = localContext.ServiceManager.createInstanceWithContext(
                        "com.sun.star.bridge.UnoUrlResolver", localContext )
        smgr = resolver.resolve( "uno:socket,host=localhost,port=2002;urp;StarOffice.ServiceManager" )
        remoteContext = smgr.getPropertyValue( "DefaultContext" )
        desktop = smgr.createInstanceWithContext( "com.sun.star.frame.Desktop",remoteContext)
        Doc =desktop.getCurrentComponent()
        self.oVC = Doc.CurrentController.getViewCursor()
        # Variable Declaration
        self.sObj=None
        self.count=0
        self.aItemList=[]
        self.aComponentAdd=[]
        self.aObjectList=[]
        # Call method to perform Enumration on Report Document
        self.EnumDocument()
        # Perform checking that Field-1 and Field - 4 is available or not alos get Combobox
        # filled if condition is true
        desktop=getDesktop()
        doc =desktop.getCurrentComponent()
        docinfo=doc.getDocumentInfo()
        self.oMyObject=None
        # Check weather Field-1 is available if not then exit from application
        if not docinfo.getUserFieldValue(0)=="":
            self.sMyHost= docinfo.getUserFieldValue(0)
        else:
            print "Insert Field-1"
            self.win.endExecute()
        # Check weather Field-4 is available or not otherwise exit from application
        if not docinfo.getUserFieldValue(3)=="":
            if self.oVC.TextField:
                self.oCurObj=self.oVC.TextField
                self.oMyObject= self.getOperation(self.oVC.TextField.Items.__getitem__(1))
                if self.oMyObject.__getitem__(0) == "field":
                    self.win = DBModalDialog(60, 50, 140, 250, "Field Builder")
                    self.win.addFixedText("lblVariable", 3, 12, 30, 15, "Variable :")

                    self.win.addComboBox("cmbVariable", 30, 10, 105, 15,True,
                                        itemListenerProc=self.cmbVariable_selected)

                    self.insVariable = self.win.getControl( "cmbVariable" )
                    self.win.addFixedText("lblUName", 8, 32, 40, 15, "Name :")
                    self.win.addEdit("txtUName", 30, 30, 105, 15,)
                    self.win.addFixedText("lblFields", 10, 52, 25, 15, "Fields :")
                    self.win.addComboListBox("lstFields", 30, 50, 105, 150, False)
                    self.insField = self.win.getControl( "lstFields" )
                    self.win.addButton('btnOK',-5 ,-25,45,15,'Ok'
                                 ,actionListenerProc = self.btnOkOrCancel_clicked )
                    self.win.addButton('btnCancel',-5 - 45 - 5 ,-25,45,15,'Cancel'
                                  ,actionListenerProc = self.btnOkOrCancel_clicked )
                    print self.oMyObject
                    #self.win.selectListBoxItem( self, cCtrlName, cItemText, bSelect=True )

                    self.count=0
                    oParEnum = doc.getTextFields().createEnumeration()
                    while oParEnum.hasMoreElements():
                        oPar = oParEnum.nextElement()
                        if oPar.supportsService("com.sun.star.text.TextField.DropDown"):
                            self.count += 1
                    self.getList()
                    cursor = doc.getCurrentController().getViewCursor()
                    text=cursor.getText()
                    tcur=text.createTextCursorByRange(cursor)
                    for j in range(self.aObjectList.__len__()):
                        if self.aObjectList[j].__getslice__(0,self.aObjectList[j].find("(")) == "Objects":
                            self.insVariable.addItem(self.aObjectList[j],1)
                    for i in range(self.aItemList.__len__()):
                        if self.aComponentAdd[i]=="Document":
                            sLVal=self.aItemList[i].__getitem__(1).__getslice__(self.aItemList[i].__getitem__(1).find(",'")+2,self.aItemList[i].__getitem__(1).find("')"))
                            for j in range(self.aObjectList.__len__()):
                                if self.aObjectList[j].__getslice__(0,self.aObjectList[j].find("(")) == sLVal:
                                    self.insVariable.addItem(self.aObjectList[j],1)
                        if tcur.TextSection:
                            if self.aComponentAdd[i]== tcur.TextSection.Name:
                                sLVal=self.aItemList[i].__getitem__(1).__getslice__(self.aItemList[i].__getitem__(1).find(",'")+2,self.aItemList[i].__getitem__(1).find("')"))
                                for j in range(self.aObjectList.__len__()):
                                    if self.aObjectList[j].__getslice__(0,self.aObjectList[j].find("(")) == sLVal:
                                        self.insVariable.addItem(self.aObjectList[j],1)
                        if tcur.TextTable:
                            if not self.aComponentAdd[i] == "Document" and self.aComponentAdd[i].__getslice__(self.aComponentAdd[i].rfind(".")+1,self.aComponentAdd[i].__len__())== tcur.TextTable.Name:
                                self.VariableScope(tcur,self.aComponentAdd[i])#self.aComponentAdd[i].__getslice__(self.aComponentAdd[i].rfind(".")+1,self.aComponentAdd[i].__len__())

                    self.win.setEditText("txtUName",self.oMyObject.__getitem__(1).__getslice__(0,self.oMyObject.__getitem__(1).find(".")))
                    j=0
                    for j in range(self.aObjectList.__len__()):
                        if self.aObjectList[j].__getslice__(0,self.aObjectList[j].find("(")) == self.oMyObject.__getitem__(1).__getslice__(0,self.oMyObject.__getitem__(1).find(".")):
                            #self.win.setComboBoxText( "cmbVariable", self.aObjectList[j] )
                            self.genTree(self.aObjectList[j].__getslice__(self.aObjectList[j].find("(")+1,self.aObjectList[j].__len__()-1),1,ending_excl=['one2many','many2one','many2many','reference'], recur=['many2one'])
                    self.win.doModalDialog()

                if self.oMyObject.__getitem__(0) == "expression":
                    self.win = DBModalDialog(60, 50, 140, 90, "Expression Builder")
                    self.win.addFixedText("lblName", 5, 10, 20, 15, "Name :")
                    self.win.addEdit("txtName", 30, 5, 100, 15)
                    self.win.setEditText("txtName",self.oCurObj.Items.__getitem__(0))
                    self.win.addFixedText("lblExpression",5 , 30, 25, 15, "Expression :")
                    self.win.addEdit("txtExpression", 30, 25, 100, 15)
                    self.win.setEditText("txtExpression",self.oMyObject.__getitem__(1))
                    self.win.addButton( "btnOK", -10, -10, 30, 15, "OK",
                                    actionListenerProc = self.btnOkOrCancel_clicked )
                    self.win.addButton( "btnCancel", -10 - 30 -5, -10, 30, 15, "Cancel",
                                    actionListenerProc = self.btnOkOrCancel_clicked )
                    self.win.doModalDialog()

                if self.oMyObject.__getitem__(0)=="repeatIn":
                    self.win = DBModalDialog(60, 50, 140, 250, "RepeatIn Builder")
                    self.win.addFixedText("lblVariable", 18, 12, 30, 15, "Variable :")
                    self.win.addComboBox("cmbVariable", 45, 10, 90, 15,True,
                                        itemListenerProc=self.cmbVariable_selected)
                    self.insVariable = self.win.getControl( "cmbVariable" )
                    self.win.addFixedText("lblName", 5, 32, 40, 15, "Object Name :")
                    self.win.addEdit("txtName", 45, 30, 90, 15,)
                    self.win.addFixedText("lblUName", 24, 52, 40, 15, "Name :")
                    self.win.addEdit("txtUName", 45, 50, 90, 15,)
                    self.win.addFixedText("lblFields", 25, 72, 25, 15, "Fields :")
                    self.win.addComboListBox("lstFields", 45, 70, 90, 150, False)
                    self.insField = self.win.getControl( "lstFields" )
                    self.win.addButton('btnOK',-5 ,-10,45,15,'Ok'
                                  ,actionListenerProc = self.btnOkOrCancel_clicked )
                    self.win.addButton('btnCancel',-5 - 45 - 5 ,-10,45,15,'Cancel'
                                  ,actionListenerProc = self.btnOkOrCancel_clicked )
                    print self.oMyObject
                    self.count=0
                    oParEnum = doc.getTextFields().createEnumeration()
                    while oParEnum.hasMoreElements():
                        oPar = oParEnum.nextElement()
                        if oPar.supportsService("com.sun.star.text.TextField.DropDown"):
                            self.count += 1
                    self.getList()
                    cursor = doc.getCurrentController().getViewCursor()
                    text=cursor.getText()
                    tcur=text.createTextCursorByRange(cursor)
                    for j in range(self.aObjectList.__len__()):
                        if self.aObjectList[j].__getslice__(0,self.aObjectList[j].find("(")) == "Objects":
                            self.insVariable.addItem(self.aObjectList[j],1)
                    for i in range(self.aItemList.__len__()):
                        if self.aComponentAdd[i]=="Document":
                            sLVal=self.aItemList[i].__getitem__(1).__getslice__(self.aItemList[i].__getitem__(1).find(",'")+2,self.aItemList[i].__getitem__(1).find("')"))
                            for j in range(self.aObjectList.__len__()):
                                if self.aObjectList[j].__getslice__(0,self.aObjectList[j].find("(")) == sLVal:
                                    self.insVariable.addItem(self.aObjectList[j],1)
                        if tcur.TextSection:
                            if self.aComponentAdd[i]== tcur.TextSection.Name:
                                sLVal=self.aItemList[i].__getitem__(1).__getslice__(self.aItemList[i].__getitem__(1).find(",'")+2,self.aItemList[i].__getitem__(1).find("')"))
                                for j in range(self.aObjectList.__len__()):
                                    if self.aObjectList[j].__getslice__(0,self.aObjectList[j].find("(")) == sLVal:
                                        self.insVariable.addItem(self.aObjectList[j],1)
                        if tcur.TextTable:
                            if not self.aComponentAdd[i] == "Document" and self.aComponentAdd[i].__getslice__(self.aComponentAdd[i].rfind(".")+1,self.aComponentAdd[i].__len__())== tcur.TextTable.Name:
                                self.VariableScope(tcur,self.aComponentAdd[i])

                    self.win.setEditText("txtUName",self.oVC.TextField.Items.__getitem__(0))
                    self.win.setEditText("txtName",self.oMyObject.__getitem__(2))
                    j=0
                    print self.oMyObject

                    for j in range(self.aObjectList.__len__()):
                        if self.aObjectList[j].__getslice__(0,self.aObjectList[j].find("(")) == self.oMyObject.__getitem__(1).__getslice__(0,self.oMyObject.__getitem__(1).find(".")):
                            #self.win.setComboBoxSelectedText( "cmbVariable", self.aObjectList[j] )

                            self.genTree(self.aObjectList[j].__getslice__(self.aObjectList[j].find("(")+1,self.aObjectList[j].__len__()-1),1,ending=['one2many','many2many'], recur=['one2many','many2many'])

                    self.win.doModalDialog()

        else:
            print "Insert Field-4"

    def getOperation(self, str):
        #str = "[[ RepeatIn(objects, 'variable') ]]" #repeatIn
        #str = "[[ saleorder.partner_id.name ]]" # field
        #str = "[[ some thing complex ]]" # expression
        method1 = lambda x: (u'repeatIn', x.group(1), x.group(2))
        method2 = lambda x: (u'field', x.group(1))
        method3 = lambda x: (u'expression', x.group(1))
        regexes = [
                ('\\[\\[ *repeatIn\\( *(.+)*, *\'([a-zA-Z0-9_]+)\' *\\) *\\]\\]', method1),
                ('\\[\\[ *([a-zA-Z0-9_\.]+) *\\]\\]', method2),
                ('\\[\\[ *(.+) *\\]\\]', method3)
        ]
        for (rule,method) in regexes:
                res= re.match(rule, str)
                if res:
                        return method(res)
                        break

    def cmbVariable_selected(self,oItemEvent):
        if self.count > 0 :
            sock = xmlrpclib.ServerProxy(self.sMyHost + '/xmlrpc/object')
            desktop=getDesktop()
            doc =desktop.getCurrentComponent()
            docinfo=doc.getDocumentInfo()
            self.win.removeListBoxItems("lstFields", 0, self.win.getListBoxItemCount("lstFields"))
            sItem=self.win.getComboBoxSelectedText("cmbVariable")
            if self.oMyObject.__getitem__(0)=="repeatIn":
                self.genTree(sItem.__getslice__(sItem.find("(")+1,sItem.find(")")),1,ending=['one2many','many2many'], recur=['one2many','many2many'])
            if self.oMyObject.__getitem__(0)=="field":
                self.genTree(sItem.__getslice__(sItem.find("(")+1,sItem.find(")")),1,ending_excl=['one2many','many2one','many2many','reference'], recur=['many2one'])
        else:
            if self.oMyObject.__getitem__(0)=="repeatIn":
                self.insField.addItem("objects",self.win.getListBoxItemCount("lstFields"))

    def btnOkOrCancel_clicked( self, oActionEvent ):
        if oActionEvent.Source.getModel().Name == "btnOK":
            desktop=getDesktop()
            doc = desktop.getCurrentComponent()
            text = doc.Text
            if self.oMyObject.__getitem__(0)=="expression":
                if self.win.getEditText("txtName")!="" and self.win.getEditText("txtExpression")!="":
                    sKey=u""+self.win.getEditText("txtName")
                    sValue=u"[[ " + self.win.getEditText("txtExpression") + " ]]"
                    self.oCurObj.Items = (sKey,sValue)
                    self.oCurObj.update()
            if self.oMyObject.__getitem__(0)=="repeatIn":
                if self.win.getListBoxSelectedItem("lstFields") != "" and self.win.getEditText("txtName") != "" and self.win.getEditText("txtUName") != "" :
                    if self.win.getListBoxSelectedItem("lstFields") == "objects":
                        sKey=u""+ self.win.getEditText("txtUName")
                        sValue=u"[[ repeatIn(" + self.win.getListBoxSelectedItem("lstFields") + ",'" + self.win.getEditText("txtName") + "') ]]"
                        oInputList.Items = (sKey,sValue)
                        self.oCurObj.Items = (sKey,sValue)
                        self.oCurObj.update()
                    else:
                        sObjName=self.win.getComboBoxSelectedText("cmbVariable")
                        sObjName=sObjName.__getslice__(0,sObjName.find("("))
                        sKey=u""+ self.win.getEditText("txtUName")
                        sValue=u"[[ repeatIn(" + sObjName + self.win.getListBoxSelectedItem("lstFields").replace("/",".") + ",'" + self.win.getEditText("txtName") +"') ]]"

                        self.oCurObj.Items = (sKey,sValue)
                        self.oCurObj.update()
            if self.oMyObject.__getitem__(0)=="field":
                if self.win.getListBoxSelectedItem("lstFields") != "" and self.win.getEditText("txtUName") != "" :

                    sObjName=self.win.getComboBoxSelectedText("cmbVariable")
                    print sObjName
                    sObjName=sObjName.__getslice__(0,sObjName.find("("))
                    print sObjName
                    sKey=u""+ self.win.getEditText("txtUName")
                    sValue=u"[[ " + sObjName + self.win.getListBoxSelectedItem("lstFields").replace("/",".") + " ]]"
                    self.oCurObj.Items = (sKey,sValue)
                    self.oCurObj.update()
            self.win.endExecute()
        elif oActionEvent.Source.getModel().Name == "btnCancel":
            self.win.endExecute()

    def getDesktop(self):
        localContext = uno.getComponentContext()
        resolver = localContext.ServiceManager.createInstanceWithContext(
                        "com.sun.star.bridge.UnoUrlResolver", localContext )
        smgr = resolver.resolve( "uno:socket,host=localhost,port=2002;urp;StarOffice.ServiceManager" )
        remoteContext = smgr.getPropertyValue( "DefaultContext" )
        desktop = smgr.createInstanceWithContext( "com.sun.star.frame.Desktop",remoteContext)
        return desktop

    def EnumDocument(self):
        desktop = self.getDesktop()
        Doc =desktop.getCurrentComponent()
        oParEnum = Doc.getText().createEnumeration()
        while oParEnum.hasMoreElements():
            oPar = oParEnum.nextElement()
            if oPar.supportsService("com.sun.star.text.TextTable"):
                self.getChildTable(oPar)
            if oPar.supportsService("com.sun.star.text.Paragraph"):
                oSecEnum = oPar.createEnumeration()
                while oSecEnum.hasMoreElements():
                    oSubSection = oSecEnum.nextElement()
                    if oSubSection.TextSection:
                        if oSubSection.TextField:
                            self.aItemList.append( oSubSection.TextField.Items )
                            self.aComponentAdd.append(oSubSection.TextSection.Name)
                    elif oPar.getAnchor().TextField:
                        sItem=oPar.getAnchor().TextField.Items.__getitem__(1)
                        if sItem.__getslice__(sItem.find("[[ ")+3,sItem.find("("))=="repeatIn":
                            self.aItemList.append(oSubSection.TextField.Items )
                            self.aComponentAdd.append("Document")

    def VariableScope(self,oTcur,sTableName=""):
        if sTableName.find(".") != -1:
            for i in range(self.aItemList.__len__()):
                if self.aComponentAdd[i]==sTableName:
                    sLVal=self.aItemList[i].__getitem__(1).__getslice__(self.aItemList[i].__getitem__(1).find(",'")+2,self.aItemList[i].__getitem__(1).find("')"))
                    for j in range(self.aObjectList.__len__()):
                        if self.aObjectList[j].__getslice__(0,self.aObjectList[j].find("(")) == sLVal:
                            self.insVariable.addItem(self.aObjectList[j],1)
            self.VariableScope(oTcur, sTableName.__getslice__(0,sTableName.rfind(".")))
        else:
             for i in range(self.aItemList.__len__()):
                if self.aComponentAdd[i]==sTableName:
                    sLVal=self.aItemList[i].__getitem__(1).__getslice__(self.aItemList[i].__getitem__(1).find(",'")+2,self.aItemList[i].__getitem__(1).find("')"))
                    for j in range(self.aObjectList.__len__()):
                        if self.aObjectList[j].__getslice__(0,self.aObjectList[j].find("(")) == sLVal:
                            self.insVariable.addItem(self.aObjectList[j],1)

    def getChildTable(self,oPar,sTableName=""):
        sNames = oPar.getCellNames()
        bEmptyTableFlag=True
        for val in sNames:
            oCell = oPar.getCellByName(val)
            #oTCurs = oCell.createTextCursor()
            oCurEnum = oCell.createEnumeration()
            while oCurEnum.hasMoreElements():
                try:
                    oCur = oCurEnum.nextElement()
                except:
                    Exception
                    print "Problem with writing in Table"
                if oCur.supportsService("com.sun.star.text.TextTable"):
                    if sTableName=="":
                        self.getChildTable(oCur,oPar.Name)
                    else:
                        self.getChildTable(oCur,sTableName+"."+oPar.Name)
                else:
                    oSecEnum = oCur.createEnumeration()
                    while oSecEnum.hasMoreElements():
                        oSubSection = oSecEnum.nextElement()
                        if oSubSection.supportsService("com.sun.star.text.TextField"):
                            bEmptyTableFlag=False
                            sItem=oSubSection.TextField.Items.__getitem__(1)
                            if sItem.__getslice__(sItem.find("[[ ")+3,sItem.find("("))=="repeatIn":
                                if self.aItemList.__contains__(oSubSection.TextField.Items)==False:
                                    self.aItemList.append(oSubSection.TextField.Items)
                                if sTableName=="":
                                    if  self.aComponentAdd.__contains__(oPar.Name)==False:
                                        self.aComponentAdd.append(oPar.Name)
                                else:
                                    if self.aComponentAdd.__contains__(sTableName+"."+oPar.Name)==False:
                                        self.aComponentAdd.append(sTableName+"."+oPar.Name)
        if bEmptyTableFlag==True:
            self.aItemList.append((u'',u''))
            if sTableName=="":
                if  self.aComponentAdd.__contains__(oPar.Name)==False:
                    self.aComponentAdd.append(oPar.Name)
            else:
                if self.aComponentAdd.__contains__(sTableName+"."+oPar.Name)==False:
                    self.aComponentAdd.append(sTableName+"."+oPar.Name)
        return 0

    def genTree(self,object,level=3, ending=[], ending_excl=[], recur=[], root=''):
        sock = xmlrpclib.ServerProxy(self.sMyHost + '/xmlrpc/object')
        res = sock.execute('terp', 3, 'admin', object , 'fields_get')
        key = res.keys()
        key.sort()
        for k in key:
            if (not ending or res[k]['type'] in ending) and ((not ending_excl) or not (res[k]['type'] in ending_excl)):
                self.insField.addItem(root+'/'+k,self.win.getListBoxItemCount("lstFields"))
            if (res[k]['type'] in recur) and (level>0):
                self.insField.addItem(root+'/'+k,self.win.getListBoxItemCount("lstFields"))
                self.genTree(res[k]['relation'], level-1, ending, ending_excl, recur, root+'/'+k)

    def getPath(self,sPath,sMain):
        desktop=getDesktop()
        doc =desktop.getCurrentComponent()
        oParEnum = doc.getTextFields().createEnumeration()
        while oParEnum.hasMoreElements():
            oPar = oParEnum.nextElement()
            if oPar.supportsService("com.sun.star.text.TextField.DropDown"):
                sItem=oPar.Items.__getitem__(1)
                if sPath.__getslice__(0,sPath.find(".")) == sMain:
                    break;
                else:
                    if sItem.__getslice__(sItem.find(",'")+2,sItem.find("')")) == sPath.__getslice__(0,sPath.find(".")):
                        sPath =  sItem.__getslice__(sItem.find("(")+1,sItem.find(",")) + sPath.__getslice__(sPath.find("."),sPath.__len__())
                        self.getPath(sPath, sMain)
        return sPath

    def getList(self):
        desktop=getDesktop()
        doc =desktop.getCurrentComponent()
        docinfo=doc.getDocumentInfo()
        sMain=""
        if not self.count == 0:
            if self.count >= 1:
                oParEnum = doc.getTextFields().createEnumeration()
                while oParEnum.hasMoreElements():
                    oPar = oParEnum.nextElement()
                    if oPar.supportsService("com.sun.star.text.TextField.DropDown"):
                        sItem=oPar.Items.__getitem__(1)
                        if sItem.__getslice__(sItem.find("(")+1,sItem.find(","))=="objects":
                            sMain = sItem.__getslice__(sItem.find(",'")+2,sItem.find("')"))
                oParEnum = doc.getTextFields().createEnumeration()
                if self.oMyObject.__getitem__(0)=="repeatIn":
                    self.aObjectList.append("Objects(" + docinfo.getUserFieldValue(3) + ")")
                while oParEnum.hasMoreElements():
                    oPar = oParEnum.nextElement()
                    if oPar.supportsService("com.sun.star.text.TextField.DropDown"):
                        sItem=oPar.Items.__getitem__(1)
                        if sItem.__getslice__(sItem.find("[[ ")+3,sItem.find("("))=="repeatIn":
                            if sItem.__getslice__(sItem.find("(")+1,sItem.find(","))=="objects":
                                self.aObjectList.append(sItem.__getslice__(sItem.rfind(",'")+2,sItem.rfind("')")) + "(" + docinfo.getUserFieldValue(3) + ")")
                            else:
                                sTemp=sItem.__getslice__(sItem.find("(")+1,sItem.find(","))
                                if sMain == sTemp.__getslice__(0,sTemp.find(".")):
                                    self.getRelation(docinfo.getUserFieldValue(3), sItem.__getslice__(sItem.find(".")+1,sItem.find(",")), sItem.__getslice__(sItem.find(",'")+2,sItem.find("')")))
                                else:
                                    sPath=self.getPath(sItem.__getslice__(sItem.find("(")+1,sItem.find(",")), sMain)
                                    self.getRelation(docinfo.getUserFieldValue(3), sPath.__getslice__(sPath.find(".")+1,sPath.__len__()), sItem.__getslice__(sItem.find(",'")+2,sItem.find("')")))
        else:
            self.aObjectList.append("Objects(" + docinfo.getUserFieldValue(3) + ")")


    def getPath(self,sPath,sMain):
        desktop=getDesktop()
        doc =desktop.getCurrentComponent()
        oParEnum = doc.getTextFields().createEnumeration()
        while oParEnum.hasMoreElements():
            oPar = oParEnum.nextElement()
            if oPar.supportsService("com.sun.star.text.TextField.DropDown"):
                sItem=oPar.Items.__getitem__(1)
                if sPath.__getslice__(0,sPath.find(".")) == sMain:
                    break;
                else:
                    if sItem.__getslice__(sItem.find(",'")+2,sItem.find("')")) == sPath.__getslice__(0,sPath.find(".")):
                        sPath =  sItem.__getslice__(sItem.find("(")+1,sItem.find(",")) + sPath.__getslice__(sPath.find("."),sPath.__len__())
                        self.getPath(sPath, sMain)
        return sPath

    def getRelation(self, sRelName, sItem, sObjName ):
        sock = xmlrpclib.ServerProxy(self.sMyHost + '/xmlrpc/object')
        res = sock.execute('terp', 3, 'admin', sRelName , 'fields_get')
        key = res.keys()
        for k in key:
            if sItem.find(".") == -1:
                if k == sItem:
                    self.aObjectList.append(sObjName + "(" + res[k]['relation'] + ")")
                    return 0
            if k == sItem.__getslice__(0,sItem.find(".")):
                self.getRelation(res[k]['relation'], sItem.__getslice__(sItem.find(".")+1,sItem.__len__()), sObjName)

#modify()