# -*- coding: utf-8 -*-
# Copyright 2018 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.update_module_moved_fields(
        env.cr, 'payment.transaction', [
            'sale_order_id',
        ],
        'website_quote', 'website_portal_sale',
    )
