# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2011 Therp BV (<http://therp.nl>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

""" 

    Standalone runnable to analyse two progressive datase layouts from the
    OpenUpgrade server.

"""

import  copy, csv, re
keys = ['module', 'operation', 'model', 'field', 'type', 'isfunction', 'relation', 'required', 'selection_keys', 'req_default', 'inherits']

def readfile(file):
    fields = []
    readfile = csv.reader(open(file, 'rb'), delimiter=',', quotechar='"')
    for row in readfile:
        col = 0
        field = {}
        for key in keys:
            field[key] = row[col]
            col += 1
        field['matched'] = False
        fields.append(field)
    return fields

def equal(dicta, dictb, ignore):
    ka = dicta.keys()
    kb = dictb.keys()
    kbstatic = dictb.keys()
    for keyset in [ ka, kb, kbstatic ]:
        for k in ignore:
            keyset.remove(k)
    for k in ka:
        if k not in kbstatic:
            return False
        if dicta[k] != dictb[k]:
            return False
        kb.remove(k)
    if kb:
        return False
    return True

def compare(dicta, dictb, fields):
    for field in fields:
        if dicta[field] != dictb[field]:
            return False
    return True

def search(item, dict, fields):
    for i in dict:
        if not compare(item, i, fields):
            continue
        return i
    return None

def fieldprint(old, new, field='NOT SPECIFIED', text=None):
#    repr = 'module %s, model %s, field %s (%s)' % (old['module'], old['model'], old['field'], old['type'])
    fieldrepr = "%s (%s)" % (old['field'], old['type'])
    repr = '%s / %s / %s' % (old['module'].ljust(12), old['model'].ljust(24), fieldrepr.ljust(30))
    if text:
        print "%s: %s" % (repr, text)
    else:
        print "%s: %s is now \'%s\' ('%s')" % (repr, field, new[field], old[field])

def report_generic(new, old, attrs):
    for attr in attrs:
        if attr == 'required':
            if old[attr] != new['required'] and new['required']:
                text = "now required"
                if column['req_default']:
                    text += ', default = %s' % column['req_default']
                fieldprint(old, new, text=text)
        elif attr == 'isfunction':
            if old['isfunction'] != new['isfunction']:
                if new['isfunction']:
                    text = "now a function"
                else:
                    text = "not a function anymore"
                fieldprint(old, new, text=text)
        else:
            if old[attr] != new[attr]:
                fieldprint(old, new, attr)

k5 = readfile('5.csv')
k6 = readfile('6.csv')

origlen = len(k5)

models6 = set([ column['model'] for column in k6 ])
models5 = set([ column['model'] for column in k5 ])

matched_direct = 0
matched_other_module = 0
matched_other_type = 0
matched_other_name = 0
in_obsolete_models = 0

obsolete_models = []
for model in models5:
    if model not in models6:
        obsolete_models.append(model)
        print '# model %s removed' % model

for column in copy.copy(k5):
    if column['model'] in obsolete_models:
        k5.remove(column)
        in_obsolete_models += 1

for model in models6:
    if model not in models5:
        print '# new model %s' % model
    
def match(match_fields, report_fields, warn=False):
    count = 0
    for column in copy.copy(k5):
        found = search(column, k6, match_fields)
        if found:
            if warn:
                print "Tentatively"
            report_generic(found, column, report_fields)
            k5.remove(column)
            k6.remove(found)
            count += 1
    return count

matched_direct = match(['module', 'operation', 'model', 'field'],
                       ['relation', 'type', 'selection_keys', 'inherits', 'isfunction', 'required'])

# other module, same type and operation
matched_other_module = match(['operation', 'model', 'field', 'type'],
                             ['module', 'relation', 'selection_keys', 'inherits', 'isfunction', 'required'])

# other module, same operation, other type
matched_other_type = match(['operation', 'model', 'field'],
                           ['relation', 'type', 'selection_keys', 'inherits', 'isfunction', 'required'])

# fields with other names
#matched_other_name = match(['module', 'type', 'relation'],
#                           ['field', 'relation', 'type', 'selection_keys', 'inherits', 'isfunction', 'required'], warn=True)

printkeys = ['relation', 'required', 'selection_keys', 'req_default', 'inherits', 'operation']
for column in k5:
    # we do not care about removed function fields
    if not column['isfunction']:
        if column['operation'] == 'create':
            column['operation'] = ''
        fieldprint(column, None, text="DEL " + ", ".join([k + ': ' + str(column[k]) for k in printkeys if column[k]]))
for column in k6:
    # we do not care about newly added function fields
    if not column['isfunction']:
        if column['operation'] == 'create':
            column['operation'] = ''
        fieldprint(column, None, text="NEW " + ", ".join([k + ': ' + str(column[k]) for k in printkeys if column[k]]))

print "# %d fields matched," % (origlen - len(k5))
print "# Direct match: %d" % matched_direct
print "# Found in other module: %d" % matched_other_module
print "# Found with different type: %d" % matched_other_type
print "# Found with different name: %d" % matched_other_name
print "# In obsolete models: %d" % in_obsolete_models
print "# Not matched: %d" % len(k5)
print "# New columns: %d" % len(k6)
