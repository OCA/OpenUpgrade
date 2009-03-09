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

from tools.translate import _

from base_module_quality import base_module_quality
import pooler

class quality_test(base_module_quality.abstract_quality_check):

    def __init__(self):
        super(quality_test, self).__init__()
        self.name = _("PEP-8 Test")
        self.note = _("""
PEP-8 Test
""")
        self.bool_installed_only = False
        self.ponderation = 1.0
        self.bad_standard = 0
        self.good_standard = 0
        self.result_py = {}
        return None

    def run_test(self, cr, uid, module_path):
        list_files = os.listdir(module_path)
        for i in list_files:
                path = os.path.join(module_path, i)
                if os.path.isdir(path):
                    for j in os.listdir(path):
                        list_files.append(os.path.join(i, j))

        py_list = []
        for file_py in list_files:
            if file_py.split('.')[-1] == 'py' and not file_py.endswith('__init__.py') and not file_py.endswith('__terp__.py'):
                file_path = os.path.join(module_path, file_py)
                py_list.append(file_path)

        self.check_import(py_list)
        self.check_licence(py_list)
        self.check_loop(py_list)
        self.check_space(py_list)
        self.check_space_operator(py_list)
        self.score = self.good_standard and float(self.good_standard) / float(self.good_standard + self.bad_standard)
        self.result = self.get_result({ module_path: [int(self.score * 100)]})
        self.result_details += self.get_result_general(self.result_py)
        return None

    def check_import(self, py_list):
        for py in py_list:
            f = open(py, 'r')
            class_or_def = False
            line_counter = 0
            file_name = py.split('/')[-1]
            while True:
                line_counter += 1
                line = f.readline()
                if not line: break
                if ((line.find('class') > -1) or (line.find('def') > -1)):
                    class_or_def = True
                import_found = line.find('import')
                comment_found = line.find('#')
                if comment_found == -1 and import_found != -1:
                    self.good_standard += 1
                    if (class_or_def):
                        self.bad_standard += 1
                        self.result_py[file_name + str(line_counter)] = [file_name, line_counter, 'Imports are always put at the top of the file, just after any module comments and docstrings, and before module globals and constants']
                    if (line.find('from') < 0 and line.find(',') != -1):
                        self.bad_standard += 1
                        self.result_py[file_name + str(line_counter)] = [file_name, line_counter, 'Imports should usually be on separate lines']

    def check_licence(self, py_list):
        for py in py_list:
            f = open(py, 'r')
            bad_position = False
            copyright_found = False
            gnu_found = False
            license_found = False
            gnu_website_found = False
            line_counter = 0
            file_name = py.split('/')[-1]
            while True:
                declaration = False
                flag = False
                line_counter += 1
                line = f.readline()
                if not line: break
                if ((line.find('class') > -1) or (line.find('def') > -1) or (line.find('import') > -1)):
                    bad_position = True
                comment_found = line.find('#')
                copyright_found = line.find('Copyright')
                gnu_found = line.find('GNU')
                license_found = line.find('License')
                gnu_website_found = line.find('www.gnu.org/licenses')
                if ((copyright_found > -1) or (gnu_found > -1) or (license_found > -1) or (gnu_website_found > -1)):
                    self.good_standard += 1
                    declaration = True
                    flag = True
                    break
                if (comment_found > -1) and bad_position and declaration:
                    self.bad_standard += 1
                    self.result_py[file_name + str(line_counter)] = [file_name, line_counter, 'Declaration of copyright must be at the top of file']
                    break
            if bad_position and (not flag):
                self.bad_standard += 1
                self.result_py[file_name] = [file_name, '--', 'File is not copyright']

    def check_loop(self, py_list):
        for py in py_list:
            f = open(py, 'r')
            methods = ['browse', 'search', 'read', 'copy', 'unlink']
            place_for = 1000
            file_name = py.split('/')[-1]
            line_counter = 0
            counter = 0
            while True:
                line_counter += 1
                line = f.readline()
                if not line: break
                place_method = 0
                for i in line :
                    if (i == ' '):
                        place_method += 1
                    elif (i != ' '):
                        break
                    elif (place_method > 100):
                        break
                if (line.find('for') > -1):
                    place_for = place_method
                if (place_for < place_method):
                    counter += 1
                    for method in methods:
                        got = line.find(method)
                        if(got > -1):
                            self.bad_standard += 1
                            self.result_py[file_name + str(line_counter)] = [file_name, line_counter, 'puting method inside loop is not good']
            self.good_standard += counter

    def check_space(self, py_list):
        for py in py_list:
            f = open(py, 'r')
            counter_line = 0
            file_name = py.split('/')[-1]
            counter = 0
            while True:
                counter_line += 1
                line = f.readline()
                if not line: break
                pos_comma = line.find(',')
                pos_semicolon = line.find(';')
                pos_colon = line.find(':')
                space_find = -1
                if (pos_comma != -1 or pos_semicolon != -1 or pos_colon != -1):
                    counter += 1
                    for i in line:
                        space_find += 1
                        if (i == ' '):
                            if ((space_find + 1) == pos_comma) or ((space_find + 1) == pos_semicolon) or ((space_find + 1) == pos_colon):
                                self.bad_standard += 1
                                self.result_py[file_name + str(counter_line)] = [file_name, counter_line, 'You should not have space before (: ; ,)']
            self.good_standard += counter #  to be check

    def check_space_operator(self, py_list):
        for py in py_list:
            f = open(py, 'r')
            space_counter = 0
            eq_found = False
            operator_found = False
            line_counter = 0
            file_name = py.split('/')[-1]
            while True:
                line_counter += 1
                line = f.readline()
                if not line: break
                for counter in line:
                    if (counter == ' '):
                        space_counter += 1
                    else:
                        if (space_counter > 1):
                            if counter in ['=', '<', '>', '!', '+', '-', '*', '/', '^', '%'] or operator_found:
                                self.bad_standard += 1
                                self.result_py[file_name + str(line_counter)] = [file_name, line_counter, 'More than one space around an assignment (or other) operator to align it with another']
                        operator_found = False
                        space_counter = 0
                    if counter in ['=', '<', '>', '!', '+', '-', '*', '/', '^', '%']:
                        self.good_standard += 1
                        operator_found = True

    def get_result(self, dict_obj):
        header = ('{| border="1" cellspacing="0" cellpadding="5" align="left" \n! %-40s \n', [_('Result of import statements in py %')])
        if not self.error:
            return self.format_table(header, data_list=dict_obj)
        return ""

    def get_result_general(self, dict_obj):
        str_html = '''<html><strong>Result</strong><head></head><body><table>'''
        header = ('<tr><th>%s</th><th>%s</th><th>%s</th></tr>', [_('Object Name'), _('Line number'), _('Suggestion')])
        if not self.error:
            res = str_html + self.format_html_table(header, data_list=dict_obj) + '</table></body></html>'
            return res
        return ""

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

