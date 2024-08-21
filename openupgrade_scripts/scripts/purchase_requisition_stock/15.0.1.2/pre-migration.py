# Copyright 2024 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    """The module purchase_requisition_grouped_by_procurement previously added
    group_id column in previous version. Now procurement_group_id field exists."""
    if openupgrade.is_module_installed(
        env.cr, "purchase_requisition_grouped_by_procurement"
    ):
        openupgrade.rename_fields(
            env,
            [
                (
                    "purchase.requisition",
                    "purchase_requisition",
                    "group_id",
                    "procurement_group_id",
                ),
            ],
        )
