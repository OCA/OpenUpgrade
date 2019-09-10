# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_xmlids(env.cr, [
        ('stock_dropshipping.procurement_rule_drop_shipping',
         'stock_dropshipping.stock_rule_drop_shipping'),
    ])
