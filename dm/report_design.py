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
from osv import osv
import time
from customer_function import customer_function


def generate_reports(cr,uid,obj,report_type,context):
    customer_id = obj.customer_id.id
    step_id = obj.step_id.id
    pool = pooler.get_pool(cr.dbname)
    dm_doc_obj = pool.get('dm.offer.document') 
    report_xml = pool.get('ir.actions.report.xml')

    document_id = dm_doc_obj.search(cr,uid,[('step_id','=',obj.step_id.id),('category_id','=','Production')])

    type_id = pool.get('dm.campaign.document.type').search(cr,uid,[('code','=',report_type)])

    vals={'segment_id': obj.segment_id.id, 'name': obj.step_id.code + "_" +str(obj.customer_id.id), 'type_id': type_id[0]}

    camp_doc  = pool.get('dm.campaign.document').create(cr,uid,vals)
    
    if document_id :
        report_ids = report_xml.search(cr,uid,[('document_id','=',document_id[0]),('report_type','=',report_type)])
        document_name = dm_doc_obj.read(cr,uid,document_id,['name'])[0]['name']
        if report_ids :
            attachment_obj = pool.get('ir.attachment')
            for report in pool.get('ir.actions.report.xml').browse(cr, uid, report_ids) :
                srv = netsvc.LocalService('report.'+report.report_name)
                context['customer_id'] = customer_id
                context['document_id'] = document_id[0]
                report_data,report_type = srv.create(cr, uid, [], {},context)
                attach_vals={'name' : document_name+ "_" +str(obj.customer_id.id),
                             'datas_fname' : 'report.'+report.report_name+'.'+report_type ,
                             'res_model' : 'dm.campaign.document',
                             'res_id' : camp_doc,
                             'datas': base64.encodestring(report_data),
                             }
                attachment_obj.create(cr,uid,attach_vals)
    return True



def generate_plugin_value(cr, uid, document_id, customer_id, context={}):
    if not document_id :
        return False
    if not customer_id :
        return False
    vals = {}

    pool = pooler.get_pool(cr.dbname)
    def compute_customer_plugin(cr, uid, p, cid):
        args = {}
        res  = pool.get('ir.model').browse(cr, uid, p.model_id.id)
        args['model_name'] = res.model
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
            plugin_value = compute_customer_plugin(cr, uid, p, customer_id)

        else :
            arguments = p.argument_ids
            for a in arguments:
                if not a.stored_plugin :
                    args[str(a.name)]=str(a.value)
                else :
                    args[str(a.name)]=compute_customer_plugin(cr, uid, a.custome_plugin_id, customer_id)
            path = os.path.join(os.getcwd(), "addons/dm/dm_ddf_plugins", cr.dbname)
            plugin_name = p.file_fname.split('.')[0]
            sys.path.append(path)
            X =  __import__(plugin_name)
            plugin_func = getattr(X, plugin_name)
            plugin_value = plugin_func(cr, uid, customer_id, **args)

        if p.store_value : 
            dm_plugins_value.create(cr, uid,{'date':time.strftime('%Y-%m-%d'),
                                             'customer_id':customer_id,
                                             'plugin_id':p.id,
                                             'value' : plugin_value})
        vals[str(p.id)] = plugin_value
    return vals

class offer_document(rml_parse):
    def __init__(self, cr, uid, name, context):
        super(offer_document, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'document':self.document,
        })
        self.context = context        
    def document(self):
        if 'form' not in self.datas :
            customer_id = self.context['customer_id']
            document_id = self.context['document_id']
        else :
            customer_id = self.datas['form']['customer_id']
            document_id = self.ids[0]
        values = generate_plugin_value(self.cr,self.uid,document_id,customer_id)
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
