# -*- coding: utf-8 -*-
# © 2012-2017 2012-2014 OpenUpgrade community <https://odoo-community.org/>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import time
try:
    from openerp.osv.orm import TransientModel
    from openerp.osv import fields
    from openerp import pooler
    from openerp.addons.openupgrade_records.blacklist import BLACKLIST_MODULES
except ImportError:
    from osv.osv import osv_memory as TransientModel
    from osv import fields
    import pooler
    from openupgrade_records.blacklist import BLACKLIST_MODULES
from openerp.tools.translate import _


STATE_SELECTION = [
    ('init', 'init'),
    ('confirm', 'confirm'),
    ('ready', 'ready'),
]


class install_all_wizard(TransientModel):
    _name = 'openupgrade.install.all.wizard'
    _description = 'OpenUpgrade Install All Wizard'
    _columns = {
        'state': fields.selection(
            STATE_SELECTION,
            'State',
            readonly=True,
        ),
        'no_localization': fields.boolean(
            string='Do not install localization modules',
            readonly=True,
            states={'init': [('readonly', False)]}
        ),
        'to_install': fields.integer(
            'Number of modules to install', readonly=True),
        }
    _defaults = {
        'state': lambda *a: 'init',
        'no_localization': True,
    }

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

    def _get_module_domain(self, no_localization):
        module_domain = [
            ('state', 'not in',
                ['installed', 'uninstallable', 'unknown']),
            ('category_id.name', '!=', 'Tests'),
            ('name', 'not in', BLACKLIST_MODULES),
        ]
        if no_localization:
            module_domain.append(('name', 'not like', 'l10n_'))
        return module_domain

    def redisplay_wizard_screen(self, cr, uid, ids, context=None):
        """Redisplay wizardscreen."""
        return {
            'name': _('Install (nearly) all modules'),
            'view_type': 'form',
            'view_mode': 'form',
            'views': [(False, 'form')],
            'res_model': self._name,
            'res_id': ids[0],
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    def confirm_install(self, cr, uid, ids, context=None):
        """Show users number of modules to be installed."""
        user_input = self.browse(cr, uid, ids, context=context)[0]
        module_obj = self.pool.get('ir.module.module')
        update, add = module_obj.update_list(cr, uid,)
        module_domain = self._get_module_domain(user_input.no_localization)
        module_count = module_obj.search_count(
            cr, uid, module_domain, context=context
        )
        if module_count:
            self.write(
                cr, uid, ids, {
                    'state': 'confirm',
                    'to_install': module_count,
                },
                context=context
            )
        else:
            self.write(
                cr, uid, ids, {
                    'state': 'ready',
                    'to_install': module_count,
                },
                context=context
            )
        return self.redisplay_wizard_screen(cr, uid, ids, context=context)

    def install_all(self, cr, uid, ids, context=None):
        """
        Main wizard step. Set all installable modules to install
        and actually install them. Exclude testing modules.
        """
        user_input = self.browse(cr, uid, ids, context=context)[0]
        module_obj = self.pool.get('ir.module.module')
        module_domain = self._get_module_domain(user_input.no_localization)
        module_ids = module_obj.search(
            cr, uid, module_domain, context=context
        )
        if module_ids:
            module_obj.write(
                cr, uid, module_ids, {'state': 'to install'}, context=context)
            cr.commit()
            _db, pool = pooler.restart_pool(cr.dbname, update_module=True)
        self.write(cr, uid, ids, {'state': 'ready'}, context)
        return self.redisplay_wizard_screen(cr, uid, ids, context=context)
