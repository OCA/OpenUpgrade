# Copyright 2018 Eficent <http://www.eficent.com>
# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade
from psycopg2.extensions import AsIs


def map_product_attribute_create_variant(cr):
    # cannot use map_values method because it cannot map from a boolean
    openupgrade.logged_query(
        cr, """UPDATE product_attribute
        SET create_variant = 'always'
        WHERE %s
        """, (AsIs(openupgrade.get_legacy_name('create_variant')), ),
    )
    openupgrade.logged_query(
        cr, """UPDATE product_attribute
        SET create_variant = 'no_variant'
        WHERE NOT %s
        """, (AsIs(openupgrade.get_legacy_name('create_variant')), ),
    )


@openupgrade.migrate()
def migrate(env, version):
    env['product.category']._parent_store_compute()
    map_product_attribute_create_variant(env.cr)
