# Copyright 2019 Eficent <http://www.eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade, openupgrade_120
from psycopg2.extensions import AsIs


def map_sale_order_require_payment(cr):
    # cannot use map_values method because it cannot map from a boolean
    openupgrade.logged_query(
        cr, """UPDATE sale_order
        SET require_payment = TRUE
        WHERE %s = 1
        """, (AsIs(openupgrade.get_legacy_name('require_payment')), ),
    )
    openupgrade.logged_query(
        cr, """UPDATE sale_order
        SET require_payment = FALSE
        WHERE %s = 0
        """, (AsIs(openupgrade.get_legacy_name('require_payment')), ),
    )


def map_sale_order_template_require_payment(cr):
    # cannot use map_values method because it cannot map from a boolean
    openupgrade.logged_query(
        cr, """UPDATE sale_order_template
        SET require_payment = TRUE
        WHERE %s = 1
        """, (AsIs(openupgrade.get_legacy_name('require_payment')), ),
    )
    openupgrade.logged_query(
        cr, """UPDATE sale_order_template
        SET require_payment = FALSE
        WHERE %s = 0
        """, (AsIs(openupgrade.get_legacy_name('require_payment')), ),
    )


def set_group_sale_order_template(cr):
    cr.execute(
        """SELECT res_id FROM ir_model_data WHERE module = 'base'
        AND model = 'res.groups' AND name = 'group_user'""")
    user_group_id = cr.fetchone()[0]
    cr.execute(
        """SELECT res_id FROM ir_model_data WHERE module = 'sale_management'
        AND model = 'res.groups' AND name = 'group_sale_order_template'""")
    sale_order_template_group_id = cr.fetchone()[0]
    cr.execute(
        """
        INSERT INTO res_groups_implied_rel (gid, hid)
        VALUES (%s, %s)
    """, (user_group_id, sale_order_template_group_id),
    )


@openupgrade.migrate()
def migrate(env, version):
    map_sale_order_require_payment(env.cr)
    map_sale_order_template_require_payment(env.cr)
    set_group_sale_order_template(env.cr)
    openupgrade.load_data(
        env.cr, 'sale_quotation_builder',
        'migrations/12.0.1.0/noupdate_changes.xml')
    openupgrade.delete_records_safely_by_xml_id(
        env, [
            'sale_quotation_builder.confirmation_mail',
        ],
    )
    openupgrade_120.convert_field_bootstrap_3to4(
        env, 'product.template', 'quotation_only_description',
    )
    openupgrade_120.convert_field_bootstrap_3to4(
        env, 'sale.order', 'website_description',
    )
    openupgrade_120.convert_field_bootstrap_3to4(
        env, 'sale.order.line', 'website_description',
    )
    openupgrade_120.convert_field_bootstrap_3to4(
        env, 'sale.order.option', 'website_description',
    )
    openupgrade_120.convert_field_bootstrap_3to4(
        env, 'sale.order.template', 'website_description',
    )
    openupgrade_120.convert_field_bootstrap_3to4(
        env, 'sale.order.template.line', 'website_description',
    )
    openupgrade_120.convert_field_bootstrap_3to4(
        env, 'sale.order.template.option', 'website_description',
    )
