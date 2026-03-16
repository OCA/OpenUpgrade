# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

_added_fields = [
    (
        "product_uom_id",
        "mrp.workcenter.capacity",
        "mrp_workcenter_capacity",
        "many2one",
        None,
        "mrp",
    )
]

_renamed_field_references = [
    (
        "mrp.production",
        "lot_producing_id",
        "lot_producing_ids",
    ),
    (
        "mrp.production",
        "procurement_group_id",
        "reference_ids",
    ),
]

_copied_columns = {
    "mrp_workorder": [
        ("state", None, None),
    ]
}


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.add_fields(env, _added_fields)
    openupgrade.rename_field_references(env, _renamed_field_references)
    openupgrade.copy_columns(env.cr, _copied_columns)
