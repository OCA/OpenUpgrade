# Copyright 2025 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

_column_renames = {
    "website_controller_page": [("page_name", "name")],
}

_new_columns = [
    ("website.controller.page", "record_view_id", "many2one"),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_columns(env.cr, _column_renames)
    openupgrade.add_columns(env, _new_columns)
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE website_controller_page
        SET record_view_id = view_id
        WHERE page_type = 'single'""",
    )
    openupgrade.cow_templates_mark_if_equal_to_upstream(env.cr)
