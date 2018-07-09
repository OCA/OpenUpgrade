# Copyright 2017-2019 Tecnativa - Pedro M. Baeza
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

# It comes from the renaming of portal_sale > sale
_portal_sale_xmlid_renames = [
    ('sale.portal_sale_order_user_rule', 'sale.sale_order_rule_portal'),
    ('sale.portal_sale_order_line_rule', 'sale.sale_order_line_rule_portal'),
]

COLUMN_COPIES = {
    'product_template': [
        ('track_service', None, None),
    ],
}


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.copy_columns(env.cr, COLUMN_COPIES)
    openupgrade.rename_xmlids(env.cr, _xmlid_renames)
    openupgrade.rename_xmlids(env.cr, _portal_xmlid_renames)
    openupgrade.rename_xmlids(env.cr, _portal_sale_xmlid_renames)
    xml_ids_to_remove = [
        'sale_payment.orders_followup',
        'sale.portal_personal_contact',
    ]
    for xml_id in xml_ids_to_remove:
        try:
            with env.cr.savepoint():
                env.ref(xml_id).unlink()
        except Exception:
            pass
    openupgrade.update_module_moved_fields(
        env.cr, 'sale.order', ['procurement_group_id'], 'sale', 'sale_stock',
    )
    openupgrade.add_fields(
        env, [
            ('amt_invoiced', 'sale.order.line', 'sale_order_line', 'monetary',
             False, 'sale'),
            ('amt_to_invoice', 'sale.order.line', 'sale_order_line',
             'monetary', False, 'sale'),
        ]
    )
