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
        dm_document = self.pool.get('dm.offer.document')
        dm_plugins_value = self.pool.get('dm.plugins.value')
        ddf_plugin = self.pool.get('dm.ddf.plugin')
        customer_id = self.datas['form']['customer_id']
        document = dm_document.browse(self.cr,self.uid,self.ids,['document_template_id','step_id'])[0]
        plugins = document.document_template_id.plugin_ids or []
        vals={}
        for plugin in plugins:
            args={}
            if plugin.type=='fields':
                res  = self.pool.get('ir.model').browse(self.cr,self.uid,plugin.object.id)
                args['object']=res.model
                args['field_name']=str(plugin.field.name)
                args['field_type']=str(plugin.field.ttype)
                args['field_relation']=str(plugin.field.relation)
                path = os.path.join(os.getcwd(), "addons/dm/")
                import sys
                sys.path.append(path)
                X =  __import__('customer_function')
                plugin_func = getattr(X,'customer_function')
                plugin_value = plugin_func(self.cr,self.uid,[customer_id],**args)
                for p in plugin_value : 
                    vals[str(plugin.id)]=p[1]
            else :                
                plugin_ids = dm_plugins_value.search(self.cr,self.uid,[('customer_id','=',customer_id)])
                plugin_values = dm_plugins_value.read(self.cr,self.uid,plugin_ids,['plugin_id','value'])
                for p in plugin_values:
                    vals[str(p['plugin_id'][0])]=p['value']
        return [vals]

from report.report_sxw import report_sxw

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
