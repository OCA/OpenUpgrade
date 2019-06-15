# Copyright 2019 Eficent <http://www.eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def update_product_template_attribute_value(env):
    # in v12, for each relation of the product.attribute.value and
    # product.template.attribute.line, a product.template.attribute.value
    # should exist. Thus, we determine which lines still doesn't have a
    # product.template.attribute.value and then we generate them.
    openupgrade.logged_query(
        env.cr, """
        SELECT rel.product_attribute_value_id, ptal.product_tmpl_id
        FROM product_template_attribute_line ptal
        JOIN product_attribute_value_product_template_attribute_line_rel
            rel ON rel.product_template_attribute_line_id = ptal.id
        LEFT JOIN product_template_attribute_value ptav ON (
            rel.product_attribute_value_id = ptav.product_attribute_value_id
            AND ptal.product_tmpl_id = ptav.product_tmpl_id)
        WHERE ptav.id IS NULL
        """
    )
    env['product.template.attribute.value'].create([{
        'product_attribute_value_id': x[0],
        'product_tmpl_id': x[1],
    } for x in env.cr.fetchall()])


@openupgrade.migrate()
def migrate(env, version):
    update_product_template_attribute_value(env)
