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
from report_design import generate_plugin_value
import re
import base64

_regexp1 = re.compile('(\[\'.+?\'\])')
_regexp2 = re.compile('\'.+?\'')
class offer_document(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        print "Calling offer_document __init__"
        super(offer_document, self).__init__(cr, uid, name, context)
        print "Calling offer_document super"
        self.localcontext.update({
            'time': time,
            'document':self.document,
            'trademark_id' : self.trademark_id,
        })
        print "Calling offer_document localcontext"
        self.context = context

    def _plugin_list(self):
        ir_obj = self.pool.get('ir.actions.report.xml')
        report_xml_ids = ir_obj.search(self.cr, self.uid,[('report_name', '=', self.name)])
        if report_xml_ids:
            report_xml = ir_obj.browse(self.cr, self.uid, report_xml_ids[0])
            raw_plugin_list = _regexp1.findall(report_xml.report_rml_content)
            plugin_list = []
            for i in raw_plugin_list :
                plugin = _regexp2.findall(i)[0].replace("'",'')
                plugin_list.append(plugin)
            return plugin_list
        else :
            return False

    def trademark_id(self):
        if 'form' not in self.datas :
            workitem_id = self.context['active_id']
            res = self.pool.get('dm.workitem').browse(self.cr,self.uid,workitem_id)
            return res.segment_id.proposition_id.camp_id.trademark_id
        else:
            return self.datas['form']['trademark_id']	

    def document(self):
        if 'form' not in self.datas :
            addr_id = self.context['address_id']
            doc_id = self.context['document_id']
            wi_id = self.context['active_id']
        else :

            addr_id = self.datas['form']['address_id']
            doc_id = self.ids[0]

            dm_workitem_obj = self.pool.get('dm.workitem')
            wi_data=dm_workitem_obj.search(self.cr,self.uid,[])

            if not wi_data:
                document = self.pool.get('dm.offer.document').browse(self.cr,self.uid,doc_id)

                dm_segment_obj = self.pool.get('dm.campaign.proposition.segment')
                segment_data_id=dm_segment_obj.search(self.cr,self.uid,[])

                wi_id = dm_workitem_obj.create(self.cr, self.uid,{'address_id':addr_id,
                                             'step_id':document.step_id.id,
                                             'segment_id' : segment_data_id[0]})

            else :
                wi_id = wi_data[0]
        values = generate_plugin_value(self.cr,self.uid,doc_id=doc_id,addr_id=addr_id,wi_id=wi_id,plugin_list=self._plugin_list())
        return [values]
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:        
