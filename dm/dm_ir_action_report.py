# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
import netsvc
from osv import fields, osv
import pooler
import os
from dm_document_report import offer_document
from report.report_sxw import report_sxw
from report import interface
from StringIO import StringIO
import base64
from lxml import etree 

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
            print "2222222222222222222255555555"
            report_sxw('report.'+r['report_name'], r['model'],
                    opj('addons',r['report_rml'] or '/'), header=r['header'],parser=offer_document)
            print "222222222222222222222222"
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
        print file_type
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
        
    def set_image_email(self,cr,uid,report_id):
        list_image_id = []
        def process_tag(node,list_image_id):
            if not node.getchildren():
                if  node.tag=='img' and node.get('name') and node.get('name').find('[[setHtmlImage')>=0:
                    res_id= _regex.split(node.get('name'))[1]
                    list_image_id.append((res_id,node.get('src')))
            else :
                for n in node.getchildren():
                    process_tag(n,list_image_id)
        datas = self.report_get(cr, uid, report_id)['report_sxw_content']
        root = etree.HTML(base64.decodestring(datas))
        process_tag(root,list_image_id)
        return list_image_id 

report_xml()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:               
