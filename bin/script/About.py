

import uno
#import string
#import unohelper
#import xmlrpclib
#import base64, tempfile
from com.sun.star.task import XJobExecutor
#import os
#import sys
if __name__<>'package':
    from lib.gui import *
#    from lib.error import *
#    from LoginTest import *
#    from lib.functions import *

class About(unohelper.Base, XJobExecutor):
    def __init__(self,ctx):
        self.ctx     = ctx
        self.module  = "tiny_report"
        self.version = "0.1"
        self.win = DBModalDialog(60, 50, 175, 115, ".:: About Us !!! ::.")


        fdBigFont = createUnoStruct("com.sun.star.awt.FontDescriptor")
        fdBigFont.Width = 20
        fdBigFont.Height = 25
        fdBigFont.Weight = 120
        fdBigFont.Family= 3

        self.win.addFixedText("lblTitle1", 1, 1, 30, 30)
        oLabelTitle1 = self.win.getControl("lblTitle1")
        oLabelTitle1.Model.TextColor = 16056320
        oLabelTitle1.Model.FontDescriptor = fdBigFont
        oLabelTitle1.Model.FontRelief = 1
        oLabelTitle1.Text = "Tiny"

        self.win.addFixedText("lblTitle2", 31, 1, 30, 30)
        oLabelTitle2 = self.win.getControl("lblTitle2")
        oLabelTitle2.Model.TextColor = 1
        oLabelTitle2.Model.FontDescriptor = fdBigFont
        oLabelTitle2.Model.FontRelief = 1
        oLabelTitle2.Text = "ERP"

        self.win.addFixedText("lblProdDesc", 1, 30, 173, 75)
        oLabelProdDesc = self.win.getControl("lblProdDesc")
        oLabelProdDesc.Model.TextColor = 1
        fdBigFont.Width = 10
        fdBigFont.Height = 11
        fdBigFont.Weight = 76
        oLabelProdDesc.Model.FontDescriptor = fdBigFont
        oLabelProdDesc.Model.Align = 1
        oLabelProdDesc.Model.FontRelief = 1
        oLabelProdDesc.Model.MultiLine = True
        sMessage = "This  package  helps  you  to  create  or  modify\nreports  in  Tiny  ERP.  Once  connected  to  the\nserver, you can design your template of reports\nusing fields  and expressions  and  browsing the\ncomplete structure of Tiny ERP object database."
        oLabelProdDesc.Text = sMessage

        self.win.addFixedText("lblFooter", -1, -1, 173, 25)
        oLabelFooter = self.win.getControl("lblFooter")
        oLabelFooter.Model.TextColor = 255
        #oLabelFooter.Model.BackgroundColor = 1
        oLabelFooter.Model.Border = 2
        oLabelFooter.Model.BorderColor = 255
        fdBigFont.Width = 8
        fdBigFont.Height = 9
        fdBigFont.Weight = 100
        oLabelFooter.Model.FontDescriptor = fdBigFont
        oLabelFooter.Model.Align = 1
        oLabelFooter.Model.FontRelief = 1
        oLabelFooter.Model.MultiLine = True
        sMessage = "Tiny Report v1.0 \nCopyright 2007-TODAY Tiny sprl \nThis product is free software, under the GPL licence."
        oLabelFooter.Text = sMessage
#
#        if __name__=="package":
#
#            self.win.addImageControl("imgAbout",0,0,225,169,sImagePath= "file:///home/hjo/Desktop/trunk/bin/package/images/About.jpg")#path.__getslice__(0,path.rfind("/")) + "/package/images/About.jpg")
#        else:
#            print "abc"
#            self.win.addImageControl("imgAbout",0,0,225,169,sImagePath="file:///home/hjo/Desktop/trunk/bin/package/images/About.jpg")
        self.win.doModalDialog("",None)

if __name__<>"package" and __name__=="__main__":
    About(None)
elif __name__=="package":
    g_ImplementationHelper.addImplementation( \
            About,
            "org.openoffice.tiny.report.about",
            ("com.sun.star.task.Job",),)

