# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_column_renames = {
    'res_partner': [
        ('birthdate', None),
    ],
}


@openupgrade.migrate(use_env=False)
def migrate(cr, version):
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
            ('share', 'base'),
            ('web_tip', 'web'),
            ('web_view_editor', 'web'),
            ('mail_tip', 'mail'),
            ('im_odoo_support', 'im_livechat'),
            # OCA/sale-workflow
            ('sale_order_back2draft', 'sale'),
        ], merge_modules=True,
    )
