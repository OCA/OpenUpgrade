import uno
import string
import unohelper
import xmlrpclib
from com.sun.star.task import XJobExecutor
if __name__<>"package":
    from lib.gui import *
    from lib.error import ErrorDialog
    from lib.functions import *
    from ServerParameter import *
    from LoginTest import *
    database="dm"
    uid = 1

def genDmTree(object,aList,insField,host,level=3, ending=[], ending_excl=[], recur=[], root='', actualroot=""):
    try:
        sock = xmlrpclib.ServerProxy(host+'/xmlrpc/object')
        global passwd
        passwd = 'admin'
        global dm_data
        document_id = dm_data['document_id']
        model = dm_data['model']
        field = dm_data['field']
        res = sock.execute(database, uid, passwd, object , 'fields_get')
        key = res.keys()
        key.sort()
        if document_id and model and object == model:
            custom = sock.execute(database, uid, passwd, 'dm.offer.document' , 'read', [document_id],[field] )[0]
            custom_field_ids = custom[field]
            custom_fields =sock.execute(database, uid, passwd, 'ir.model.fields' , 'read', custom_field_ids, )
            key = map(lambda c:c['name'],custom_fields)
            key.sort()
        for k in key:
            if (not ending or res[k]['type'] in ending) and ((not ending_excl) or not (res[k]['type'] in ending_excl)):
                insField.addItem(root+'/'+res[k]["string"],len(aList))
                aList.append(actualroot+'/'+k)
            if (res[k]['type'] in recur) and (level>0):
                genTree(res[k]['relation'],aList,insField,host ,level-1, ending, ending_excl, recur,root+'/'+res[k]["string"],actualroot+'/'+k)
    except:
        import traceback;traceback.print_exc()
def getDmList(aObjectList,host,count):
    desktop=getDesktop()
    doc =desktop.getCurrentComponent()
    docinfo=doc.getDocumentInfo()
    sMain=""
    if not count == 0:
        if count >=1:
            oParEnum = doc.getTextFields().createEnumeration()
            while oParEnum.hasMoreElements():
                oPar = oParEnum.nextElement()
                if oPar.supportsService("com.sun.star.text.TextField.DropDown"):
                    sItem=oPar.Items[1]
                    if sItem[sItem.find("[[ ")+3:sItem.find("(")]=="repeatIn":
                        if sItem[sItem.find("(")+1:sItem.find(",")]=="objects":
                            aObjectList.append(sItem[sItem.rfind(",'")+2:sItem.rfind("')")] + "(" + docinfo.getUserFieldValue(3) + ")")
                        else:
                            sTemp=sItem[sItem.find("(")+1:sItem.find(",")]
                            if sMain == sTemp[:sTemp.find(".")]:
                                getDmRelation(docinfo.getUserFieldValue(3), sItem[sItem.find(".")+1:sItem.find(",")], sItem[sItem.find(",'")+2:sItem.find("')")],aObjectList,host)
                            else:
                                sPath=getPath(sItem[sItem.find("(")+1:sItem.find(",")], sMain)
                                getDmRelation(docinfo.getUserFieldValue(3), sPath[sPath.find(".")+1:], sItem[sItem.find(",'")+2:sItem.find("')")],aObjectList,host)
    else:
        aObjectList.append("List of " + docinfo.getUserFieldValue(3))
def getDmRelation(sRelName, sItem, sObjName, aObjectList, host ):
    sock = xmlrpclib.ServerProxy(host+'/xmlrpc/object')
    global passwd
    global dm_data
    document_id = dm_data['document_id']
    model = dm_data['model']
    field = dm_data['field']
    res = sock.execute(database, uid, passwd, sRelName , 'fields_get')
    key = res.keys()
    if document_id and model and object == model[0]:
        custom = sock.execute(database, uid, passwd, 'dm.offer.document' , 'read', [document_id],field )[0]
        custom_field_ids = custom[field]
        custom_fields =sock.execute(database, uid, passwd, 'ir.model.fields' , 'read', custom_field_ids, )
        key = map(lambda c:c['name'],custom_fields)
        key.sort()

    for k in key:
        if sItem.find(".") == -1:
            if k == sItem:
                aObjectList.append(sObjName + "(" + res[k]['relation'] + ")")
                return 0
    if k == sItem[:sItem.find(".")]:
        getRelation(res[k]['relation'], sItem[sItem.find(".")+1:], sObjName,aObjectList,host)
    
#class directmarketing:
class Directmarketing( unohelper.Base, XJobExecutor ):
    def __init__(self,ctx):
        self.ctx     = ctx
        self.module  = "openerp_report"
        self.version = "0.1"
        LoginTest()
        if not loginstatus and __name__=="package":
            exit(1)
        global passwd
        global dm_data
        dm_data={}
        self.password = passwd
        self.password = 'admin'
        self.OfferCode={}
        self.OfferStepCode={}
        self.OfferDocument={}
        self.aListModel={}

        desktop=getDesktop()
        doc = desktop.getCurrentComponent()
        self.docinfo=doc.getDocumentInfo()
        
        self.sock = xmlrpclib.ServerProxy(self.docinfo.getUserFieldValue(0) +'/xmlrpc/object')
        self.sMyHost = self.docinfo.getUserFieldValue(0)
        self.win = DBModalDialog(60, 50, 180, 105, "Direct Marketing")

        ids = self.sock.execute(database, uid, self.password, 'ir.module.module', 'search', [('name','=','base_report_designer'),('state', '=', 'installed')])
        if not len(ids):
            ErrorDialog("Please Install base_report_designer  module first!", "", "Module Uninstalled Error")
            exit(1)

        ids = self.sock.execute(database, uid, self.password, 'ir.module.module', 'search', [('name','=','dm'),('state', '=', 'installed')])
        if not len(ids):
            ErrorDialog("Please Install Direct Marketing  module to continue!", "", "Module Uninstalled Error")
            exit(1)

        self.win.addFixedText("lblOffer", 2, 12, 60, 15, "Select Offer:")

        self.win.addComboBox("cmbOffer", 180-120-2, 10, 120, 15,True,itemListenerProc=self.changeOffer)
        self.cmbOffer = self.win.getControl( "cmbOffer" )
        
        ids = self.sock.execute(database, uid, self.password, 'dm.offer', 'search', [('state','=','draft')])
        res = self.sock.execute(database, uid, self.password, 'dm.offer' , 'read', ids,['code'] )
        res.sort(lambda x, y: cmp(x['code'],y['code']))

        for r in res:
            self.cmbOffer.addItem(r['code'],self.cmbOffer.getItemCount())
            self.OfferCode[r['code']] = r['id']

        self.win.addFixedText("lblOfferStep", 2, 28, 60, 15 ,"Select Offer Step :")
        self.win.addComboBox("cmbOfferStep", 180-120-2, 28, 120, 15 , True ,itemListenerProc=self.changeOfferStep)
        self.cmbOfferStep = self.win.getControl( "cmbOfferStep" )

        self.win.addFixedText("lblDocument", 2, 44, 60, 15 ,"Document :")
        self.win.addComboBox("cmbDocument", 180-120-2, 46, 120, 15 , True,itemListenerProc=self.selectDocument)
        self.cmbDocument = self.win.getControl( "cmbDocument" )

        self.win.addFixedText("lblmodel", 2, 62, 60, 15 ,"Model :")
        self.win.addComboBox("cmbmodel", 180-120-2, 64, 120, 15 , True)#,itemListenerProc=self.selectDocument)
        self.cmbmodel = self.win.getControl( "cmbmodel" )
        
        self.win.addButton('btnOK',-2 ,-5,45,15,'Ok', actionListenerProc = self.btnOk_clicked )

        self.win.addButton('btnCancel',-2 - 45 - 5 ,-5,45,15,'Cancel', actionListenerProc = self.btnCancel_clicked )

        self.win.doModalDialog("cmbOffer",None)

    def selectDocument(self,oActionEvent):
        document_code = self.win.getComboBoxSelectedText("cmbDocument")
        res = self.sock.execute(database, uid, self.password, 'dm.offer.document' , 'fields_get')
        key = res.keys()
        key.sort()
        for k in key:
            if res[k]['type'] =='many2many' and res[k]['relation']=='ir.model.fields':
                self.cmbmodel.addItem(res[k]["string"],len(self.aListModel))
                self.aListModel[res[k]["string"]]=(res[k]['context']['model'],k)
                
    def changeOfferStep(self,oActionEvent):
        offer_step=self.win.getComboBoxSelectedText("cmbOfferStep")

        offer_step_id = self.OfferStepCode[offer_step]
        
        ids = self.sock.execute(database, uid, self.password, 'dm.offer.document', 'search', [('step_id','=',offer_step_id)])
        res = self.sock.execute(database, uid, self.password, 'dm.offer.document' , 'read', ids,['code','customer_field_ids','customer_order_field_ids'] )

        res.sort(lambda x, y: cmp(x['code'],y['code']))

        self.win.removeListBoxItems("cmbDocument", 0, self.win.getListBoxItemCount("cmbDocument"))

        for r in res:
            self.cmbDocument.addItem(r['code'],self.cmbDocument.getItemCount())
            self.OfferDocument[r['code']] = (r['id'],r['customer_field_ids'],r['customer_order_field_ids'])

    def changeOffer(self,oActionEvent):

        offer=self.win.getComboBoxSelectedText("cmbOffer")
        offer_id = self.OfferCode[offer]
        
        ids = self.sock.execute(database, uid, self.password, 'dm.offer.step', 'search', [('offer_id','=',offer_id)])
        res = self.sock.execute(database, uid, self.password, 'dm.offer.step' , 'read', ids,['code'] )
        res.sort(lambda x, y: cmp(x['code'],y['code']))
        
        self.win.removeListBoxItems("cmbOfferStep", 0, self.win.getListBoxItemCount("cmbOfferStep"))

        self.OfferStepCode={}
        
        for r in res:
            self.cmbOfferStep.addItem(r['code'],self.cmbOfferStep.getItemCount())
            self.OfferStepCode[r['code']] = r['id']


    def btnOk_clicked(self,oActionEvent):
        if self.win.getComboBoxSelectedText("cmbDocument") :
            document_code = self.win.getComboBoxSelectedText("cmbDocument")
            document_id =  self.OfferDocument[document_code][0]
            sMain=self.win.getComboBoxSelectedText("cmbmodel")
            global dm_data
            dm_data['document_id']=document_id                
            dm_data['field'] = self.aListModel[sMain][1]
            dm_data['model'] = self.aListModel[sMain][0]
            self.docinfo.setUserFieldValue(3,dm_data['model'])
            obj = dm_data['model'].split('.')[-1]
            sValue="[[ repeatIn(objects,'%s') ]]"%obj
            sKey = "|-."+obj+".-|"            
            desktop=getDesktop()
            doc = desktop.getCurrentComponent()
            cursor = doc.getCurrentController().getViewCursor()
            oInputList = doc.createInstance("com.sun.star.text.TextField.DropDown")
            oInputList.Items = (sKey,sValue)
            doc.Text.insertTextContent(cursor,oInputList,False)
        else :
            ErrorDialog('You have not selected any document \n First select document','',"Direct Marketing")
        self.win.endExecute()
    def btnCancel_clicked( self, oActionEvent ):
        self.win.endExecute()

if __name__<>"package" and __name__=="__main__":
    Directmarketing(None)
elif __name__=="package":
    g_ImplementationHelper.addImplementation( \
            Directmarketing,
            "org.openoffice.openerp.report.directmarketing",
            ("com.sun.star.task.Job",),)
    