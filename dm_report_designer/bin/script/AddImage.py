import uno
import string
import unohelper
import xmlrpclib
from com.sun.star.task import XJobExecutor
if __name__<>"package":
    from lib.gui import *
    from lib.functions import *
    from lib.error import ErrorDialog
    from lib.tools import write_data_to_file
    from LoginTest import *
    database="dm"
    dm_data ={}
    dm_data['document_id']=1
    passwd = 'admin'
    uid = 1
import base64
import uno
import pyuno
import getopt, sys, string
import os
from com.sun.star.text.ControlCharacter import PARAGRAPH_BREAK
from com.sun.star.text.TextContentAnchorType import AT_PARAGRAPH, AS_CHARACTER     
    
class AddImage(unohelper.Base, XJobExecutor ):
    def __init__(self,sVariable="",sFields="",sDisplayName="",bFromModify=False):
        LoginTest()
        if not loginstatus and __name__=="package":
            exit(1)
        self.win = DBModalDialog(60, 50, 190, 90, "Field Builder")

        self.win.addFixedText("lblImage", 10, 12, 60, 15, "Attachment :")
        self.win.addComboBox("cmbImage", 180-130, 10, 130, 15,True)
        
        self.win.addButton('btnOK',-5 ,-5,45,15,'Ok' ,actionListenerProc = self.btnOk_clicked )
        self.win.addButton('btnCancel',-5 - 45 - 5 ,-5,45,15,'Cancel' ,actionListenerProc = self.btnCancel_clicked )
        
        self.cmbImage = self.win.getControl( "cmbImage" )

        global passwd
        self.password = passwd
        self.sGDisplayName=sDisplayName
        desktop=getDesktop()
        doc =desktop.getCurrentComponent()
        docinfo=doc.getDocumentInfo()
        self.sMyHost= ""
        self.datas={}
        if not docinfo.getUserFieldValue(3) == "" and not docinfo.getUserFieldValue(0)=="":
            self.sMyHost = docinfo.getUserFieldValue(0)
            sock = xmlrpclib.ServerProxy(self.sMyHost + '/xmlrpc/object')
            
            self.attachment_ids = sock.execute(database, uid, self.password, 'ir.attachment' ,  'search', [('res_model','=','dm.offer.document'),('res_id','=',dm_data['document_id'])])
            res = sock.execute(database, uid, self.password, 'ir.attachment' ,  'read',self.attachment_ids, ['datas_fname','datas'])
            for r in res:
                self.cmbImage.addItem(r['datas_fname'],self.cmbImage.getItemCount())
                self.datas[r['datas_fname']]=r['datas']
            self.win.doModalDialog("cmbImage",None)                    
        else:
            ErrorDialog("You have not selected document and model for \n the report.Please select it first from \n Direct Marketing Reporting ->Select Document")
            self.win.endExecute()

    def create_image(self,image_file_name):
        image_ext= image_file_name.split(".")[-1]
        fp_name = tempfile.mktemp("."+image_ext)
        fp_name1="r"+fp_name
        fp_path=os.path.join(fp_name1).replace("\\","/")
        fp_win=fp_path[1:]
        filename = ( os.name == 'nt' and fp_win or fp_name )
        if image_file_name in self.datas and self.datas[image_file_name]:
            write_data_to_file( filename, base64.decodestring(self.datas[image_file_name]))
        return filename      
      
    def insert_image(self,filename):
        desktop=getDesktop()
        doc =desktop.getCurrentComponent()
        docinfo=doc.getDocumentInfo()
        text = doc.Text
        cursor = doc.getCurrentController().getViewCursor()
        oBitmaps = doc.createInstance('com.sun.star.drawing.BitmapTable')
        oBitmaps.insertByName(filename, filename)
        url = oBitmaps.getByName(filename)
        mySize = uno.createUnoStruct('com.sun.star.awt.Size')
        mySize.Width = 5000
        mySize.Height = 5000
        text.insertControlCharacter(cursor, PARAGRAPH_BREAK, False)
        oShape = doc.createInstance("com.sun.star.drawing.GraphicObjectShape")
        oShape.GraphicURL =url 
        oShape.AnchorType = AS_CHARACTER 
        oShape.Size = mySize
        myPosition = uno.createUnoStruct('com.sun.star.awt.Point') 
        myPosition.X = oShape.Position.X-400
        myPosition.Y = oShape.Position.Y-400                    
        oShape.Position=myPosition
        text.insertTextContent(cursor,oShape,uno.Bool(0))
        
    def btnOk_clicked( self, oActionEvent ):
        try :
            image_file_name = self.win.getComboBoxSelectedText("cmbImage")
            filename = self.create_image(image_file_name)
            self.insert_image(filename)
        except Exception,e:
            print "Exception e",e
        self.win.endExecute()            
    def btnCancel_clicked( self, oActionEvent ):
        self.win.endExecute()

if __name__<>"package" and __name__=="__main__":
    AddImage()
elif __name__=="package":
    g_ImplementationHelper.addImplementation( AddImage, "org.openoffice.openerp.report.addimage", ("com.sun.star.task.Job",),)
