# Copyright 2019 Eficent <http://www.eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade
from psycopg2.extensions import AsIs


def fill_sale_order_template_requires(cr):
    openupgrade.logged_query(
        cr, """
        UPDATE sale_order_template
        SET require_signature = TRUE
        WHERE %s = 0
        """, (AsIs(openupgrade.get_legacy_name('require_payment')), ),
    )
    openupgrade.logged_query(
        cr, """
        UPDATE sale_order_template
        SET require_payment = TRUE
        WHERE %s = 1
        """, (AsIs(openupgrade.get_legacy_name('require_payment')), ),
    )


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    if openupgrade.column_exists(
            cr, 'sale_order_template',
            openupgrade.get_legacy_name('require_payment')):
        fill_sale_order_template_requires(cr)
    openupgrade.load_data(
        env.cr, 'sale_management', 'migrations/12.0.1.0/noupdate_changes.xml')
