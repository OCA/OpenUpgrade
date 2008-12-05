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
from report import interface
from osv import osv
import time

#class offer_document(rml_parse):
#    def __init__(self, cr, uid, name, context):
#        super(offer_document, self).__init__(cr, uid, name, context)
#        self.localcontext.update({
#            'time': time,
#        })
#        self.context = context
#    def _eval(self, expr):
#        print "=========================",expr
#        object={}
#        object['customer_order_field_ids']='dm.customer.order'
#        object['customer_field_ids']='dm.customer'
#        field = expr.split('.')[0].strip()
#        pool = pooler.get_pool(self.cr.dbname)
#        if field.find('objects')<0:
#            print object[field]
##            ids = pool.get(object[field]).searh(self.cr,self.uid,[])
#            ids = pool.get('dm.customer').search(self.cr,self.uid,[])
#            res1 = pool.get(object[field]).read(self.cr,self.uid,ids,[field])
#            print "------------------------------------------------------------------",res1
#        res = super(offer_document,self)._eval(expr)
#        print "----------------------------",res
#        return res        

#from report_sxw import report_sxw

#def my_register_all(db,report=False):
#    opj = os.path.join
#    cr = db.cursor()
#    if report and report['actual_model'] :
#        cr.execute("SELECT * FROM ir_act_report_xml WHERE id =%d"%report['id'])
#        result = cr.dictfetchall()
#        cr.close()
#        for r in result:
#            if r['report_rml'] or r['report_rml_content_data']:
#                r = report_sxw('report.'+r['report_name'], r['model'],
#                        opj('addons',r['report_rml'] or '/'), header=r['header'],parser=offer_document)
#    else:
#        cr.execute("select * from ir_act_report_xml where not auto and actual_model is not null")
#        result = cr.dictfetchall()
#        if result:
#            cr.close()
#            for r in result:
#                if r['report_rml'] or r['report_rml_content_data']:
#                    r = report_sxw('report.'+r['report_name'], r['model'],
#                            opj('addons',r['report_rml'] or '/'), header=r['header'],parser=offer_document)
#        else:
#            cr.execute("SELECT * FROM ir_act_report_xml WHERE auto ORDER BY id")
#            result = cr.dictfetchall()
#            cr.close()
#            for r in result:
#                if netsvc.service_exist('report.'+r['report_name']):
#                    continue
#                if r['report_rml'] or r['report_rml_content_data']:
#                    report_sxw('report.'+r['report_name'], r['model'],
#                            opj('addons',r['report_rml'] or '/'), header=r['header'])
#                if r['report_xsl']:
#                    interface.report_rml('report.'+r['report_name'], r['model'],
#                            opj('addons',r['report_xml']),
#                            r['report_xsl'] and opj('addons',r['report_xsl']))
#interface.register_all =  my_register_all
class report_xml(osv.osv):
    _inherit = 'ir.actions.report.xml'
    _columns = {
        'actual_model':fields.char('Report Object', size=64),
        'document_id':fields.integer('Document'),
        }
#
#    def upload_report(self, cr, uid, report_id, file_sxw, context):
#        '''
#        Untested function
#        '''
#        pool = pooler.get_pool(cr.dbname)
#        sxwval = StringIO(base64.decodestring(file_sxw))
#        fp = tools.file_open('normalized_oo2rml.xsl',
#                subdir='addons/base_report_designer/wizard/tiny_sxw2rml')
#        report = pool.get('ir.actions.report.xml').write(cr, uid, [report_id], {
#            'report_sxw_content': base64.decodestring(file_sxw),
#            'report_rml_content': str(sxw2rml(sxwval, xsl=fp.read()))
#        })
#        cr.commit()
#        report = pool.get('ir.actions.report.xml').read(cr, uid, [report_id],['actual_model'])[0]
#        db = pooler.get_db_only(cr.dbname)
#        my_register_all(db,report)
#        return True
#
report_xml()

#class new_report_sxw(report_sxw.report_sxw):
def mygetObjects(self, cr, uid, ids, context):
    table = self.table
    if 'actual_model' in context and context['actual_model']:
        table =context['actual_model']
        ids = pooler.get_pool(cr.dbname).get(table).search(cr,uid,[])
    res = pooler.get_pool(cr.dbname).get(table).browse(cr, uid, ids, list_class=browse_record_list, context=context, fields_process=_fields_process)
    return res
report_sxw.getObjects = mygetObjects