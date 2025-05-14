# Copyright 2025 Tecnativa - Carlos Lopez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def _update_detailed_type_to_course(env):
    """
    Adapt all products using into a course to the new detailed_type=course
    """
    openupgrade.logged_query(
        env.cr,
        """UPDATE product_template pt
            SET detailed_type = 'course'
        FROM product_product pp
            JOIN slide_channel sc ON sc.product_id = pp.id
        WHERE pp.product_tmpl_id = pt.id;
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    _update_detailed_type_to_course(env)
