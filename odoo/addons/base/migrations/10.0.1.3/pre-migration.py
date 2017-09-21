# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade
from odoo.addons.openupgrade_records.lib import apriori

_column_renames = {
    'res_partner': [
        ('birthdate', None),
    ],
}


@openupgrade.migrate(use_env=False)
def migrate(cr, version):
    openupgrade.update_module_names(
        cr, apriori.renamed_modules.iteritems()
    )
    openupgrade.rename_columns(cr, _column_renames)
    cr.execute(
        # we rely on the ORM to write this value
        'alter table ir_model_fields add column store boolean'
    )
    openupgrade.copy_columns(cr, {
        'ir_act_window': [
            ('target', None, None),
        ],
    })
    openupgrade.map_values(
        cr, openupgrade.get_legacy_name('target'), 'target',
        [
            ('inlineview', 'inline'),
        ],
        table='ir_act_window')
    cr.execute(
        "update ir_ui_view set type='kanban' where type='sales_team_dashboard'"
    )
    cr.execute('update res_currency set symbol=name where symbol is null')
    # create xmlids for installed languages
    cr.execute(
        '''insert into ir_model_data
        (module, name, model, res_id)
        select
        'base',
        'lang_' ||
        case
            when char_length(code) > 2 then
            case
                when upper(substring(code from 1 for 2)) =
                upper(substring(code from 4 for 2)) then
                    substring(code from 1 for 2)
                else
                    code
            end
            else
                code
        end,
        'res.lang', id
        from res_lang''')
    openupgrade.update_module_names(
        cr, [
            ('account_full_reconcile', 'account'),
            ('mail_tip', 'mail'),
            ('project_timesheet', 'hr_timesheet'),
            ('sale_service', 'sale_timesheet'),
            ('share', 'base'),
            ('web_tip', 'web'),
            ('web_view_editor', 'web'),
            ('mail_tip', 'mail'),
            ('im_odoo_support', 'im_livechat'),
            ('marketing', 'marketing_campaign'),
            # OCA/account-invoicing
            ('purchase_stock_picking_return_invoicing_open_qty',
             'purchase_stock_picking_return_invoicing'),
            # OCA/e-commerce
            ('website_sale_b2c', 'sale'),  # used groups are in sale
            # OCA/sale-workflow
            ('sale_order_back2draft', 'sale'),
            # OCA/social
            ('mass_mailing_security_group', 'mass_mailing'),
            # OCA/web
            ('web_easy_switch_company', 'web'),
        ], merge_modules=True,
    )
