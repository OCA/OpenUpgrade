# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module Copyright (C) 2012 OpenUpgrade community
#    https://launchpad.net/~openupgrade-committers
#
#    Contributors:
#    Therp BV <http://therp.nl>
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

import os
from osv import osv, fields

try:
    from openerp.addons.openupgrade_records.lib import compare
    from openerp.openupgrade_records.lib import apriori
    from openerp.addons import get_module_path
except ImportError:
    from openupgrade_records.lib import compare
    from openupgrade_records.lib import apriori
    from addons import get_module_path

class openupgrade_analysis_wizard(osv.osv_memory):
    _name = 'openupgrade.analysis.wizard'
    _description = 'OpenUpgrade Analysis Wizard'
    _columns = {
        'server_config': fields.many2one(
            'openupgrade.comparison.config',
            'Configuration', required=True),
        'state': fields.selection(
            [('init', 'Init'), ('ready', 'Ready')], 'State',
            readonly=True),
        'log': fields.text('Log'),
        'write': fields.boolean(
            'Write files',
            help='Write analysis files to the module directories'
            ),
        }
    _defaults = {
        'state': lambda *a: 'init',
        'write': lambda *a: True,
        }

    def get_communication(self, cr, uid, ids, context=None):
        """ 
        Retrieve both sets of database representations,
        perform the comparison and register the resulting
        change set
        """
        def write_file(
            module, version, contents, filename='openupgrade_analysis.txt'):
            module_path = get_module_path(module)
            if not module_path:
                return "ERROR: could not find module path:\n"
            full_path = os.path.join(
                module_path, 'migrations', version)
            if not os.path.exists(full_path):
                try:
                    os.makedirs(full_path)
                except os.error:
                    return "ERROR: could not create migrations directory:\n"
            logfile = os.path.join(full_path, filename)
            try:
                f = open(logfile, 'w')
            except Exception:
                return "ERROR: could not open file %s for writing:\n" % logfile
            f.write(contents)
            f.close()
            return None

        wizard = self.browse(cr, uid, ids[0], context=context)
        # Retrieve connection and access methods
        conf_obj = self.pool.get('openupgrade.comparison.config')
        connection = conf_obj.get_connection(
            cr, uid, [wizard.server_config.id], context=context)
        remote_record_obj = connection.get_model('openupgrade.record')
        local_record_obj = self.pool.get('openupgrade.record')
        
        # Retrieve field representations and compare
        remote_records = remote_record_obj.field_dump(context)
        local_records = local_record_obj.field_dump(cr, uid, context)
        res = compare.compare_sets(remote_records, local_records)

        # Retrieve xml id representations and compare
        fields = ['module', 'model', 'name']
        local_xml_record_ids = local_record_obj.search(
            cr, uid, [('type', '=', 'xmlid')])
        remote_xml_record_ids = remote_record_obj.search(
            [('type', '=', 'xmlid')])
        local_xml_records = [
            dict([(field, x[field]) for field in fields])
            for x in local_record_obj.read(
                cr, uid, local_xml_record_ids, fields)
            ]
        remote_xml_records = [
            dict([(field, x[field]) for field in fields])
            for x in remote_record_obj.read(
                remote_xml_record_ids, fields)
            ]
        res_xml = compare.compare_xml_sets(
            remote_xml_records, local_xml_records)

        # reorder and output the result
        keys = list(set(res.keys() + res_xml.keys()))
        keys.remove('general')
        keys = ['general'] + keys
        module_obj = self.pool.get('ir.module.module')
        module_ids = module_obj.search(
            cr, uid, [('state', '=', 'installed')])
        modules = dict([(x['name'], x) for x in module_obj.read(cr, uid, module_ids)])
        general = ''
        for key in keys:
            contents = "---Fields in module '%s'---\n" % key
            if key in res:
                contents += '\n'.join([unicode(line) for line in sorted(res[key])])
                if res[key]:
                    contents += '\n'
            contents += "---XML records in module '%s'---\n" % key
            if key in res_xml:
                contents += '\n'.join([unicode(line) for line in res_xml[key]])
                if res_xml[key]:
                    contents += '\n'
            if key == 'general':
                general += contents
                continue
            if key not in modules:
                general += (
                    "ERROR: module not in list of installed modules:\n"
                    + contents)
                continue
            if wizard.write:
                error = write_file(
                    key, modules[key]['installed_version'], contents)
                if error:
                    general += error
                    general += contents
            else:
                general += contents
        
        # Store the general log in as many places as possible ;-)
        if wizard.write and 'base' in modules:
            write_file(
                'base', modules['base']['installed_version'], general,
                'openupgrade_general_log.txt')
        self.pool.get('openupgrade.comparison.config').write(
            cr, uid, wizard.server_config.id,
            {'last_log': general})
        self.write(cr, uid, ids, {'state': 'ready', 'log': general})

        result = {
            'name': self._description,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'openupgrade.analysis.wizard',
            'domain': [],
            'context': context,
            'type': 'ir.actions.act_window',
            #'target': 'new',
            'res_id': ids[0],
            }
        return result

openupgrade_analysis_wizard()

