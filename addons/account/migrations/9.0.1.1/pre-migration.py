# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenUpgrade module for Odoo
#    @copyright 2014-Today: Odoo Community Association
#    @author: Sylvain LE GAL <https://twitter.com/legalsylvain>
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

from openupgradelib import openupgrade


PROPERTY_FIELDS = {
    ('product.category', 'property_account_expense_categ', 'property_account_expense_categ_id'),
    ('product.category', 'property_account_income_categ', 'property_account_income_categ_id'),
    ('res.partner', 'property_account_payable', 'property_account_payable_id'),
    ('res.partner', 'property_account_receivable', 'property_account_receivable_id'),
}


def migrate_properties(cr):
    for model, name_v8, name_v9 in PROPERTY_FIELDS:
        openupgrade.logged_query(cr, """
            update ir_model_fields
            set name = '{name_v9}'
            where name = '{name_v8}'
            and model = '{model}'
            """.format(model=model, name_v8=name_v8, name_v9=name_v9))
        openupgrade.logged_query(cr, """
            update ir_property
            set name = '{name_v9}'
            where name = '{name_v8}'
            """.format(name_v8=name_v8, name_v9=name_v9))


@openupgrade.migrate()
def migrate(cr, version):
    openupgrade.rename_tables(cr, [('account_tax_code', 'account_tax_group')])
    migrate_properties(cr)
    cr.execute("""
        delete from ir_ui_view v
        using ir_model_data d where
        v.id=d.res_id and d.model='ir.ui.view' and
        d.module='sales_team' and
        d.name='view_sale_config_settings'
        """)
