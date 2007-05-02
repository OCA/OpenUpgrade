import uno
import string
import unohelper
from com.sun.star.task import XJobExecutor
from lib.gui import *
import xmlrpclib

class Repeatln:
    def __init__(self):

        self.win = DBModalDialog(60, 50, 140, 250, "Field Builder")

        self.win.addFixedText("lblVariable", 18, 12, 30, 15, "Variable :")

        self.win.addComboBox("cmbVariable", 45, 10, 90, 15,True,
                             itemListenerProc=self.cmbVariable_selected)

        self.win.addFixedText("lblName", 5, 32, 40, 15, "Object Name :")

        self.win.addEdit("txtName", 45, 30, 90, 15,)

        self.insVariable = self.win.getControl( "cmbVariable" )

        self.win.addFixedText("lblFields", 25, 52, 25, 15, "Fields :")

        self.win.addComboListBox("lstFields", 45, 50, 90, 150, False)

        self.insField = self.win.getControl( "lstFields" )

        sock = xmlrpclib.ServerProxy('http://localhost:8069/xmlrpc/object')

        #self.getModule(sock)

        self.win.addButton('btnOK',-5 ,-25,45,15,'Ok'
                      ,actionListenerProc = self.btnOkOrCancel_clicked )

        self.win.addButton('btnCancel',-5 - 45 - 5 ,-25,45,15,'Cancel'
                      ,actionListenerProc = self.btnOkOrCancel_clicked )

        self.sObj=None

        self.aItemList=[]

        self.aComponentAdd=[]

        self.aObjectList=[]

        self.EnumDocument()

        desktop=getDesktop()

        doc =desktop.getCurrentComponent()

        #oParEnum = doc.getTextFields().createEnumeration()

        #for i in range(self.aComponentAdd.__len__()):
        #    print self.aComponentAdd[i]
        # Get the object of current document


        docinfo=doc.getDocumentInfo()
        # find out how many objects are created in document
        if not docinfo.getUserFieldValue(3) == "":

            self.count=0

            oParEnum = doc.getTextFields().createEnumeration()

            while oParEnum.hasMoreElements():

                oPar = oParEnum.nextElement()

                if oPar.supportsService("com.sun.star.text.TextField.DropDown"):

                    self.count += 1

            self.getList()
            cursor = doc.getCurrentController().getViewCursor()
            #for i in range(self.aObjectList.__len__()):
            text=cursor.getText()
            tcur=text.createTextCursorByRange(cursor)
            for j in range(self.aObjectList.__len__()):
                if self.aObjectList[j].__getslice__(0,self.aObjectList[j].find("(")) == "Objects":
                    self.insVariable.addItem(self.aObjectList[j],1)

            if not tcur.TextTable:
                for i in range(self.aItemList.__len__()):
                    print self.aComponentAdd[i]
                    if self.aComponentAdd[i]=="Document":

                        sLVal=self.aItemList[i].__getitem__(1).__getslice__(self.aItemList[i].__getitem__(1).find(",'")+2,self.aItemList[i].__getitem__(1).find("')"))
                        print sLVal + "--" + self.aItemList[i].__getitem__(1)
                        for j in range(self.aObjectList.__len__()):
                            print self.aObjectList[j].__getslice__(0,self.aObjectList[j].find("("))
                            if self.aObjectList[j].__getslice__(0,self.aObjectList[j].find("(")) == sLVal:

                                self.insVariable.addItem(self.aObjectList[j],1)

            else:
                print "Still Under Construction"



            self.win.doModalDialog()

        else:

            print "Insert Field-4"

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

            sock = xmlrpclib.ServerProxy('http://localhost:8069/xmlrpc/object')

            desktop=getDesktop()

            doc =desktop.getCurrentComponent()

            docinfo=doc.getDocumentInfo()

            self.win.removeListBoxItems("lstFields", 0, self.win.getListBoxItemCount("lstFields"))

            sItem=self.win.getComboBoxSelectedText("cmbVariable")

            self.genTree(sItem.__getslice__(sItem.find("(")+1,sItem.find(")")),1,ending=['one2many','many2many'], recur=['one2many','many2many'])
        else:

            self.insField.addItem("objects",self.win.getListBoxItemCount("lstFields"))

        #self.genTree(self.win.getComboBoxSelectedText("cmbVariable"),2, , recur=['many2one'])  ending_excl=['many2one'],

    def btnOkOrCancel_clicked( self, oActionEvent ):
        #Called when the OK or Cancel button is clicked.

        if oActionEvent.Source.getModel().Name == "btnOK":

            self.bOkay = True

            desktop=getDesktop()

            doc = desktop.getCurrentComponent()

            text = doc.Text

            cursor = doc.getCurrentController().getViewCursor()


            if self.win.getListBoxSelectedItem("lstFields") != "" and self.win.getEditText("txtName") != "" :

                    sObjName=""
                    #objField = doc.createInstance("com.sun.star.text.TextField.HiddenText")
                    oInputList = doc.createInstance("com.sun.star.text.TextField.DropDown")

                    if self.win.getListBoxSelectedItem("lstFields") == "objects":

                        sKey=u""+self.win.getListBoxSelectedItem("lstFields")

                        sValue=u"[[ repeatIn(" + self.win.getListBoxSelectedItem("lstFields") + ",'" + self.win.getEditText("txtName") + "') ]]"

                        oInputList.Items = (sKey,sValue)

                        text.insertTextContent(cursor,oInputList,False)

                    else:
                        sObjName=self.win.getComboBoxSelectedText("cmbVariable")

                        sObjName=sObjName.__getslice__(0,sObjName.find("("))

                        if cursor.TextTable==None:

                            sKey=self.win.getListBoxSelectedItem("lstFields").replace("/",".")

                            sKey=u""+sKey.__getslice__(1,sKey.__len__())

                            sValue=u"[[ repeatIn(" + sObjName + self.win.getListBoxSelectedItem("lstFields").replace("/",".") + ",'" + self.win.getEditText("txtName") +"') ]]"

                            oInputList.Items = (sKey,sValue)

                            text.insertTextContent(cursor,oInputList,False)
                        else:

                            oTable = cursor.TextTable

                            oCurCell = cursor.Cell

                            tableText = oTable.getCellByName( oCurCell.CellName )

                            cursor = tableText.createTextCursor()

                            cursor.gotoEndOfParagraph(True)

                            sKey=self.win.getListBoxSelectedItem("lstFields").replace("/",".")

                            sKey=u""+sKey.__getslice__(1,sKey.__len__())

                            sValue=u"[[ repeatIn(" + sObjName + self.win.getListBoxSelectedItem("lstFields").replace("/",".") + ",'" + self.win.getEditText("txtName") +"') ]]"

                            oInputList.Items = (sKey,sValue)

                            tableText.insertTextContent(cursor,oInputList,False)

        elif oActionEvent.Source.getModel().Name == "btnCancel":

            self.win.endExecute()

    # this method will featch data from the database and place it in the combobox
    def genTree(self,object,level=3, ending=[], ending_excl=[], recur=[], root=''):

        sock = xmlrpclib.ServerProxy('http://localhost:8069/xmlrpc/object')

        res = sock.execute('terp', 3, 'admin', object , 'fields_get')

        key = res.keys()

        key.sort()

        for k in key:

            if (not ending or res[k]['type'] in ending) and ((not ending_excl) or not (res[k]['type'] in ending_excl)):

                self.insField.addItem(root+'/'+k,self.win.getListBoxItemCount("lstFields"))

            #if (res[k]['type'] in recur):
                #self.insField.addItem(root+'/'+k,self.win.getListBoxItemCount("lstFields"))

            if (res[k]['type'] in recur) and (level>0):

                self.genTree(res[k]['relation'], level-1, ending, ending_excl, recur, root+'/'+k)

    def getList(self):
        #Perform checking that which object is to show in listbox
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
                #self.insVariable.addItem("Objects(" + docinfo.getUserFieldValue(3) + ")",1)

                while oParEnum.hasMoreElements():

                    oPar = oParEnum.nextElement()

                    if oPar.supportsService("com.sun.star.text.TextField.DropDown"):

                        sItem=oPar.Items.__getitem__(1)

                        if sItem.__getslice__(sItem.find("(")+1,sItem.find(","))=="objects":
                        #   print oMain
                            self.aObjectList.append(sItem.__getslice__(sItem.rfind(",'")+2,sItem.rfind("')")) + "(" + docinfo.getUserFieldValue(3) + ")")
                            #self.insVariable.addItem(sItem.__getslice__(sItem.rfind(",'")+2,sItem.rfind("')")) + "(" + docinfo.getUserFieldValue(3) + ")",1)

                        else:

                            sTemp=sItem.__getslice__(sItem.find("(")+1,sItem.find(","))

                            if sMain == sTemp.__getslice__(0,sTemp.find(".")):

                                self.getRelation(docinfo.getUserFieldValue(3), sItem.__getslice__(sItem.find(".")+1,sItem.find(",")), sItem.__getslice__(sItem.find(",'")+2,sItem.find("')")))

                            else:

                                sPath=self.getPath(sItem.__getslice__(sItem.find("(")+1,sItem.find(",")), sMain)

                                self.getRelation(docinfo.getUserFieldValue(3), sPath.__getslice__(sPath.find(".")+1,sPath.__len__()), sItem.__getslice__(sItem.find(",'")+2,sItem.find("')")))

        else:
            self.aObjectList.append("Objects(" + docinfo.getUserFieldValue(3) + ")")
            #self.insVariable.addItem("Objects(" + docinfo.getUserFieldValue(3) + ")",1)

    def getPath(self,sPath,sMain):

        desktop=getDesktop()

        doc =desktop.getCurrentComponent()

        oParEnum = doc.getTextFields().createEnumeration()

        while oParEnum.hasMoreElements():

            oPar = oParEnum.nextElement()

            if oPar.supportsService("com.sun.star.text.TextField.DropDown"):

                sItem=oPar.Items.__getitem__(1)

                if sPath.__getslice__(0,sPath.find(".")) == sMain:

                    return sPath

                else:

                    if sItem.__getslice__(sItem.find(",'")+2,sItem.find("')")) == sPath.__getslice__(0,sPath.find(".")):

                        sPath =  sItem.__getslice__(sItem.find("(")+1,sItem.find(",")) + sPath.__getslice__(sPath.find("."),sPath.__len__())

                        self.getPath(sPath, sMain)

    def getRelation(self, sRelName, sItem, sObjName ):

        sock = xmlrpclib.ServerProxy('http://localhost:8069/xmlrpc/object')

        res = sock.execute('terp', 3, 'admin', sRelName , 'fields_get')

        key = res.keys()

        for k in key:

            if sItem.find(".") == -1:

                if k == sItem:

                    self.aObjectList.append(sObjName + "(" + res[k]['relation'] + ")")
                    #self.insVariable.addItem(sObjName + "(" + res[k]['relation'] + ")",1)

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


    def getChildTable(self,oPar,sTableName=""):
        sNames = oPar.getCellNames()

        for val in sNames:

            oCell = oPar.getCellByName(val)

            oTCurs = oCell.createTextCursor()

            oCurEnum = oTCurs.createEnumeration()

            while oCurEnum.hasMoreElements():

                oCur = oCurEnum.nextElement()

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

                            if self.aItemList.__contains__(oSubSection.TextField.Items)==False:

                                self.aItemList.append(oSubSection.TextField.Items)

                            if sTableName=="":

                                if  self.aComponentAdd.__contains__(oPar.Name)==False:

                                    self.aComponentAdd.append(oPar.Name)

                            else:

                                if self.aComponentAdd.__contains__(sTableName+"."+oPar.Name)==False:

                                    self.aComponentAdd.append(sTableName+"."+oPar.Name)

        return 0

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

                if oPar.supportsService("com.sun.star.text.TextContent"):

                    oContentEnum = oPar.createContentEnumeration("com.sun.star.text.TextContent")

                    if oPar.getAnchor().TextField:

                        self.aItemList.append( oPar.getAnchor().TextField.Items )

                        self.aComponentAdd.append("Document")

        #i=0
        #print aItemList.__len__()
        #print aComponentAdd.__len__()

        #for i in range(aItemList.__len__()):
            #print aItemList[i]
        #for i in range(aComponentAdd.__len__()):
            #print self.aComponentAdd[i]


Repeatln()


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
