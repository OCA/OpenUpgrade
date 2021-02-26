# Copyright 2020 Payam Yasaie <https://www.tashilgostar.com>
# Copyright 2021 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_field_renames = [
    ('product.template', 'product_template', 'product_image_ids', 'product_template_image_ids'),
]


def invert_website_sequence(env):
    """In v12, the e-commerce controller gives a default order with a descending
    sequence, but now in v13, the sequence field is used as ascending, so we
    need to invert existing data for preserving the previous order.
    """
    openupgrade.logged_query(
        env.cr, """
        UPDATE product_template pt
        SET website_sequence = sub.rank
        FROM (
            SELECT id, rank() OVER (
                ORDER BY website_sequence desc, id desc
            ) FROM product_template
        ) sub
        WHERE sub.id = pt.id"""
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_fields(env, _field_renames)
    invert_website_sequence(env)
