

import uno
import unohelper
import string
import re
from com.sun.star.task import XJobExecutor
if __name__<>"package":

    from lib.gui import *
    from LoginTest import *
    database="trunk_1"

class ConvertBracesToField( unohelper.Base, XJobExecutor ):

    def __init__(self,ctx):

        self.ctx     = ctx
        self.module  = "tiny_report"
        self.version = "0.1"
        LoginTest()

        if not loginstatus and __name__=="package":
            exit(1)

        self.aReportSyntex=[]
        self.getBraces(self.aReportSyntex)

        self.setValue()

    def setValue(self):
        desktop=getDesktop()
        doc = desktop.getCurrentComponent()
        docinfo=  doc.getDocumentInfo()
        count = 0
        regexes = [
                  ['\\[\\[ *repeatIn\\( *([a-zA-Z0-9_\.]+), *\'([a-zA-Z0-9_]+)\' *\\) *\\]\\]', "RepeatIn"],
                  ['\\[\\[ *([a-zA-Z0-9_\.]+) *\\]\\]', "Field"]
                  ]
        oFieldObject = []
        oRepeatInObjects = []
        saRepeatInList = []
        sHost = docinfo.getUserFieldValue(0)
        nCount = 0
        oParEnum = doc.getTextFields().createEnumeration()
        while oParEnum.hasMoreElements():
            oPar = oParEnum.nextElement()
            nCount += 1
        getList(oRepeatInObjects,sHost,nCount)
        print oRepeatInObjects
        for ro in oRepeatInObjects:
            if ro.find("(")<>-1:
                saRepeatInList.append([ro.__getslice__(0,ro.find("(")),ro.__getslice__(ro.find("(")+1,ro.find(")"))])
        print saRepeatInList
        try:
            oParEnum = doc.getTextFields().createEnumeration()
            while oParEnum.hasMoreElements():
                oPar = oParEnum.nextElement()
                if oPar.supportsService("com.sun.star.text.TextField.DropDown"):
                    for reg in regexes:
                        res=re.findall(reg[0],oPar.Items[1])
                        if len(res) <> 0:
                            if res[0][0] == "objects":
                                sTemp = docinfo.getUserFieldValue(3)
                                sTemp = u"|-." + sTemp.__getslice__(sTemp.rfind(".")+1,len(sTemp)) + ".-|"
                                oPar.Items=(sTemp,oPar.Items[1])
                                oPar.update()
                            elif type(res[0]) <> type(u''):
                                sock = xmlrpclib.ServerProxy(docinfo.getUserFieldValue(0) + '/xmlrpc/object')
                                sObject = self.getRes(sock, docinfo.getUserFieldValue(3), res[0][0].__getslice__(res[0][0].find(".")+1,len(res[0][0])).replace(".","/"))
                                r = sock.execute(database, 3, docinfo.getUserFieldValue(1), docinfo.getUserFieldValue(3) , 'fields_get')
                                oPar.Items=(u"|-." + r[res[0][0].__getslice__(res[0][0].rfind(".")+1 ,len(res[0][0]))]["string"] + ".-|",oPar.Items[1])
                                oPar.update()
                            else:
                                sock = xmlrpclib.ServerProxy(docinfo.getUserFieldValue(0) + '/xmlrpc/object')
                                obj = None
                                for rl in saRepeatInList:
                                    if rl[0] == res[0].__getslice__(0,res[0].find(".")):
                                        obj=rl[1]
                                try:
                                    sObject = self.getRes(sock, obj, res[0].__getslice__(res[0].find(".")+1,len(res[0])).replace(".","/"))
                                    r = sock.execute(database, 3, docinfo.getUserFieldValue(1), sObject , 'read',[1])
                                except:
                                    r = "TTT"

                                if len(r) <> 0:
                                    if r <> "TTT":
                                        oPar.Items=(u"" + str(r[0][res[0].__getslice__(res[0].rfind(".")+1,len(res[0]))]) ,oPar.Items[1])
                                        oPar.update()
                                    else:
                                        oPar.Items=(u""+r,oPar.Items[1])
                                        oPar.update()
                                else:
                                    oPar.Items=(u"TTT",oPar.Items[1])
                                    oPar.update()
        except:
            import traceback;traceback.print_exc()

    def getRes(self,sock,sObject,sVar):
        desktop=getDesktop()
        doc =desktop.getCurrentComponent()
        docinfo=doc.getDocumentInfo()
        res = sock.execute(database, 3, docinfo.getUserFieldValue(1), sObject , 'fields_get')
        key = res.keys()
        key.sort()
        myval=None
        if not sVar.find("/")==-1:
            myval=sVar.__getslice__(0,sVar.find("/"))
        else:
            myval=sVar
        for k in key:
            if (res[k]['type'] in ['many2one']) and k==myval:

                self.getRes(sock,res[myval]['relation'], sVar.__getslice__(sVar.find("/")+1,sVar.__len__()))
                return res[myval]['relation']
            elif k==myval:
                return sObject
    def getBraces(self,aReportSyntex=[]):

        desktop=getDesktop()
        doc = desktop.getCurrentComponent()
        aSearchString=[]
        aReplaceString=[]
        aRes=[]

        try:
            regexes = [
                ['\\[\\[ *repeatIn\\( *([a-zA-Z0-9_\.]+), *\'([a-zA-Z0-9_]+)\' *\\) *\\]\\]', "RepeatIn"],
                ['\\[\\[ *([a-zA-Z0-9_\.]+) *\\]\\]', "Field"],
                ['\\[\\[ *.+? \\]\\]', "Expression"]
                ]

            #regexes = [['\[\[ repeatIn\( (.+), \'([a-zA-Z0-9_]+)\' \) \]\]','RepeatIn'],['\[\[([a-zA-Z0-9_\.]+)\]\]','Field'],['\[\[.+?\]\]','Expression']]

            search = doc.createSearchDescriptor()
            search.SearchRegularExpression = True

            for reg in regexes:
                search.SearchString = reg[0]
                found = doc.findFirst( search )

                while found:
                    res=re.findall(reg[0],found.String)

                    if found.String not in [r[0] for r in aReportSyntex] and len(res) == 1:

                        text=found.getText()
                        oInputList = doc.createInstance("com.sun.star.text.TextField.DropDown")
                        if reg[1]<>"Expression":
                            oInputList.Items=(u""+found.String,u""+found.String)
                        else:
                            oInputList.Items=(u"???????",u""+found.String)
                        aReportSyntex.append([oInputList,reg[1]])
                        text.insertTextContent(found,oInputList,False)
                        found.String =""

                    else:
                        aRes.append([res,reg[1]])
                        found = doc.findNext(found.End, search)

            search = doc.createSearchDescriptor()
            search.SearchRegularExpression = False

            for res in aRes:

                for r in res[0]:
                    search.SearchString=r
                    found=doc.findFirst(search)

                    while found:

                        text=found.getText()

                        oInputList = doc.createInstance("com.sun.star.text.TextField.DropDown")
                        if res[1]<>"Expression":
                            oInputList.Items=(u""+found.String,u""+found.String)
                        else:
                            oInputList.Items=(u"???????",u""+found.String)
                        aReportSyntex.append([oInputList,res[1]])
                        text.insertTextContent(found,oInputList,False)
                        found.String =""
                        found = doc.findNext(found.End, search)
        except:
            pass



if __name__<>"package":

    ConvertBracesToField(None)
else:

    g_ImplementationHelper.addImplementation( \
        ConvertBracesToField,
        "org.openoffice.tiny.report.convertBF",
        ("com.sun.star.task.Job",),)

