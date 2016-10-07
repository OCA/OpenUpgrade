# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2012-2015 Odoo Community Association (OCA)
#    (<http://odoo-community.org>)
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

try:
    from openerp.osv.orm import TransientModel, except_orm
    from openerp.osv import fields
    from openupgradelib import openupgrade_tools
    from openerp import pooler
except ImportError:
    from osv.osv import osv_memory as TransientModel, except_osv as except_orm
    from osv import fields
    from openupgradelib import openupgrade_tools
    import pooler


class generate_records_wizard(TransientModel):
    _name = 'openupgrade.generate.records.wizard'
    _description = 'OpenUpgrade Generate Records Wizard'
    _columns = {
        'state': fields.selection(
            [('init', 'init'), ('ready', 'ready')], 'State'),
        }
    _defaults = {
        'state': lambda *a: 'init',
        }

    def quirk_payment_term_lines(self, cr, uid, context=None):
        """ Installing the account module again adds another 'balance'
        line to all standard payment terms in the module's data. This
        violates a constraint that there can only be one balance line.
        Remove these lines upon reinstallation """
        module_obj = self.pool.get('ir.module.module')
        if module_obj.search(
                cr, uid, [('state', '=', 'to install'),
                          ('name', '=', 'account')]):
            term_ids = [
                self.pool['ir.model.data'].xmlid_to_res_id(
                    cr, uid, xmlid) for xmlid in
                ['account.account_payment_term_15days',
                 'account.account_payment_term_net']]
            if term_ids:
                cr.execute(
                    """
                    DELETE FROM account_payment_term_line
                    WHERE payment_id in %s AND value = 'balance'
                    """, (tuple(term_ids),))

    def generate(self, cr, uid, ids, context=None):
        """
        Main wizard step. Make sure that all modules are up-to-date,
        then reinitialize all installed modules.
        Equivalent of running the server with '-d <database> --init all'

        The goal of this is to fill the records table.

        TODO: update module list and versions, then update all modules?
        """
        # Truncate the records table
        if (openupgrade_tools.table_exists(cr, 'openupgrade_attribute') and
                openupgrade_tools.table_exists(cr, 'openupgrade_record')):
            cr.execute(
                'TRUNCATE openupgrade_attribute, openupgrade_record;'
                )

        # Need to get all modules in state 'installed'
        module_obj = self.pool.get('ir.module.module')
        module_ids = module_obj.search(
            cr, uid, [('state', 'in', ['to install', 'to upgrade'])])
        if module_ids:
            cr.commit()
            _db, pool = pooler.restart_pool(cr.dbname, update_module=True)
        # Did we succeed above?
        module_ids = module_obj.search(
            cr, uid, [('state', 'in', ['to install', 'to upgrade'])])
        if module_ids:
            modules = module_obj.read(
                cr, uid, module_ids, ['name'], context=context)
            raise except_orm(
                "Cannot reliably generate records",
                ("Cannot seem to install or upgrade modules " +
                 ', '.join([x['name'] for x in modules])))
        # Now reinitialize all installed modules
        module_ids = module_obj.search(
            cr, uid, [('state', '=', 'installed')])
        module_obj.write(
            cr, uid, module_ids, {'state': 'to install'})
        self.quirk_payment_term_lines(cr, uid, context=context)
        cr.commit()
        _db, pool = pooler.restart_pool(cr.dbname, update_module=True)
        self.write(cr, uid, ids, {'state': 'ready'})
        # and we are done
        return True

generate_records_wizard()
