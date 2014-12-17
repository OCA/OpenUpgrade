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

#####################################################################
#   library providing a function to analyse two progressive database
#   layouts from the OpenUpgrade server.
#####################################################################

import collections
import copy

try:
    from openerp.addons.openupgrade_records.lib import apriori
except ImportError:
    from openupgrade_records.lib import apriori


def module_map(module):
    return apriori.renamed_modules.get(module, module)


def model_map(model):
    return apriori.renamed_models.get(model, model)


IGNORE_FIELDS = [
    ]


def compare_records(dict_old, dict_new, fields):
    """
    Check equivalence of two OpenUpgrade field representations
    with respect to the keys in the 'fields' arguments.
    Take apriori knowledge into account for mapped modules or
    model names.
    Return True of False.
    """
    for field in fields:
        if field == 'module':
            if (module_map(dict_old[field]) != dict_new[field]):
                return False
        elif field == 'model':
            if (model_map(dict_old[field]) != dict_new[field]):
                return False
        elif dict_old[field] != dict_new[field]:
            return False
    return True


def search(item, item_list, fields):
    """
    Find a match of a dictionary in a list of similar dictionaries
    with respect to the keys in the 'fields' arguments.
    Return the item if found or None.
    """
    for other in item_list:
        if not compare_records(item, other, fields):
            continue
        return other
    # search for renamed fields
    if 'field' in fields:
        for other in item_list:
            if not item['field'] or item['field'] != other.get('oldname'):
                continue
            if compare_records(
                    dict(item, field=other['field']), other, fields):
                return other
    return None


def fieldprint(old, new, field, text, reprs):
    fieldrepr = "%s (%s)" % (old['field'], old['type'])
    fullrepr = '%-12s / %-24s / %-30s' % (
        old['module'], old['model'], fieldrepr)
    if not text:
        text = "%s is now '%s' ('%s')" % (field, new[field], old[field])
    reprs[module_map(old['module'])].append("%s: %s" % (fullrepr, text))


def report_generic(new, old, attrs, reprs):
    for attr in attrs:
        if attr == 'required':
            if old[attr] != new['required'] and new['required']:
                text = "now required"
                if new['req_default']:
                    text += ', default = %s' % new['req_default']
                fieldprint(old, new, None, text, reprs)
        elif attr == 'isfunction':
            if old['isfunction'] != new['isfunction']:
                if new['isfunction']:
                    text = "now a function"
                else:
                    text = "not a function anymore"
                fieldprint(old, new, None, text, reprs)
        elif attr == 'oldname':
            if new.get('oldname') == old['field']:
                text = 'was renamed to %s [nothing to to]' % new['field']
                fieldprint(old, new, None, text, reprs)
        elif old[attr] != new[attr]:
            fieldprint(old, new, attr, None, reprs)


def compare_sets(old_records, new_records):
    """
    Compare a set of OpenUpgrade field representations.
    Try to match the equivalent fields in both sets.
    Return a textual representation of changes in a dictionary with
    module names as keys. Special case is the 'general' key
    which contains overall remarks and matching statistics.
    """
    reprs = collections.defaultdict(list)

    for record in old_records + new_records:
        record['matched'] = False
    origlen = len(old_records)
    new_models = set([column['model'] for column in new_records])
    old_models = set([column['model'] for column in old_records])

    matched_direct = 0
    matched_other_module = 0
    matched_other_type = 0
    matched_other_name = 0
    in_obsolete_models = 0

    obsolete_models = []
    for model in old_models:
        if model not in new_models:
            obsolete_models.append(model)
            reprs['general'].append('obsolete model %s' % model)

    for column in copy.copy(old_records):
        if column['model'] in obsolete_models:
            old_records.remove(column)
            in_obsolete_models += 1

    for model in new_models:
        if model not in old_models:
            reprs['general'].append('new model %s' % model)

    def match(match_fields, report_fields, warn=False):
        count = 0
        for column in copy.copy(old_records):
            found = search(column, new_records, match_fields)
            if found:
                if warn:
                    pass
                    # print "Tentatively"
                report_generic(found, column, report_fields, reprs)
                old_records.remove(column)
                new_records.remove(found)
                count += 1
        return count

    matched_direct = match(
        ['module', 'mode', 'model', 'field'],
        ['relation', 'type', 'selection_keys', 'inherits',
         'isfunction', 'required', 'oldname'])

    # other module, same type and operation
    matched_other_module = match(
        ['mode', 'model', 'field', 'type'],
        ['module', 'relation', 'selection_keys', 'inherits',
         'isfunction', 'required', 'oldname'])

    # other module, same operation, other type
    matched_other_type = match(
        ['mode', 'model', 'field'],
        ['relation', 'type', 'selection_keys', 'inherits',
         'isfunction', 'required', 'oldname'])

    # fields with other names
    # matched_other_name = match(
    # ['module', 'type', 'relation'],
    # ['field', 'relation', 'type', 'selection_keys',
    #   'inherits', 'isfunction', 'required'], warn=True)

    printkeys = [
        'relation', 'required', 'selection_keys',
        'req_default', 'inherits', 'mode'
        ]
    for column in old_records:
        # we do not care about removed function fields
        if column['isfunction'] or column['field'] in IGNORE_FIELDS:
            continue
        if column['mode'] == 'create':
            column['mode'] = ''
        fieldprint(
            column, None, None, "DEL " + ", ".join(
                [k + ': ' + str(column[k]) for k in printkeys if column[k]]
                ), reprs)

    for column in new_records:
        # we do not care about newly added function fields
        if column['isfunction'] or column['field'] in IGNORE_FIELDS:
            continue
        if column['mode'] == 'create':
            column['mode'] = ''
        fieldprint(
            column, None, None, "NEW " + ", ".join(
                [k + ': ' + str(column[k]) for k in printkeys if column[k]]
                ), reprs)

    for line in [
            "# %d fields matched," % (origlen - len(old_records)),
            "# Direct match: %d" % matched_direct,
            "# Found in other module: %d" % matched_other_module,
            "# Found with different type: %d" % matched_other_type,
            "# Found with different name: %d" % matched_other_name,
            "# In obsolete models: %d" % in_obsolete_models,
            "# Not matched: %d" % len(old_records),
            "# New columns: %d" % len(new_records)
            ]:
        reprs['general'].append(line)
    return reprs


def compare_xml_sets(old_records, new_records):
    reprs = collections.defaultdict(list)
    match_fields = ['module', 'model', 'name']
    for column in copy.copy(old_records):
        found = search(column, new_records, match_fields)
        if found:
            old_records.remove(column)
            new_records.remove(found)

    for record in old_records:
        record['old'] = True
    for record in new_records:
        record['new'] = True

    sorted_records = sorted(
        old_records + new_records,
        key=lambda k: (k['model'], 'old' in k, k['name'])
    )
    for entry in sorted_records:
        if 'old' in entry:
            content = 'DEL %(model)s: %(name)s' % entry
        elif 'new' in entry:
            content = 'NEW %(model)s: %(name)s' % entry
        reprs[module_map(entry['module'])].append(content)
    return reprs
