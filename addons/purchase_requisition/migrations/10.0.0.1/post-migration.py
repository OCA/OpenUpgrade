# -*- coding: utf-8 -*-
# Copyright 2018 Tecnativa - Vicent Cubells
# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def fill_product(env):
    """Fill with an pre-created product as it's required."""
    product = env['product.product'].create({
        'active': False,
        'name': 'OU purchase requisition line wildcard',
    })
    openupgrade.logged_query(
        env.cr, """
        UPDATE purchase_requisition_line
        SET product_id = %s
        WHERE product_id IS NULL;""", (product.id, ),
    )


@openupgrade.migrate()
def migrate(env, version):
    fill_product(env)
    openupgrade.set_defaults(
        env.cr, env, {'purchase.requisition': [('type_id', None)]},
        use_orm=True,
    )
