

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

#        for r in self.aReportSyntex:
#            if r[1]=="RepeatIn":
#                res1=re.findall("\\( *(.+),", r[0].Items[1])
#                res2=re.findall("\'([a-zA-Z0-9_]+)\'",r[0].Items[1])
#                if res1[0]=="objects":
#                    print res1,res2

    def getBraces(self,aReportSyntex=[]):

        desktop=getDesktop()
        doc = desktop.getCurrentComponent()
        aSearchString=[]
        aReplaceString=[]
        aRes=[]

        try:
            regexes = [
                ['\\[\\[ *repeatIn\\( *(.+), *\'([a-zA-Z0-9_]+)\' *\\) *\\]\\]', "RepeatIn"],
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
                        print "aaa",reg[1]
                        oInputList = doc.createInstance("com.sun.star.text.TextField.DropDown")
                        oInputList.Items=(u""+found.String,u""+found.String)
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
                        oInputList.Items=(u""+found.String,u""+found.String)
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

