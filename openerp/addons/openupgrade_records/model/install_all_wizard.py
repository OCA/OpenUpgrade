# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module Copyright (C) 2012-2014 OpenUpgrade community
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

import time
try:
    from openerp.osv.orm import TransientModel
    from openerp.osv import fields
    from openerp import pooler
except ImportError:
    from osv.osv import osv_memory as TransientModel
    from osv import fields
    import pooler


class install_all_wizard(TransientModel):
    _name = 'openupgrade.install.all.wizard'
    _description = 'OpenUpgrade Install All Wizard'
    _columns = {
        'state': fields.selection(
            [('init', 'init'), ('ready', 'ready')], 'State', readonly=True),
        'to_install': fields.integer(
            'Number of modules to install', readonly=True),
        }
    _defaults = {
        'state': lambda *a: 'init',
        }

    def default_get(self, cr, uid, fields, context=None):
        """
        Update module list and retrieve the number
        of installable modules
        """
        res = super(install_all_wizard, self).default_get(
            cr, uid, fields, context=None)
        module_obj = self.pool.get('ir.module.module')
        update, add = module_obj.update_list(cr, uid,)
        print "%s modules added" % add
        module_ids = module_obj.search(
            cr, uid, [
                ('state', 'not in',
                 ['installed', 'uninstallable', 'unknown'])
                ])
        res.update(
            {'to_install': module_ids and len(module_ids) or False}
            )
        return res

    def quirk_fiscalyear(self, cr, uid, ids, context=None):
        """
        Install account module first and create a fiscal year,
        in order to prevent "No fiscal year defined" exception
        during an upgrade or reinstallation of the account module.

        Refer to account_fiscalyear.find(), which is called as
        a default function by the orm upon module upgrade.
        """
        module_obj = self.pool.get('ir.module.module')
        pool = self.pool
        # Retrieve status of the account module
        account_module_id = module_obj.search(
            cr, uid, [('name', '=', 'account')], context=context)[0]
        state = module_obj.read(
            cr, uid, account_module_id, ['state'], context=context)['state']
        if state != 'installed':
            # Cancel installation of other modules
            module_ids = module_obj.search(
                cr, uid, [('state', '=', 'to install')])
            module_obj.write(cr, uid, module_ids, {'state': 'uninstalled'})
            # Mark the module and its dependencies
            module_obj.button_install(cr, uid, [account_module_id])
            # Install account module
            cr.commit()
            _db, pool = pooler.restart_pool(cr.dbname, update_module=True)
        # get or create today's fiscal year
        fy_obj = pool.get('account.fiscalyear')
        if not fy_obj.find(cr, uid, False, exception=False, context=context):
            fy_obj.create(cr, uid, {
                'name': time.strftime('%Y'),
                'code': time.strftime('%Y'),
                'date_start': "%s-01-01" % time.strftime('%Y'),
                'date_stop': "%s-12-31" % time.strftime('%Y'),
                })

    def install_all(self, cr, uid, ids, context=None):
        """
        Main wizard step. Set all installable modules to install
        and actually install them. Exclude testing modules.
        """
        module_obj = self.pool.get('ir.module.module')
        module_ids = module_obj.search(
            cr, uid, [
                ('state', 'not in',
                 ['installed', 'uninstallable', 'unknown']),
                ('category_id.name', '!=', 'Tests'),
                ])
        if module_ids:
            module_obj.write(
                cr, uid, module_ids, {'state': 'to install'})
            cr.commit()
            _db, pool = pooler.restart_pool(cr.dbname, update_module=True)
            self.write(cr, uid, ids, {'state': 'ready'})
        return True

install_all_wizard()
