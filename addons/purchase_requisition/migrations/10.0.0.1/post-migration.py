# -*- coding: utf-8 -*-
# Copyright 2018 Tecnativa - Vicent Cubells
# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def fill_product(env):
    """Fill with an pre-created product as it's required."""
    if env['purchase.requisition.line'].search_count(
            [('product_id', '=', False)]) > 0:
        categ_id = env["product.template"]._get_default_category_id()
        if not categ_id:
            categ_id = env["product.category"].search(
                [], limit=1, order='id asc').id
        product = env['product.product'].create({
            'active': False,
            'categ_id': categ_id,  # categ_id is required
            'company_id': False,  # tacke into account multi-company context
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
