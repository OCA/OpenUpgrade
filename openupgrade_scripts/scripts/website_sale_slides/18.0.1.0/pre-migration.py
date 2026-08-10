# Copyright 2026 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

_columns_copy = {
    "product_template": [("service_tracking", None, None)],
}


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.copy_columns(env.cr, _columns_copy)
    openupgrade.map_values(
        env.cr,
        "detailed_type",
        "service_tracking",
        [("course", "course")],
        table="product_template",
    )
