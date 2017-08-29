# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

_column_renames = {
    'crm_team': [
        ('code', None),
        ('working_hours', None),
    ],
}

_xmlid_renames = [
    ('base.group_sale_manager', 'sales_team.group_sale_manager'),
    ('base.group_sale_salesman', 'sales_team.group_sale_salesman'),
    ('base.group_sale_salesman_all_leads',
     'sales_team.group_sale_salesman_all_leads'),
    ('website.salesteam_website_sales', 'sales_team.salesteam_website_sales'),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_columns(env.cr, _column_renames)
    openupgrade.rename_xmlids(env.cr, _xmlid_renames)
