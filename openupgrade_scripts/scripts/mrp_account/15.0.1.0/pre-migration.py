# Copyright 2023 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


def pre_create_mrp_production_analytic_account_id(env):
    """Pre-create the column for avoiding computation on module upgrade"""
    if openupgrade.column_exists(env.cr, "mrp_production", "analytic_account_id"):
        return
    openupgrade.add_fields(
        env,
        [
            (
                "analytic_account_id",
                "mrp.production",
                "mrp_production",
                "many2one",
                False,
                "mrp_account",
            )
        ],
    )


@openupgrade.migrate()
def migrate(env, version):
    pre_create_mrp_production_analytic_account_id(env)
