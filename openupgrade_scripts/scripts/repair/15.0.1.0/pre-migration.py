# Copyright 2025 Tecnativa - Carlos Lopez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.convert_field_to_html(
        env.cr, "repair_order", "internal_notes", "internal_notes"
    )
    openupgrade.convert_field_to_html(
        env.cr, "repair_order", "quotation_notes", "quotation_notes"
    )
    openupgrade.copy_columns(
        env.cr,
        {"repair_order": [("state", None, None)]},
    )
