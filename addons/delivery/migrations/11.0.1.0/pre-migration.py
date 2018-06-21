# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def migrate_delivery_carrier(cr):
    """ delivery_carrier is no more an _inherits of product.product

    Thus we copy field values from related product.template and product.product
    for fields which were transfered to delivery.carrier
    """
    table = 'delivery_carrier'
    # Create column
    for column_name, column_type in [('name', 'VARCHAR'), ('active', 'BOOLEAN')]:
        if not openupgrade.column_exists(cr, table, column_name):
            query = (
                "ALTER TABLE delivery_carrier ADD COLUMN %s %s"
            ) % (column_name, column_type)
            openupgrade.logged_query(cr, query, [])
    query = ("UPDATE delivery_carrier"
             " SET active = product_product.active,"
             "     name = product_template.name"
             " FROM product_product INNER JOIN product_template"
             " ON product_product.product_tmpl_id = product_template.id"
             " WHERE product_product.id = delivery_carrier.product_id")
    openupgrade.logged_query(cr, query, [])


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    migrate_delivery_carrier(env.cr)
