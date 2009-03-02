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

import os
import tools
from tools.translate import _

from base_module_quality import base_module_quality
import pooler
import re
import tools
import xml.dom.minidom

class quality_test(base_module_quality.abstract_quality_check):

    def __init__(self):
        super(quality_test, self).__init__()
        self.name = _("Workflow Test")
        self.note = _("This test checks where object has workflow or not on it if there is a state field and several buttons on it and also checks validity of workflow xml file")
        self.bool_installed_only = True
        self.ponderation = 1
        return None

    def run_test(self, cr, uid, module_path):
        pool = pooler.get_pool(cr.dbname)
        module_name = module_path.split('/')[-1]
        obj_list = self.get_objects(cr, uid, module_name)
        view_obj = pool.get('ir.ui.view')
        view_ids = view_obj.search(cr, uid, [('model', 'in', obj_list), ('type', 'in', ['form'])])
        view_data = view_obj.browse(cr, uid, view_ids)
        field_obj = pool.get('ir.model.fields')
        field_ids = field_obj.search(cr, uid, [('model', 'in', obj_list)])
        field_data = field_obj.browse(cr, uid, field_ids)
        state_check = []
        wkf_avail = []
        result_dict = {}
        if obj_list:
            wkf_ids = pool.get('workflow').search(cr, uid, [('osv', 'in', obj_list)])
            wkfs = pool.get('workflow').read(cr, uid, wkf_ids, ['osv'])
            for i in wkfs:
                wkf_avail.append(i['osv'])
        for field in field_data:
            if field.name == 'state':
                state_check.append(field.model)
        bad_view = 0
        good_view = 0
        for view in view_data:
            if view.model in state_check:
                dom = xml.dom.minidom.parseString(view.arch)
                node = dom.childNodes
                attrs = self.node_attributes(node[0])
                count = self.count_button(node[0], count=0)
                if count > 3 and not view.model in wkf_avail:
                    bad_view +=  1
                    result_dict[view.model] = [view.model, 'The presence of a field state in object often indicative of a need for workflow behind. And connect them to ensure consistency in this field.']
                elif count > 0 and view.model in wkf_avail:
                    good_view += 1
        self.score = float(good_view) / float(bad_view + good_view)
        self.result = self.get_result({ module_name: ['Result Workflow', int(self.score * 100)]})
        self.result_details += self.get_result_details(result_dict)
        return None

    def get_result(self, dict):
        header = ('{| border="1" cellspacing="0" cellpadding="5" align="left" \n! %-40s \n! %-10s \n', [_('Module Name'), _('Result of views in %')])
        if not self.error:
            return self.format_table(header, data_list=dict)
        return ""

    def get_result_details(self, dict):
        str_html = '''<html><head></head><body><table border="1">'''
        header = ('<tr><th>%s</th><th>%s</th></tr>', [_('Object Name'),_('Feed back About Workflow of Module')])
        if not self.error:
            res = str_html + self.format_html_table(header, data_list=dict) + '</table><newline/></body></html>'
            return res
        return ""

    def node_attributes(self, node):
        result = {}
        attrs = node.attributes
        if attrs is None:
            return {}
        for i in range(attrs.length):
            result[attrs.item(i).localName] = str(attrs.item(i).nodeValue)
            if attrs.item(i).localName == "digits" and isinstance(attrs.item(i).nodeValue, (str, unicode)):
                result[attrs.item(i).localName] = eval(attrs.item(i).nodeValue)
        return result

    def count_button(self, node, count):
        for node in node.childNodes:
            if node.localName == 'button':
                count += 1
            if node.childNodes:
                count = self.count_button(node, count)
        return count

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
