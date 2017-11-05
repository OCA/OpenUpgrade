# -*- coding: utf-8 -*-
# Copyright 2017 Therp BV
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


field_renames = [
    # renamings with oldname attribute - They also need the rest of operations
    ('product.attribute.value', 'product_attribute_value', 'color',
     'html_color'),
]


@openupgrade.migrate()
def migrate(env, version):
    # keeping info in website pricelist table that would be dropped
    sql = """create table website_pricelist_openupgrade_10 as select * from
        website_pricelist"""
    env.cr.execute(sql)
    openupgrade.rename_fields(env, field_renames)
