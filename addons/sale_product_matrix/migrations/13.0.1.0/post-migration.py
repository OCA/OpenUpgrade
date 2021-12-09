# Copyright 2021 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def set_product_template_matrix_add_mode(env):
    """
    sale_order_variant_mgmt allows to choose only product_templates
    that have 2 attribute_line_ids, so we will set as
    product_add_mode='matrix' the products that accomplish the above condition.
    """
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE product_template pt
        SET product_add_mode = 'matrix'
        WHERE 2 = (
            SELECT COUNT(*)
            FROM product_template_attribute_line ptal
            WHERE ptal.product_tmpl_id = pt.id
        )
        """
    )


@openupgrade.migrate()
def migrate(env, version):
    set_product_template_matrix_add_mode(env)
