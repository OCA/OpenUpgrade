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
import pooler
from report import report_sxw
from dm.dm_report_design import generate_plugin_value
import re
import base64

_regexp1 = re.compile('(\[\'.+?\'\])')
_regexp2 = re.compile('\'.+?\'')

class offer_document(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(offer_document, self).__init__(cr, uid, name, context)
        self.localcontext.update({
#            'time': time,
            'document':self.document,
#            'trademark_id' : self.trademark_id,
            'report_type':''
        })
        self.context = context

    def _plugin_list(self):
        ir_obj = self.pool.get('ir.actions.report.xml')
        report_xml_ids = ir_obj.search(self.cr, self.uid,[('report_name', '=', self.name)])
        if report_xml_ids:
            report_xml = ir_obj.browse(self.cr, self.uid, report_xml_ids[0])
            self.report_type = report_xml.report_type
            rml = report_xml.report_rml_content
            raw_plugin_list = _regexp1.findall(rml)
            plugin_list = []
            for i in raw_plugin_list :
                plugin = _regexp2.findall(i)[0].replace("'", '')
                plugin_list.append(plugin)
            return plugin_list
        else :
            return False

    def trademark_id(self):
        if 'form' not in self.datas :
            if 'segment_id' in self.context:
                segment_id = self.pool.get('dm.campaign.proposition.segment').browse(self.cr, self.uid, self.context['segment_id'])
                return segment_id.proposition_id.camp_id.trademark_id.id
            elif 'workitem_id' in self.context:
                workitem_id = self.pool.get('dm.workitem').browse(self.cr, self.uid, self.context['workitem_id'])
                return workitem_id.segment_id.proposition_id.camp_id.trademark_id.id
            else : return False
        else:
            segment_id = self.pool.get('dm.campaign.proposition.segment').browse(self.cr, self.uid, self.datas['form']['segment_id'])
            return segment_id.trademark_id.id

    def document(self):
        plugin_list = self._plugin_list()
        if 'form' not in self.datas :
            type = 'email_doc'
            address_id = self.context['address_id']
            document_id = self.context['document_id']
            if 'segment_id' in self.context:
                segment_id = self.context['segment_id']
            else:
                segment_id = False
            camp_doc_id = self.context['camp_doc_id']
            workitem_id = self.context['workitem_id']
        else :
            type = 'preview'
            address_id = self.datas['form']['address_id']
            document_id = self.ids[0]
            segment_id = self.datas['form']['segment_id']
            camp_doc_id = False

            doc = self.pool.get('dm.offer.document').browse(self.cr, self.uid, document_id)
            workitem_id = self.pool.get('dm.workitem').create(self.cr, self.uid, {'address_id':address_id,
                'segment_id':segment_id, 'step_id':doc.step_id.id, 'is_preview':True, 
                'state':'done'})

        values = generate_plugin_value(self.cr, self.uid, 
            document_id = document_id,
            camp_doc_id = camp_doc_id,
            address_id = address_id,
            segment_id = segment_id,
            workitem_id = workitem_id,
            plugin_list = plugin_list,
            type = type,
            )
        return [values]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
