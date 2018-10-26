# -*- coding: utf-8 -*-
# © 2017 bloopark systems (<http://bloopark.de>)
# Copyright 2018 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_xmlid_renames = [
    ('sale.group_display_incoterm', 'sale_stock.group_display_incoterm'),
]


def activate_proforma(env):
    """If module `sale_proforma_report` (OCA/sale-reporting) was installed we
    need to activate the "Pro-forma Invoices" setting as the module was
    deprecated in favour of it."""
    if openupgrade.column_exists(env.cr, 'sale_order', 'proforma'):
        employee_group = env.ref('base.module_category_human_resources')
        proforma_group = env.ref('sale.group_proforma_sales')
        employee_group.write({'implied_ids': [(4, proforma_group.id)]})


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_xmlids(env.cr, _xmlid_renames)
    openupgrade.load_data(
        env.cr, 'sale', 'migrations/11.0.1.1/noupdate_changes.xml',
    )
    activate_proforma(env)
