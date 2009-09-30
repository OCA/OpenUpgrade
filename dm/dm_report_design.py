from osv import fields
from osv import osv
import pooler
import tools
import netsvc

from plugin.customer_function import customer_function
from plugin.dynamic_text import dynamic_text
from plugin.php_url import php_url
from plugin.current_time import current_time

import re
import time
import datetime
import base64
import os
import sys

# To Fix : use no style css, no static values, en-IN ??
internal_html_report = '''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
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
_regex = re.compile('\[\[setHtmlImage\((.+?)\)\]\]')

def merge_message(cr, uid, keystr, context): # {{{
    " Merge offer internal document content and plugins values "
    def merge(match):
        dm_obj = pooler.get_pool(cr.dbname).get('dm.offer.document')
        obj = dm_obj.browse(cr, uid, context.get('document_id'))
        exp = str(match.group()[2:-2]).strip()
        args = context.copy()
        if 'plugin_list' in context :
            args['plugin_list'] = context['plugin_list']
        else :
            args['plugin_list'] = [exp]

        plugin_values = generate_plugin_value(cr, uid, **args)
        context.update(plugin_values)
        context.update({'object':obj, 'time':time})
        result = eval(exp, context)
        if result in (None, False):
            # What is that ?
            return str("!!!Missing-Plugin-Value!!!")
        return result
    com = re.compile('(\[\[.+?\]\])')
    message = com.sub(merge, keystr)
    return message # }}}
    
def generate_internal_reports(cr, uid, report_type, document_data, camp_doc, context): # {{{

    "Generate documents from the internal editor"
    pool = pooler.get_pool(cr.dbname)
    attachment_obj = pool.get('ir.attachment')
    
    if report_type=='html2html' and document_data.content:
        "Check if to use the internal editor report"
        if not document_data.content:
                return "no_report_for_document"
        report_data = internal_html_report + str(document_data.content)+"</BODY></HTML>"
        context['type'] = 'email_doc'
        report_data = merge_message(cr, uid, report_data, context)
        if camp_doc : 
           attach_vals={'name' : document_data.name + "_" + str(context['address_id']),
                       'datas_fname' : 'report_test' + report_type ,
                       'res_model' : 'dm.campaign.document',
                       'res_id' : camp_doc,
                       'datas': base64.encodestring(report_data),
                       'file_type':'html'
                       }
           attach_id = attachment_obj.create(cr,uid,attach_vals,{'not_index_context':True})
           return "doc_done"
        return report_data # }}}

def generate_openoffice_reports(cr, uid, report_type, document_data, camp_doc, context): # {{{
    " Generate documents created by OpenOffice "

    """ Get reports to process """
    report_content = []
    pool = pooler.get_pool(cr.dbname)    
    attachment_obj = pool.get('ir.attachment')
    report_xml = pool.get('ir.actions.report.xml')
    
    report_ids = report_xml.search(cr, uid, [('document_id','=',document_data.id),
        ('report_type','=',report_type)])
    if not report_ids :
        return "no_report_for_document"

    for report in pool.get('ir.actions.report.xml').browse(cr, uid, report_ids) :
        srv = netsvc.LocalService('report.' + report.report_name)
        report_data, report_type = srv.create(cr, uid, [], {}, context)
        if camp_doc : 
            attach_vals = {
                    'name' : document_data.name + "_" + str(context['address_id']) + str(report.id),
                    'datas_fname' : 'report.' + report.report_name + '.' + report_type ,
                    'res_model' : 'dm.campaign.document',
                    'res_id' : camp_doc,
                    'datas': base64.encodestring(report_data),
                    'file_type':report_type
                    }
            attach_id = attachment_obj.create(cr,uid,attach_vals,{'not_index_context':True})
        else :
            report_content.append(report_data)
    if report_content and not camp_doc:
        return report_content
    else :
        return "doc_done" # }}}

def document_process(cr, uid, obj, report_type, context): # {{{

    """ Set addess_id depending of the source : partner address, crm case, etc """
    address_id = getattr(obj, obj.source).id
    address_ids = []

    if obj.is_global:
        """ if internal segment workitem """
        for cust_id in getattr(obj.segment_id.customers_file_id, obj.source + "s"):
            address_ids.append(cust_id.id)
    else:
        """ if customer workitem """
        address_ids.append(address_id)

    if obj.step_id:
        step_id = obj.step_id.id
    else:
        return {'code':"no_step_for_wi"}

    pool = pooler.get_pool(cr.dbname)
    dm_doc_obj = pool.get('dm.offer.document') 
    report_xml = pool.get('ir.actions.report.xml')
    camp_mail_service_obj = pool.get('dm.campaign.mail_service')


    """ Set mail service to use """
    if obj.mail_service_id:
        mail_service = obj.mail_service_id
    else:
        if obj.segment_id :
            if not obj.segment_id.proposition_id:
                return {'code':"no_proposition_for_wi"}
            elif not obj.segment_id.proposition_id.camp_id:
                return {'code':"no_campaign_for_wi"}
            else:
                camp_id = obj.segment_id.proposition_id.camp_id.id
                camp_mail_service_id = camp_mail_service_obj.search(cr,uid,[('campaign_id','=',camp_id),('offer_step_id','=',step_id)])
                if not camp_mail_service_id:
                    return {'code':"no_mail_service_for_campaign"}
                else:
                    mail_service = camp_mail_service_obj.browse(cr, uid, camp_mail_service_id)[0].mail_service_id
        else:
            return {'code':"no_segment_for_wi"}

    ms_id = mail_service.id

    """ Get offer step documents to process """
    document_id = dm_doc_obj.search(cr, uid, [('step_id','=',obj.step_id.id),('category_id','=','Production')])
    if not document_id :
        return {'code':"no_document_for_step"}
    document_data = dm_doc_obj.browse(cr, uid, document_id[0])

    if not document_data.content and document_data.editor == 'internal' :
        return {'code':"no_report_for_document"}
    report_ids = report_xml.search(cr, uid, [('document_id','=',document_data.id),('report_type','=',report_type)])
    if not report_ids and document_data.editor == 'oord' :
        return {'code':"no_report_for_document"}

    r_type = report_type
    if report_type == 'html2html':
        r_type = 'html'

    type_id = pool.get('dm.campaign.document.type').search(cr,uid,[('code','=',r_type)])
    
    if obj.sale_order_id:
        so = obj.sale_order_id.name
    else:
        so = False

    for address_id in address_ids:

        """ Create campaign document """
        vals={
            'segment_id': obj.segment_id.id or False,
            'name': obj.step_id.code + "_" + str(address_id),
            'type_id': type_id[0],
            'mail_service_id': ms_id,
            'document_id' : document_id[0],
            (obj.source) : address_id,
            'origin' : so,
            }

        camp_doc = pool.get('dm.campaign.document').create(cr, uid, vals)

        """ If DMS stored document """
        if mail_service.store_email_document :
            context['address_id'] = address_id
            context['document_id'] = document_id[0]
            context['store_document'] = True
            if document_data.editor ==  'internal' :
                res = generate_internal_reports(cr, uid, report_type, document_data, camp_doc, context)
            elif document_data.editor == 'oord' :
                res = generate_openoffice_reports(cr, uid, report_type, document_data, camp_doc, context)
            if type(res) not in (type([]) , type(True)) :
                return res

    return {'code':'doc_done','ids':[camp_doc]} # }}}
"""            
def compute_customer_plugin(cr, uid, **args): # {{{
    res  = pool.get('ir.model').browse(cr, uid, args['plugin_obj'].model_id.id)    
    args['model_name'] = res.model
    args['field_name'] = str(args['plugin_obj'].field_id.name)
    args['field_type'] = str(args['plugin_obj'].field_id.ttype)
    args['field_relation'] = str(args['plugin_obj'].field_id.relation)
    return customer_function(cr, uid, **args) # }}}
"""
def _generate_value(cr, uid, plugin_obj, localcontext, **args): # {{{
    pool = pooler.get_pool(cr.dbname)
    localcontext['plugin_obj'] = plugin_obj
    plugin_args={}
    plugin_value = ''
    if plugin_obj.type in ('fields','image'):
        res  = pool.get('ir.model').browse(cr, uid, plugin_obj.model_id.id)    
        args['model_name'] = res.model
        args['field_name'] = str(plugin_obj.field_id.name)
        args['field_type'] = str(plugin_obj.field_id.ttype)
        args['field_relation'] = str(plugin_obj.field_id.relation)
        plugin_value = customer_function(cr, uid, **args)
        if not plugin_value :
            return False
    else :
        arg_ids = pool.get('dm.plugin.argument').search(cr,uid,[('plugin_id','=',plugin_obj.id)])
        for arg in pool.get('dm.plugin.argument').browse(cr,uid,arg_ids):
            if not arg.stored_plugin :
                plugin_args[str(arg.name)] = arg.value
            else :
                plugin_args[str(arg.name)] = _generate_value(cr,uid,arg.custome_plugin_id,
                    localcontext,**args)

        if plugin_obj.type=='dynamic' and plugin_obj.python_code :
            localcontext.update(plugin_args)
            localcontext['pool']=pool
            exec plugin_obj.python_code.replace('\r','') in localcontext
            plugin_value =  plugin_obj.code in localcontext and localcontext[plugin_obj.code] or ''
        elif plugin_obj.type == 'dynamic_text' :
            plugin_args['ref_text_id'] = plugin_obj.ref_text_id.id
            args.update(plugin_args)
            plugin_value = dynamic_text(cr, uid, **args)
        elif plugin_obj.type == 'url' :
            plugin_args['encode'] = plugin_obj.encode
            plugin_value = php_url(cr, uid,**plugin_args)
        else :
            path = os.path.join(os.getcwd(), "addons/dm/dm_dtp_plugins", cr.dbname)
            plugin_name = plugin_obj.file_fname.split('.')[0]
            sys.path.append(path)
            X =  __import__(plugin_name)
            plugin_func = getattr(X, plugin_name)
            plugin_value = plugin_func(cr, uid,**args)
    return plugin_value # }}}

def generate_plugin_value(cr, uid, **args): # {{{
    if not 'document_id' in args and not args['document_id'] :
        return False
    vals = {}
    localcontext = {'cr':cr,'uid':uid}
    localcontext.update(args)

    pool = pooler.get_pool(cr.dbname)
    dm_document = pool.get('dm.offer.document')
    dm_plugins_value = pool.get('dm.plugins.value')

    plugins = dm_document.browse(cr, uid, args['document_id'], ['document_template_plugin_ids' ])
    if 'plugin_list' in args and args['plugin_list'] :
        "Get plugins to compute value"
        p_ids = pool.get('dm.dtp.plugin').search(cr,uid,[('code','in',args['plugin_list'])])
        plugin_ids = pool.get('dm.dtp.plugin').browse(cr,uid,p_ids)
    else :
        "If no plugins in document do nothing"
        return {}
        
    for plugin_obj in plugin_ids :
        "Compute plugin value"
        plugin_value = _generate_value(cr, uid, plugin_obj, localcontext, **args)
#       dnt remove this comment it s for url changes
#        if plugin_obj.type == 'url' :
#            vals['%s_text_display'%str(plugin_obj.code)] = plugin_value[-1]
#            plugin_value = plugin_value[0]
        if plugin_obj.store_value :
            if not 'camp_doc_id' in args and not args['camp_doc_id'] :
                return False
            dm_plugins_value.create(cr, uid,{
                'document_id' : args['camp_doc_id'],
                'plugin_id' : plugin_obj.id,
                'value' : plugin_value
            })
        vals[str(plugin_obj.code)] = plugin_value

    return vals # }}}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
