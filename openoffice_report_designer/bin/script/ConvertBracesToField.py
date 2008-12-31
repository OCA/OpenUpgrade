
import uno
import unohelper
import string
import re
import base64

from com.sun.star.task import XJobExecutor
if __name__<>"package":
    from lib.gui import *
    from LoginTest import *
    database="test"
    uid = 3


class ConvertBracesToField( unohelper.Base, XJobExecutor ):

    def __init__(self,ctx):

        self.ctx     = ctx
        self.module  = "openerp_report"
        self.version = "0.1"
        LoginTest()

        if not loginstatus and __name__=="package":
            exit(1)

        global passwd
        self.password = passwd

        self.aReportSyntex=[]
        self.getBraces(self.aReportSyntex)

        self.setValue()


    def setValue(self):

        desktop=getDesktop()
        doc = desktop.getCurrentComponent()
        docinfo=  doc.getDocumentInfo()
        count = 0
        regexes = [
            ['[a-zA-Z0-9_]+\.[a-zA-Z0-9_.]+',"Field"],
            ['\\[\\[ *repeatIn\\( *([a-zA-Z0-9_\.]+), *\'([a-zA-Z0-9_]+)\' *\\) *\\]\\]', "RepeatIn"],
            ['\\[\\[ *([a-zA-Z0-9_\.]+) *\\]\\]', "Field"]
            # ['\\[\\[ ([a-zA-Z0-9_]+\.[a-zA-Z1-9]) \\]\\]',"Field"],
            # ['\\[\\[ [a-zA-Z0-9_\.]+ and ([a-zA-Z0-9_\.]+) or .+? \\]\\]',"Field"],
            # ['\\[\\[ ([a-zA-Z0-9_\.]+) or .+? \\]\\]',"Field"],
            # ['\\[\\[ ([a-zA-Z0-9_\.]+) and .+? \\]\\]',"Field"],
            # ['\\[\\[ .+? or ([a-zA-Z0-9_\.]+) \\]\\]',"Field"],
            # ['\\[\\[ (.+?) and ([a-zA-Z0-9_\.]+) \\]\\]',"Field"],
            # ['\\[\\[ .+? % ([a-zA-Z0-9_\.]+) \\]\\]',"Field"]
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
        print "============",oRepeatInObjects
        for ro in oRepeatInObjects:
            if ro.find("(")<>-1:
                saRepeatInList.append( [ ro[:ro.find("(")], ro[ro.find("(")+1:ro.find(")")] ])
        try:
            oParEnum = doc.getTextFields().createEnumeration()
            while oParEnum.hasMoreElements():
                oPar = oParEnum.nextElement()
                if oPar.supportsService("com.sun.star.text.TextField.DropDown"):
                    for reg in regexes:
                        res=re.findall(reg[0],oPar.Items[1].replace(' ',""))
                        if len(res) <> 0:
                            if res[0][0] == "objects":
                                sTemp = docinfo.getUserFieldValue(3)
                                sTemp = "|-." + sTemp[sTemp.rfind(".")+1:] + ".-|"
                                oPar.Items=(sTemp.encode("utf-8"),oPar.Items[1].replace(' ',""))
                                oPar.update()
                            elif type(res[0]) <> type(u''):
                                sock = xmlrpclib.ServerProxy(docinfo.getUserFieldValue(0) + '/xmlrpc/object')
                                sObject = self.getRes(sock, docinfo.getUserFieldValue(3), res[0][0][res[0][0].find(".")+1:].replace(".","/"))
                                r = sock.execute(database, uid, self.password, docinfo.getUserFieldValue(3) , 'fields_get')
                                sExpr="|-." + r[res[0][0][res[0][0].rfind(".")+1:]]["string"] + ".-|"
                                oPar.Items=(sExpr.encode("utf-8"),oPar.Items[1].replace(' ',""))
                                oPar.update()
                            else:
                                sock = xmlrpclib.ServerProxy(docinfo.getUserFieldValue(0) + '/xmlrpc/object')
                                obj = None
                                for rl in saRepeatInList:
                                    if rl[0] == res[0][:res[0].find(".")]:
                                        obj=rl[1]
                                try:
                                    sObject = self.getRes(sock, obj, res[0][res[0].find(".")+1:].replace(".","/"))
                                    r = sock.execute(database, uid, self.password, sObject , 'read',[1])
                                except:
                                    r = "TTT"
                                if len(r) <> 0:
                                    if r <> "TTT":
                                        if len(res)>1:
                                            sExpr=""
                                            print res
                                            if reg[1] == 'Field':
                                                for ires in res:
                                                    try:
                                                        sExpr=r[0][ires[ires.rfind(".")+1:]]
                                                        break
                                                    except:
                                                        pass
                                                try:
                                                    oPar.Items=(sExpr.encode("utf-8") ,oPar.Items[1])
                                                    oPar.update()
                                                except Exception, e:
                                                    oPar.Items=(str(sExpr) ,oPar.Items[1])
                                                    oPar.update()
                                        else:
                                            try:
                                                sExpr=r[0][res[0][res[0].rfind(".")+1:]]
                                                if sExpr:
                                                    oPar.Items=(sExpr.encode("utf-8") ,oPar.Items[1])
                                                    oPar.update()
                                                else:
                                                     oPar.Items=(u"/",oPar.Items[1])
                                                     oPar.update()
                                            except Exception, e:
                                                oPar.Items=(str(sExpr) ,oPar.Items[1])
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
        res = sock.execute(database, uid, self.password, sObject , 'fields_get')
        key = res.keys()
        key.sort()
        myval=None
        if not sVar.find("/")==-1:
            myval=sVar[:sVar.find("/")]
        else:
            myval=sVar
        for k in key:
            if (res[k]['type'] in ['many2one']) and k==myval:
                sObject = self.getRes(sock,res[myval]['relation'], sVar[sVar.find("/")+1:])
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
                ['\\[\\[ *.+? *\\]\\]', "Expression"]
            ]

            search = doc.createSearchDescriptor()
            search.SearchRegularExpression = True

            for reg in regexes:
                search.SearchString = reg[0]
                found = doc.findFirst( search )
                while found:
                    res=re.findall(reg[0],found.String)
                    print len(res)

                    if found.String not in [r[0] for r in aReportSyntex] and len(res) == 1 :
                        text=found.getText()
                        oInputList = doc.createInstance("com.sun.star.text.TextField.DropDown")
                        if reg[1]<>"Expression":
                            oInputList.Items=(u""+found.String,u""+found.String)
                        else:
                            oInputList.Items=(u"?",u""+found.String)
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
                            oInputList.Items=(u"?",u""+found.String)
                        aReportSyntex.append([oInputList,res[1]])
                        text.insertTextContent(found,oInputList,False)
                        found.String =""
                        found = doc.findNext(found.End, search)
        except:
            import traceback;
            traceback.print_exc()

if __name__<>"package":
    ConvertBracesToField(None)
else:
    g_ImplementationHelper.addImplementation( ConvertBracesToField, "org.openoffice.openerp.report.convertBF", ("com.sun.star.task.Job",),)

