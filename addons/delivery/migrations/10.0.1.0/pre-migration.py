# -*- coding: utf-8 -*-
# © 2017 bloopark systems (<http://bloopark.de>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


# backup of partner_id and shipping_enabled columns in table delivery_carrier
# because they don't exist anymore in odoo 10
column_renames = {
    'delivery_carrier': [
        ('partner_id', None),
        ('shipping_enabled', None),
    ],
}


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    openupgrade.rename_columns(env.cr, column_renames)
