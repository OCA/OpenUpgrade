import uno
import string
import unohelper
from com.sun.star.task import XJobExecutor
from lib.gui import *
import xmlrpclib

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

class RepeatIn:
    def __init__(self):
        # Interface Design

        self.win = DBModalDialog(60, 50, 150, 250, "RepeatIn Builder")
        self.win.addFixedText("lblVariable", 2, 12, 60, 15, "Objects to loop on :")
        self.win.addComboBox("cmbVariable", 150-90-2, 10, 90, 15,True,
                            itemListenerProc=self.cmbVariable_selected)

        self.win.addFixedText("lblFields", 10, 32, 60, 15, "Field to loop on :")
        self.win.addComboListBox("lstFields", 150-90-2, 30, 90, 150, False)

        self.insVariable = self.win.getControl( "cmbVariable" )
        self.win.addFixedText("lblName", 12, 187, 60, 15, "Variable name :")
        self.win.addEdit("txtName", 150-90-2, 185, 90, 15,)

        self.win.addFixedText("lblUName", 8, 207, 60, 15, "Displayed name :")
        self.win.addEdit("txtUName", 150-90-2, 205, 90, 15,)

        self.insField = self.win.getControl( "lstFields" )
        self.win.addButton('btnOK',-2 ,-10,45,15,'Ok'
                      ,actionListenerProc = self.btnOkOrCancel_clicked )

        self.win.addButton('btnCancel',-2 - 45 - 5 ,-10,45,15,'Cancel'
                      ,actionListenerProc = self.btnOkOrCancel_clicked )
        # Variable Declaration
        self.sObj=None
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
            self.win.doModalDialog()
        else:
            ErrorDialog("Please insert user define field Field-1 or Field-4","Just go to File->Properties->User Define \nField-1 Eg. http://localhost:8069 \nOR \nField-4 Eg. account.invoice")
            self.win.endExecute()

    def getDesktop(self):
        localContext = uno.getComponentContext()
        resolver = localContext.ServiceManager.createInstanceWithContext(
                        "com.sun.star.bridge.UnoUrlResolver", localContext )
        smgr = resolver.resolve( "uno:socket,host=localhost,port=2002;urp;StarOffice.ServiceManager" )
        remoteContext = smgr.getPropertyValue( "DefaultContext" )
        desktop = smgr.createInstanceWithContext( "com.sun.star.frame.Desktop",remoteContext)
        return desktop

    def cmbVariable_selected(self,oItemEvent):
        if self.count > 0 :
            sock = xmlrpclib.ServerProxy(self.sMyHost + '/xmlrpc/object')
            print sock
            desktop=getDesktop()
            doc =desktop.getCurrentComponent()
            docinfo=doc.getDocumentInfo()
            self.win.removeListBoxItems("lstFields", 0, self.win.getListBoxItemCount("lstFields"))
            sItem=self.win.getComboBoxSelectedText("cmbVariable")
            self.genTree(sItem.__getslice__(sItem.find("(")+1,sItem.find(")")),2,ending=['one2many','many2many'], recur=['one2many','many2many'])
        else:
            self.insField.addItem("objects",self.win.getListBoxItemCount("lstFields"))

    def btnOkOrCancel_clicked( self, oActionEvent ):
        if oActionEvent.Source.getModel().Name == "btnOK":
            desktop=getDesktop()
            doc = desktop.getCurrentComponent()
            text = doc.Text
            cursor = doc.getCurrentController().getViewCursor()
            if self.win.getListBoxSelectedItem("lstFields") != "" and self.win.getEditText("txtName") != "" and self.win.getEditText("txtUName") != "" :
                sObjName=""
                oInputList = doc.createInstance("com.sun.star.text.TextField.DropDown")
                if self.win.getListBoxSelectedItem("lstFields") == "objects":
                    sKey=u""+ self.win.getEditText("txtUName")
                    sValue=u"[[ repeatIn(" + self.win.getListBoxSelectedItem("lstFields") + ",'" + self.win.getEditText("txtName") + "') ]]"
                    oInputList.Items = (sKey,sValue)
                    text.insertTextContent(cursor,oInputList,False)
                else:
                    sObjName=self.win.getComboBoxSelectedText("cmbVariable")
                    sObjName=sObjName.__getslice__(0,sObjName.find("("))
                    if cursor.TextTable==None:
                        sKey=u""+ self.win.getEditText("txtUName")
                        sValue=u"[[ repeatIn(" + sObjName + self.win.getListBoxSelectedItem("lstFields").replace("/",".") + ",'" + self.win.getEditText("txtName") +"') ]]"
                        oInputList.Items = (sKey,sValue)
                        text.insertTextContent(cursor,oInputList,False)
                    else:
                        oTable = cursor.TextTable
                        oCurCell = cursor.Cell
                        tableText = oTable.getCellByName( oCurCell.CellName )
                        #cursor = tableText.createTextCursor()
                        #cursor.gotoEndOfParagraph(True)
                        sKey=u""+ self.win.getEditText("txtUName")
                        sValue=u"[[ repeatIn(" + sObjName + self.win.getListBoxSelectedItem("lstFields").replace("/",".") + ",'" + self.win.getEditText("txtName") +"') ]]"
                        oInputList.Items = (sKey,sValue)
                        tableText.insertTextContent(cursor,oInputList,False)
                self.win.endExecute()
            else:
                ErrorDialog("Please Fill appropriate data in Object Field or Name field \nor select perticular value from the list of fields")
        elif oActionEvent.Source.getModel().Name == "btnCancel":
            self.win.endExecute()

    def genTree(self,object,level=3, ending=[], ending_excl=[], recur=[], root=''):
        sock = xmlrpclib.ServerProxy(self.sMyHost+'/xmlrpc/object')
        print sock
        res = sock.execute('terp', 3, 'admin', object , 'fields_get')
        key = res.keys()
        key.sort()
        for k in key:
            if (not ending or res[k]['type'] in ending) and ((not ending_excl) or not (res[k]['type'] in ending_excl)):
                self.insField.addItem(root+'/'+k,self.win.getListBoxItemCount("lstFields"))
            if (res[k]['type'] in recur) and (level>0):
                self.genTree(res[k]['relation'], level-1, ending, ending_excl, recur, root+'/'+k)

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
        sock = xmlrpclib.ServerProxy(self.sMyHost+'/xmlrpc/object')
        res = sock.execute('terp', 3, 'admin', sRelName , 'fields_get')
        key = res.keys()
        for k in key:
            if sItem.find(".") == -1:
                if k == sItem:
                    self.aObjectList.append(sObjName + "(" + res[k]['relation'] + ")")
                    return 0
            if k == sItem.__getslice__(0,sItem.find(".")):
                self.getRelation(res[k]['relation'], sItem.__getslice__(sItem.find(".")+1,sItem.__len__()), sObjName)

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

    def EnumDocument(self):
        desktop = self.getDesktop()
        Doc =desktop.getCurrentComponent()
        oVC = Doc.CurrentController.getViewCursor()
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

    def getChildTable(self,oPar,sTableName=""):
        sNames = oPar.getCellNames()
        bEmptyTableFlag=True
        for val in sNames:
            oCell = oPar.getCellByName(val)
            oTCurs = oCell.createTextCursor()
            oCurEnum = oTCurs.createEnumeration()
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

RepeatIn()


"""

            vOpenSearch = doc.createSearchDescriptor()

            vCloseSearch = doc.createSearchDescriptor()

            # Set the text for which to search and other
            vOpenSearch.SearchString = "repeatIn"

            vCloseSearch.SearchString = "')"

            # Find the first open delimiter
            vOpenFound = doc.findFirst(vOpenSearch)

            while not vOpenFound==None:

                #Search for the closing delimiter starting from the open delimiter
                vCloseFound = doc.findNext( vOpenFound.End, vCloseSearch)

                if vCloseFound==None:
                    print "Found an opening bracket but no closing bracket!"

                    break

                else:

                    vOpenFound.gotoRange(vCloseFound, True)

                    self.count += 1

                    vOpenFound = doc.findNext( vOpenFound.End, vOpenSearch)
                #End If
            #End while Loop
"""
