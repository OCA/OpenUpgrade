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

from tools.translate import _

from base_module_quality import base_module_quality
import pooler
import re

class quality_test(base_module_quality.abstract_quality_check):

    def __init__(self):
        super(quality_test, self).__init__()
        self.name = _("Object Test")
        self.note = _("""
Test Checks if fields and views on the object
""")
        self.bool_installed_only = True
        self.ponderation = 1.0
        return None

    def run_test(self, cr, uid, module_path):
        pool = pooler.get_pool(cr.dbname)
        module_name = module_path.split('/')[-1]
        obj_list = self.get_objects(cr, uid, module_name)
        field_obj = pool.get('ir.model.fields')
        view_obj = pool.get('ir.ui.view')
        field_ids = field_obj.search(cr, uid, [('model', 'in', obj_list)])
        view_ids = view_obj.search(cr, uid, [('model', 'in', obj_list)])
        field_data = field_obj.browse(cr, uid, field_ids)
        view_data = view_obj.browse(cr, uid, view_ids)
        result_dict = {}
        result_view = {}
        good_field = 0
        bad_field = 0
        total_field = 0
        for field in field_data:
            type = field.ttype
            name = field.name
            total_field += 1
            check_str = re.compile('[a-z]+[\w_]*$') #re.compile('[a-z]+[_]?[a-z]+$')
            if type == 'many2one':
                if name.split('_')[-1] == 'id':
                    good_field += 1
                else:
                    data = 'many2one field should end with _id'
                    result_dict[name] = [field.model, name, data]
                    bad_field += 1
            elif type in ['many2many', 'one2many']:
                if name.split('_')[-1] == 'ids':
                    good_field += 1
                else:
                    data = '%s field should end with _ids'%(type)
                    result_dict[name] = [field.model, name, data]
                    bad_field += 1
            elif check_str.match(name):
                good_field += 1
            else:
                data = 'Field name should be in lower case or it should follow python standard'
                result_dict[name] = [field.model, name, data]
                bad_field += 1

        view_dict = {}
        total_views = len(obj_list) * 2
        model_views = 0
        for view in view_data:
            view_dict[view.model] = []
            model_views += 1
        for view in view_data:
            type = view.type
            view_dict[view.model].append(view.type)
        for dict in view_dict:
            if len(view_dict[dict]) < 2:
                result_view[dict] = [dict, 'You should have atleast form/tree view of an object']

        score_view = float(model_views) / float(total_views)
        score_field = total_field and float(good_field) / float(total_field)
        self.score = (score_view + score_field)/2

        self.result = self.get_result({ module_name: [int(score_field * 100), int(score_view * 100)]})
        self.result_details += self.get_result_details(result_dict)
        self.result_details += self.get_result_views(result_view)
        return None

    def get_result(self, dict):
        header = ('{| border="1" cellspacing="0" cellpadding="5" align="left" \n! %-40s \n! %-10s \n', [_('Result of fields in %'), _('Result of views in %')])
        if not self.error:
            return self.format_table(header, data_list=dict)
        return ""

    def get_result_details(self, dict):
        str_html = '''<html><head></head><body><table border="1">'''
        header = ('<tr><th>%s</th><th>%s</th><th>%s</th></tr>',[_('Object Name'), _('Field name'), _('Suggestion')])
        if not self.error:
           res = str_html + self.format_html_table(header, data_list=dict) + '</table></body></html>'
           return res
        return ""

    def get_result_views(self, dict):
        str_html = '''<html><head></head><body><table border="1">'''
        header = ('<tr><th>%s</th><th>%s</th></tr>',[_('Object Name'), _('Suggestion')])
        if not self.error:
           res = str_html + self.format_html_table(header, data_list=dict) + '</table></body></html>'
           return res
        return ""

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

