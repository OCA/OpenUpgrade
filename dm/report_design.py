from osv import fields
from osv import osv
import pooler
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

class offer_document(rml_parse):
    def __init__(self, cr, uid, name, context):
        super(offer_document, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'document':self.document,
        })
        self.context = context        
    def document(self):
        dm_customer_order = pooler.get_pool(self.cr.dbname).get('dm.customer.order')        
        dm_plugins_value = pooler.get_pool(self.cr.dbname).get('dm.plugins.value')
        order_id = dm_customer_order.search(self.cr,self.uid,[('offer_step_id','=',self.ids)])
        order = dm_customer_order.browse(self.cr,self.uid,order_id)
        customer_id = map(lambda x:x.customer_id.id,order)
        res=[]
        for cust in customer_id:
            vals={}
            vals['cust_id'] = cust
            plugin_ids = dm_plugins_value.search(self.cr,self.uid,[('customer_id','=',cust)])
            plugin_values = dm_plugins_value.read(self.cr,self.uid,plugin_ids,['plugin_id','value'])
            for plugin in plugin_values:
                vals[str(plugin['plugin_id'][0])]=plugin['value']
            res.append(vals)
        return res

from report.report_sxw import report_sxw

def my_register_all(db,report=False):
    opj = os.path.join
    cr = db.cursor()
    cr.execute("SELECT * FROM ir_act_report_xml WHERE model=%s ORDER BY id", ('dm.offer.document',))
    result = cr.dictfetchall()
    if result :
        cr.close()
        for r in result:
            if netsvc.service_exist('report.'+r['report_name']):
                continue
            if r['report_rml'] or r['report_rml_content_data']:
                report_sxw('report.'+r['report_name'], r['model'],
                        opj('addons',r['report_rml'] or '/'), header=r['header'],parser=offer_document)
    else :
        cr.execute("SELECT * FROM ir_act_report_xml WHERE auto=%s ORDER BY id", (True,))
        result = cr.dictfetchall()
        cr.close()
        for r in result:
            if netsvc.service_exist('report.'+r['report_name']):
                continue
            if r['report_rml'] or r['report_rml_content_data']:
                print opj('addons',r['report_rml'] or '/')
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
report_xml()

#def mygetObjects(self, cr, uid, ids, context):
#    table = self.table
#    pool = pooler.get_pool(cr.dbname)
#    ir_actions_report_xml_obj = pool.get('ir.actions.report.xml')
#    if self.table=='dm.offer.document':
#        report_xml_ids = ir_actions_report_xml_obj.search(cr, uid,
#                [('report_name', '=', self.name[7:])], context=context)        
#        if report_xml_ids:
#            report_xml = ir_actions_report_xml_obj.browse(cr, uid, report_xml_ids[0],
#                    context=context)
#            table=report_xml.actual_model
#        ids = pooler.get_pool(cr.dbname).get(table).search(cr,uid,[])
#    res = pooler.get_pool(cr.dbname).get(table).browse(cr, uid, ids, list_class=browse_record_list, context=context, fields_process=_fields_process)
#    return res