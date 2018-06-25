# -*- encoding: utf-8 -*-
# Copyright 2018 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # Fill with an standard product as it's required
    product = env.ref('product.product_product_1')
    openupgrade.logged_query(
        env.cr,
        """ 
          UPDATE TABLE purchase_requisition_line
          SET product_id = %s
          WHERE product_id IS NULL;""", (product.id,)
    )
    new_type = env['purchase.requisition.type'].search([], limit=1)
    openupgrade.logged_query(
        env.cr,
        """ 
          UPDATE TABLE purchase_requisition
          SET type_id = %s """, (new_type.id,)
    )
