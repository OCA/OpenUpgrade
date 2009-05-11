from osv import fields
from osv import osv
import pooler
import sys
from report.report_sxw import report_sxw,browse_record_list,_fields_process,rml_parse
from StringIO import StringIO
import base64
import tools
from base_report_designer.wizard.tiny_sxw2rml import sxw2rml
import os
import netsvc
from report import interface ,report_sxw
import time
from customer_function import customer_function
import re
import datetime
interna_html_report = '''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
<HTML>
<HEAD>
<META HTTP-EQUIV="CONTENT-TYPE" CONTENT="text/html; charset=utf-8">
    <TITLE></TITLE>
    <META NAME="GENERATOR" CONTENT="OpenOffice.org 3.0  (Linux)">
    <META NAME="CREATED" CONTENT="20090420;15063300">
    <META NAME="CHANGED" CONTENT="20090420;15071700"> 
    <META NAME="Info 4" CONTENT="dm.offer.document">
    <STYLE TYPE="text/css">
        <!--
        @page { margin: 2cm }
        P { margin-bottom: 0.21cm }
        A:link { so-language: zxx }
        -->
    </STYLE>
</HEAD>
<BODY LANG="en-IN" DIR="LTR">
'''

def merge_message(cr, uid, keystr, context):
    logger = netsvc.Logger()
    def merge(match):
        dm_obj = pooler.get_pool(cr.dbname).get('dm.offer.document')
        id = context.get('document_id')
        obj = dm_obj.browse(cr, uid, id)
        exp = str(match.group()[2:-2]).strip()
        plugin_values = generate_plugin_value(cr, uid, id, context.get('address_id'), context)
        context.update(plugin_values)
        context.update({'object':obj,'time':time})
        result = eval(exp,context)
        if result in (None, False):
            return str("--------")
        return str(result)

    com = re.compile('(\[\[.+?\]\])')
    message = com.sub(merge, keystr)
    return message


def generate_reports(cr,uid,obj,report_type,context):

    print "Calling generate_reports from wi : ", obj.id
    print "Calling generate_reports source code : ", obj.source
    address_id = getattr(obj, obj.source).id
    print "address_id : ",address_id
    address_ids = []

    if obj.is_global:
        """ if segment workitem """
        print "source fields : ",getattr(obj.segment_id.customers_file_id, obj.source + "s")
        for cust_id in getattr(obj.segment_id.customers_file_id, obj.source + "s"):
            print "cust_id : ",cust_id
            address_ids.append(cust_id.id)
    else:
        """ if customer workitem """
        address_ids.append(address_id)

    print "address_ids : ", address_ids

    step_id = obj.step_id.id
    pool = pooler.get_pool(cr.dbname)
    dm_doc_obj = pool.get('dm.offer.document') 
    report_xml = pool.get('ir.actions.report.xml')
    r_type = report_type
    if report_type=='html2html':
        r_type = 'html'
    for address_id in address_ids:
        camp_id = obj.segment_id.proposition_id.camp_id.id
        type_id = pool.get('dm.campaign.document.type').search(cr,uid,[('code','=',r_type)])
        camp_mail_service_obj = pool.get('dm.campaign.mail_service')
        camp_mail_service_id = camp_mail_service_obj.search(cr,uid,[('campaign_id','=',camp_id),('offer_step_id','=',step_id)])
        print "camp_mail_service_id",camp_mail_service_id
        camp_mail_service = camp_mail_service_obj.browse(cr,uid,camp_mail_service_id)[0]
        print "camp_mail_service.mail_service_id",camp_mail_service.mail_service_id.time_mode
        if camp_mail_service.mail_service_id.time_mode=='interval' :
            kwargs =  {(camp_mail_service.mail_service_id.unit_interval):camp_mail_service.mail_service_id.action_interval}
            delivery_time = datetime.datetime.now() + datetime.timedelta(**kwargs)
        elif camp_mail_service.mail_service_id.time_mode=='date' :
            delivery_time = camp_mail_service.mail_service_id.action_date
        elif camp_mail_service.mail_service_id.time_mode=='hour' :
            temp_time = str(camp_mail_service.mail_service_id.action_hour)
            if time.strftime('%H.%M:') > temp_time:
                date = datetime.datetime.now() + datetime.timedelta(days=1).strftime('%Y-%m-%d')
            else : 
                date = time.strftime('%Y-%m-%d')
            delivery_time = date+' '+temp_time.replace('.',':')+':00'
        else :
            delivery_time=time.strftime('%Y-%m-%d %H:%M:%S')
        print "delivery_time",delivery_time

        document_id = dm_doc_obj.search(cr,uid,[('step_id','=',obj.step_id.id),('category_id','=','Production')])
        print "Doc id : ",document_id
        print report_type

        vals={  'segment_id': obj.segment_id.id,
            'name': obj.step_id.code + "_" +str(address_id),
            'type_id': type_id[0],
            'mail_service_id':camp_mail_service.mail_service_id.id,
            'delivery_time' : delivery_time,
            'document_id' : document_id[0],
            'address_id' : obj.address_id.id
            }
        camp_doc  = pool.get('dm.campaign.document').create(cr,uid,vals)
        print "camp_doc",camp_doc

        if document_id :
            report_ids = report_xml.search(cr,uid,[('document_id','=',document_id[0]),('report_type','=',report_type)])
            print "report_ids : ",report_ids
            print dm_doc_obj.read(cr,uid,document_id,['name','editor','content','subject'])[0]

            document_data = dm_doc_obj.read(cr,uid,document_id,['name','editor','content','subject'])[0]
            print "Doc name : ",document_data['name']
            context['address_id'] = address_id
            context['document_id'] = document_id[0]
            attachment_obj = pool.get('ir.attachment')
            if report_type=='html' and document_data['editor'] and document_data['editor']=='internal' and document_data['content']:
                report_data = interna_html_report +str(document_data['content'])+"</BODY></HTML>"
                report_data = merge_message(cr, uid, report_data, context)
                attach_vals={'name' : document_data['name'] + "_" + str(address_id),
                            'datas_fname' : 'report_test' + report_type ,
                            'res_model' : 'dm.campaign.document',
                            'res_id' : camp_doc,
                            'datas': base64.encodestring(report_data),
                            'file_type':'html'
                            }
                attach_id = attachment_obj.create(cr,uid,attach_vals)
                print "Attachment id and campaign doc id" , attach_id,camp_doc
            if report_ids :
                for report in pool.get('ir.actions.report.xml').browse(cr, uid, report_ids) :
                    srv = netsvc.LocalService('report.' + report.report_name)
                    report_data,report_type = srv.create(cr, uid, [], {},context)
                    attach_vals={'name' : document_data['name'] + "_" + str(address_id)+str(report.id),
                                 'datas_fname' : 'report.' + report.report_name + '.' + report_type ,
                                 'res_model' : 'dm.campaign.document',
                                 'res_id' : camp_doc,
                                 'datas': base64.encodestring(report_data),
                                 'file_type':report_type
                                 }
                    attach_id = attachment_obj.create(cr,uid,attach_vals)
                    print "Attachement : ",attach_id



def generate_plugin_value(cr, uid, document_id, address_id,workitem_id, context={}):
    if not document_id :
        return False
    if not address_id :
        return False
    vals = {}

    pool = pooler.get_pool(cr.dbname)
    def compute_customer_plugin(cr, uid, p, cid,wi_id=None):
        args = {}
        res  = pool.get('ir.model').browse(cr, uid, p.model_id.id)
        args['model_name'] = res.model
        if res.model=='dm.workitem' and wi_id:
            args['wi_id'] = wi_id    
        args['field_name'] = str(p.field_id.name)
        args['field_type'] = str(p.field_id.ttype)
        args['field_relation'] = str(p.field_id.relation)
        return customer_function(cr,uid, [cid], **args)

    dm_document = pool.get('dm.offer.document')
    dm_plugins_value = pool.get('dm.plugins.value')
    ddf_plugin = pool.get('dm.ddf.plugin')

    plugins = dm_document.browse(cr, uid, document_id, ['document_template_plugin_ids' ])['document_template_plugin_ids']

    for p in plugins :
        args = {}
        if p.type == 'fields':
            plugin_value = compute_customer_plugin(cr, uid, p, address_id,workitem_id)

        else :
            arg_ids = pool.get('dm.plugin.argument').search(cr,uid,[('plugin_id','=',p.id)])
            for a in pool.get('dm.plugin.argument').browse(cr,uid,arg_ids):
                if not a.stored_plugin :
                    args[str(a.name)]=str(a.value)
                else :
                    args[str(a.custome_plugin_id.code)]=compute_customer_plugin(cr, uid, a.custome_plugin_id, address_id,workitem_id)
            path = os.path.join(os.getcwd(), "addons/dm/dm_ddf_plugins", cr.dbname)
            plugin_name = p.file_fname.split('.')[0]
            sys.path.append(path)
            X =  __import__(plugin_name)
            plugin_func = getattr(X, plugin_name)
            plugin_value = plugin_func(cr, uid, address_id, **args)

        if p.store_value :
            dm_plugins_value.create(cr, uid,{'date':time.strftime('%Y-%m-%d'),
                                             'address_id':address_id,
                                             'plugin_id':p.id,
                                             'value' : plugin_value})
        vals[str(p.code)] = plugin_value
    return vals

class offer_document(rml_parse):
    def __init__(self, cr, uid, name, context):
        print "Calling offer_document __init__"
        super(offer_document, self).__init__(cr, uid, name, context)
        print "Calling offer_document super"
        self.localcontext.update({
            'time': time,
            'document':self.document,
        })
        print "Calling offer_document localcontext"
        self.context = context

    def document(self):
        print "Calling document"
        if 'form' not in self.datas :
            address_id = self.context['address_id']
            document_id = self.context['document_id']
            workitem_id = self.context['active_id']
        else :
            address_id = self.datas['form']['address_id']
            document_id = self.ids[0]
#            set the workitem id here for the report which are called directly from the document object
            workitem_id = 1
        values = generate_plugin_value(self.cr,self.uid,document_id,address_id,workitem_id)
        return [values]

from report.report_sxw import report_sxw

#class my_report_sxw(report_sxw):
#    print "Tessssssssssssssssssssssss"
#    def create_single(self, cr, uid, ids, data, report_xml, context={}):
#        print "----------------------------my method"
#        report_sxw.create_single(self, cr, uid, ids, data, report_xml, context)

def my_register_all(db,report=False):
    opj = os.path.join
    cr = db.cursor()
    result=''
    cr.execute("SELECT * FROM ir_act_report_xml WHERE model=%s ORDER BY id", ('dm.offer.document',))
    result = cr.dictfetchall()
    for r in result:
        if netsvc.service_exist('report.'+r['report_name']):
            continue
        if r['report_rml'] or r['report_rml_content_data']:
            report_sxw('report.'+r['report_name'], r['model'],
                    opj('addons',r['report_rml'] or '/'), header=r['header'],parser=offer_document)
    cr.execute("SELECT * FROM ir_act_report_xml WHERE auto=%s ORDER BY id", (True,))
    result = cr.dictfetchall()
    cr.close()
    for r in result:
        if netsvc.service_exist('report.'+r['report_name']):
            continue
        if r['report_rml'] or r['report_rml_content_data']:
            report_sxw('report.'+r['report_name'], r['model'],
                    opj('addons',r['report_rml'] or '/'), header=r['header'])
        if r['report_xsl']:
            interface.report_rml('report.'+r['report_name'], r['model'],
                    opj('addons',r['report_xml']),
                    r['report_xsl'] and opj('addons',r['report_xsl']))
interface.register_all =  my_register_all

class report_xml(osv.osv):
    _inherit = 'ir.actions.report.xml'
    _columns = {
#        'actual_model':fields.char('Report Object', size=64),
        'document_id':fields.integer('Document'),
        }
    def upload_report(self, cr, uid, report_id, file_sxw,file_type, context):
        '''
        Untested function
        '''
        pool = pooler.get_pool(cr.dbname)
        sxwval = StringIO(base64.decodestring(file_sxw))
        if file_type=='sxw':
            fp = tools.file_open('normalized_oo2rml.xsl',
                    subdir='addons/base_report_designer/wizard/tiny_sxw2rml')
            rml_content = str(sxw2rml(sxwval, xsl=fp.read()))
        if file_type=='odt':
            fp = tools.file_open('normalized_odt2rml.xsl',
                    subdir='addons/base_report_designer/wizard/tiny_sxw2rml')
            rml_content = str(sxw2rml(sxwval, xsl=fp.read()))
        if file_type=='html':
            rml_content = base64.decodestring(file_sxw)
        report = pool.get('ir.actions.report.xml').write(cr, uid, [report_id], {
            'report_sxw_content': base64.decodestring(file_sxw),
            'report_rml_content': rml_content,
        })
        cr.commit()
        db = pooler.get_db_only(cr.dbname)
        interface.register_all(db)
        return True
report_xml()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
