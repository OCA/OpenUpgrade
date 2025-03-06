# Copyright 2024 Viindoo Technology Joint Stock Company (Viindoo)
# Copyright 2024 Hunki enterprises - Holger Brunn
# Copyright 2024 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _fill_config_parameter_analytic_project_plan(env):
    env["ir.config_parameter"].set_param("analytic.project_plan", "1")


def _analytic_applicability_fill_company_id(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE account_analytic_applicability
        ADD COLUMN IF NOT EXISTS company_id INTEGER;
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    _fill_config_parameter_analytic_project_plan(env)
    _analytic_applicability_fill_company_id(env)
    # Drop triagram index on name column of account.analytic.account
    # to avoid error when loading registry, it will be recreated
    openupgrade.logged_query(
        env.cr,
        """
        DROP INDEX IF EXISTS account_analytic_account_name_index;
        """,
    )
    # Save company_id field of analytic plans for modules reinstating this
    # to pick up
    openupgrade.copy_columns(
        env.cr, {"account_analytic_plan": [("company_id", None, None)]}
    )
