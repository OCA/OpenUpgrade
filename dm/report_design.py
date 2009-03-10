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
from document import dm_ddf_plugin
from customer_function import customer_function

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
                 res  = self.pool.get('ir.model').browse(self.cr,self.uid,plugin.model_id.id)
                 args['model_name']=str(res.model)
                 args['field_name']=str(plugin.field_id.name)
                 args['field_type']=str(plugin.field_id.ttype)
                 args['field_relation']=str(plugin.field_id.relation)
                 plugin_value = customer_function(self.cr,self.uid,[customer_id],**args)
                 for p in plugin_value : 
                      vals[str(plugin.id)]=p[1]
            else :                
                arguments = plugin.argument_ids
                for a in arguments:
                    if not a.stored_plugin :
                        args[str(a.name)]=str(a.value)
                    else :
                         res  = self.pool.get('ir.model').browse(self.cr,self.uid,a.custome_plugin_id.model_id.id)
                         arg = {'model_name':str(res.model),
                                     'field_name':str(a.custome_plugin_id.field_id.name),
                                     'field_type':str(a.custome_plugin_id.field_id.ttype),
                                     'field_relation' : str(a.custome_plugin_id.field_id.relation)}
                         plugin_value = customer_function(self.cr,self.uid,[customer_id],**arg)
                         for p in plugin_value : 
                             args[str(a.name)]=p[1]                        
                path = os.path.join(os.getcwd(), "addons/dm/dm_ddf_plugins",self.cr.dbname)
                plugin_name = plugin.file_fname.split('.')[0]
                import sys
                sys.path.append(path)
                X =  __import__(plugin_name)
                plugin_func = getattr(X,plugin_name)
                plugin_values = plugin_func(self.cr,self.uid,[customer_id],**args)
                for p in plugin_values:
                    vals[str(plugin.id)]=p[1]
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
