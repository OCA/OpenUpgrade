# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - Pedro M. Baeza
# Copyright 2018 - Nicolas JEUDY
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

_xmlid_renames = [
    ('account.group_proforma_invoices', 'sale.group_proforma_sales'),
]

# It comes from the renaming of website_portal_sale > sale_payment
_portal_xmlid_renames = [
    ('sale_payment.portal_my_home_menu_sale', 'sale.portal_my_home_menu_sale'),
    ('sale_payment.portal_my_home_sale', 'sale.portal_my_home_sale'),
    ('sale_payment.portal_my_quotations', 'sale.portal_my_quotations'),
    ('sale_payment.portal_my_orders', 'sale.portal_my_orders'),
]


def update_field_module(cr):
    """Rename references for moved fields"""
    new_name = 'sale_stock'
    old_name = 'sale'
    # get moved model fields
    moved_fields = tuple(['procurement_group_id'])
    cr.execute(
        """
        SELECT id
        FROM ir_model_fields
        WHERE model = 'sale.order' AND name in %s
        """, (moved_fields,))
    field_ids = tuple([r[0] for r in cr.fetchall()])
    # update ir_model_data, the subselect allows to avoid duplicated XML-IDs
    query = ("UPDATE ir_model_data SET module = %s "
             "WHERE module = %s AND res_id IN %s AND name NOT IN "
             "(SELECT name FROM ir_model_data WHERE module = %s)")
    openupgrade.logged_query(
        cr, query, (new_name, old_name, field_ids, new_name)
    )
    # update ir_translation
    query = ("UPDATE ir_translation SET module = %s "
             "WHERE module = %s AND res_id IN %s")
    openupgrade.logged_query(cr, query, (new_name, old_name, field_ids))


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_xmlids(env.cr, _xmlid_renames)
    openupgrade.rename_xmlids(env.cr, _portal_xmlid_renames)
    try:
        with env.cr.savepoint():
            env.ref('sale_payment.orders_followup').unlink()
    except Exception:
        pass
    update_field_module(env.cr)
