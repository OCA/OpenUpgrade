# Copyright 2020 Payam Yasaie <https://www.tashilgostar.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_field_renames = [
    ('pos.category', 'pos_category', 'image', 'image_128'),
]

_xmlid_renames = [
    # ir.actions.report
    ('point_of_sale.action_report_account_statement', 'account.action_report_account_statement'),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_fields(env, _field_renames)
    openupgrade.rename_xmlids(env.cr, _xmlid_renames)
    # Fix image of pos.category after renaming column to image_128
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE ir_attachment
        SET res_field = 'image_128'
        WHERE res_field = 'image' and res_model = 'pos.category'
        """,
    )
