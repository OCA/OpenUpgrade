# Copyright 2024 Viindoo Technology Joint Stock Company (Viindoo)
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
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_analytic_applicability t1
        SET company_id = t2.company_id
        FROM account_analytic_plan t2
        WHERE t1.analytic_plan_id = t2.id
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
