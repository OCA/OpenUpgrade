# Copyright 2023 Coop IT Easy
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

_field_renames = [
    ("product.supplierinfo", "product_supplierinfo", "name", "partner_id"),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_fields(env, _field_renames)
    # restricting inherited views to groups isn't allowed any more
    env.cr.execute(
        "DELETE FROM ir_ui_view_group_rel r "
        "USING ir_ui_view v "
        "WHERE r.view_id=v.id AND v.inherit_id IS NOT NULL AND v.mode != 'primary'"
    )
