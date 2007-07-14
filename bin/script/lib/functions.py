import uno
import xmlrpclib
if __name__<>"package":
    from gui import *

def genTree(object,aList,insField,host,level=3, ending=[], ending_excl=[], recur=[], root='', actualroot=""):
    try:
        sock = xmlrpclib.ServerProxy(host+'/xmlrpc/object')
        res = sock.execute('terp', 3, 'admin', object , 'fields_get')
        key = res.keys()
        key.sort()
        for k in key:
            if (not ending or res[k]['type'] in ending) and ((not ending_excl) or not (res[k]['type'] in ending_excl)):
                insField.addItem(root+'/'+res[k]["string"],aList.__len__())#getListBoxItemCount("lstFields"))
                aList.append(actualroot+'/'+k)
            if (res[k]['type'] in recur) and (level>0):
                genTree(res[k]['relation'],aList,insField,host ,level-1, ending, ending_excl, recur,root+'/'+res[k]["string"],actualroot+'/'+k)
    except:
        import traceback;traceback.print_exc()

def VariableScope(oTcur,insVariable,aObjectList,aComponentAdd,aItemList,sTableName=""):
    if sTableName.find(".") != -1:
        for i in range(aItemList.__len__()):
            if aComponentAdd[i]==sTableName:
                sLVal=aItemList[i].__getitem__(1).__getslice__(aItemList[i].__getitem__(1).find(",'")+2,aItemList[i].__getitem__(1).find("')"))
                for j in range(aObjectList.__len__()):
                    if aObjectList[j].__getslice__(0,aObjectList[j].find("(")) == sLVal:
                        insVariable.addItem(aObjectList[j],1)
        VariableScope(oTcur,insVariable,aObjectList,aComponentAdd,aItemList, sTableName.__getslice__(0,sTableName.rfind(".")))
    else:
        for i in range(aItemList.__len__()):
            if aComponentAdd[i]==sTableName:
                sLVal=aItemList[i].__getitem__(1).__getslice__(aItemList[i].__getitem__(1).find(",'")+2,aItemList[i].__getitem__(1).find("')"))
                for j in range(aObjectList.__len__()):
                    if aObjectList[j].__getslice__(0,aObjectList[j].find("(")) == sLVal and sLVal!="":
                        insVariable.addItem(aObjectList[j],1)

def getList(aObjectList,host,count):
    desktop=getDesktop()
    doc =desktop.getCurrentComponent()
    docinfo=doc.getDocumentInfo()
    sMain=""
    if not count == 0:
        if count >= 1:
            oParEnum = doc.getTextFields().createEnumeration()
            while oParEnum.hasMoreElements():
                oPar = oParEnum.nextElement()
                if oPar.supportsService("com.sun.star.text.TextField.DropDown"):
                    sItem=oPar.Items.__getitem__(1)
                    if sItem.__getslice__(sItem.find("(")+1,sItem.find(","))=="objects":
                        sMain = sItem.__getslice__(sItem.find(",'")+2,sItem.find("')"))
            oParEnum = doc.getTextFields().createEnumeration()
            aObjectList.append("List of " + docinfo.getUserFieldValue(3))
            while oParEnum.hasMoreElements():
                oPar = oParEnum.nextElement()
                if oPar.supportsService("com.sun.star.text.TextField.DropDown"):
                    sItem=oPar.Items.__getitem__(1)
                    if sItem.__getslice__(sItem.find("[[ ")+3,sItem.find("("))=="repeatIn":
                        if sItem.__getslice__(sItem.find("(")+1,sItem.find(","))=="objects":
                            aObjectList.append(sItem.__getslice__(sItem.rfind(",'")+2,sItem.rfind("')")) + "(" + docinfo.getUserFieldValue(3) + ")")
                        else:
                            sTemp=sItem.__getslice__(sItem.find("(")+1,sItem.find(","))
                            if sMain == sTemp.__getslice__(0,sTemp.find(".")):
                                getRelation(docinfo.getUserFieldValue(3), sItem.__getslice__(sItem.find(".")+1,sItem.find(",")), sItem.__getslice__(sItem.find(",'")+2,sItem.find("')")),aObjectList,host)
                            else:
                                sPath=getPath(sItem.__getslice__(sItem.find("(")+1,sItem.find(",")), sMain)
                                getRelation(docinfo.getUserFieldValue(3), sPath.__getslice__(sPath.find(".")+1,sPath.__len__()), sItem.__getslice__(sItem.find(",'")+2,sItem.find("')")),aObjectList,host)
    else:
        aObjectList.append("List of " + docinfo.getUserFieldValue(3))

def getRelation(sRelName, sItem, sObjName, aObjectList, host ):
        sock = xmlrpclib.ServerProxy(host+'/xmlrpc/object')
        res = sock.execute('terp', 3, 'admin', sRelName , 'fields_get')
        key = res.keys()
        for k in key:
            if sItem.find(".") == -1:
                if k == sItem:
                    aObjectList.append(sObjName + "(" + res[k]['relation'] + ")")
                    return 0
            if k == sItem.__getslice__(0,sItem.find(".")):
                getRelation(res[k]['relation'], sItem.__getslice__(sItem.find(".")+1,sItem.__len__()), sObjName,aObjectList,host)


def getPath(sPath,sMain):
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
                    getPath(sPath, sMain)
    return sPath


def EnumDocument(aItemList,aComponentAdd):
    desktop = getDesktop()
    Doc =desktop.getCurrentComponent()
    #oVC = Doc.CurrentController.getViewCursor()
    oParEnum = Doc.getText().createEnumeration()
    while oParEnum.hasMoreElements():
        oPar = oParEnum.nextElement()
        if oPar.supportsService("com.sun.star.text.TextTable"):
            getChildTable(oPar,aItemList,aComponentAdd)
        if oPar.supportsService("com.sun.star.text.Paragraph"):
            oSecEnum = oPar.createEnumeration()
            while oSecEnum.hasMoreElements():
                oSubSection = oSecEnum.nextElement()
                if oSubSection.TextSection:
                    if oSubSection.TextField:
                        aItemList.append( oSubSection.TextField.Items )
                        aComponentAdd.append(oSubSection.TextSection.Name)
                elif oPar.getAnchor().TextField:
                    sItem=oPar.getAnchor().TextField.Items.__getitem__(1)
                    if sItem.__getslice__(sItem.find("[[ ")+3,sItem.find("("))=="repeatIn":
                        aItemList.append(oSubSection.TextField.Items )
                        aComponentAdd.append("Document")

def getChildTable(oPar,aItemList,aComponentAdd,sTableName=""):
    sNames = oPar.getCellNames()
    bEmptyTableFlag=True
    for val in sNames:
        oCell = oPar.getCellByName(val)
        oCurEnum = oCell.createEnumeration()
        while oCurEnum.hasMoreElements():
            try:
                oCur = oCurEnum.nextElement()

                if oCur.supportsService("com.sun.star.text.TextTable"):
                    if sTableName=="":
                        getChildTable(oCur,aItemList,aComponentAdd,oPar.Name)
                    else:
                        getChildTable(oCur,aItemList,aComponentAdd,sTableName+"."+oPar.Name)
                else:
                    oSecEnum = oCur.createEnumeration()
                    while oSecEnum.hasMoreElements():
                        oSubSection = oSecEnum.nextElement()
                        if oSubSection.supportsService("com.sun.star.text.TextField"):
                            bEmptyTableFlag=False
                            sItem=oSubSection.TextField.Items.__getitem__(1)
                            if sItem.__getslice__(sItem.find("[[ ")+3,sItem.find("("))=="repeatIn":
                                if aItemList.__contains__(oSubSection.TextField.Items)==False:
                                    aItemList.append(oSubSection.TextField.Items)
                                if sTableName=="":
                                    if  aComponentAdd.__contains__(oPar.Name)==False:
                                        aComponentAdd.append(oPar.Name)
                                else:
                                    if aComponentAdd.__contains__(sTableName+"."+oPar.Name)==False:
                                        aComponentAdd.append(sTableName+"."+oPar.Name)

            except:
                import traceback;traceback.print_exc()
    if bEmptyTableFlag==True:
        aItemList.append((u'',u''))
        if sTableName=="":
            if  aComponentAdd.__contains__(oPar.Name)==False:
                aComponentAdd.append(oPar.Name)
        else:
            if aComponentAdd.__contains__(sTableName+"."+oPar.Name)==False:
                aComponentAdd.append(sTableName+"."+oPar.Name)
    return 0

def getRecersiveSection(oCurrentSection,aSectionList):
        desktop=getDesktop()
        doc =desktop.getCurrentComponent()
        oParEnum=doc.getText().createEnumeration()
        aSectionList.append(oCurrentSection.Name)
        if oCurrentSection.ParentSection:
            getRecersiveSection(oCurrentSection.ParentSection,aSectionList)
        else:
            return
