# Copyright 2018 Eficent <http://www.eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def map_product_attribute_create_variant(cr):
    # cannot use map_values method because it cannot map from a boolean
    cr.execute(
        """
        UPDATE product_attribute
        SET create_variant = 'always'
        WHERE create_variant = TRUE
        """
    )
    cr.execute(
        """
        UPDATE product_attribute
        SET create_variant = 'no_variant'
        WHERE create_variant != 'always'
        """
    )


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    env['product.category']._parent_store_compute()
    map_product_attribute_create_variant(env.cr)
