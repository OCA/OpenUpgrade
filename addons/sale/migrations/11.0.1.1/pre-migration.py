# -*- coding: utf-8 -*-
# Copyright 2018 - Nicolas JEUDY
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

_xmlid_renames = [
    ('account.group_proforma_invoices', 'sale.group_proforma_sales'),
]

_portal_xmlid_renames = [
    ('website_portal_sale.portal_my_home_menu_sale',
     'sale.portal_my_home_menu_sale'),
    ('website_portal_sale.portal_my_home_sale',
     'sale.portal_my_home_sale'),
    ('website_portal_sale.portal_my_quotations', 'sale.portal_my_quotations'),
    ('website_portal_sale.portal_my_orders', 'sale.portal_my_orders'),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_xmlids(env.cr, _xmlid_renames)
    openupgrade.rename_xmlids(env.cr, _portal_xmlid_renames)
    try:
        with env.cr.savepoint():
            env.ref('website_portal_sale.orders_followup').unlink()
    except Exception:
        pass


