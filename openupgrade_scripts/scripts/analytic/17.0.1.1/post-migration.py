# Copyright 2024 Viindoo Technology Joint Stock Company (Viindoo)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_deleted_xml_records = ["analytic.analytic_plan_comp_rule"]


def _analytic_line_create_x_plan_column(env):
    """
    This method set system parameter for project analytic plan
    and create dynamic field on analytic items using
    '_sync_plan_column' method
    """
    project_plan = (
        env.ref("analytic.analytic_plan_projects", raise_if_not_found=False)
        or env["account.analytic.plan"]
    )
    if project_plan:
        env["ir.config_parameter"].set_param(
            "analytic.project_plan", str(project_plan.id)
        )
    plans_to_create_fields = env["account.analytic.plan"].search([])
    (plans_to_create_fields - project_plan)._sync_plan_column()
    for plan in plans_to_create_fields - project_plan:
        if plan.parent_id:
            continue
        column = plan._strict_column_name()
        openupgrade.logged_query(
            env.cr,
            f"""
            UPDATE account_analytic_line
            SET {column} = account_id,
                account_id = NULL
            WHERE plan_id = {plan.id};
            """,
        )


def _analytic_plan_update_applicability_into_property(env):
    """
    Create ir.property for default_applicability of account.analytic.plan
    in all companies as the company_id field was shifted from account.analytic.plan
    to account.analytic.applicability
    """
    env.cr.execute(
        """
        SELECT id, default_applicability FROM account_analytic_plan
        WHERE default_applicability != 'optional'
        """
    )
    values = dict(env.cr.fetchall())
    for company in env["res.company"].search([]):
        env["ir.property"].with_company(company)._set_multi(
            "default_applicability",
            "account.analytic.plan",
            values,
        )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.delete_records_safely_by_xml_id(
        env,
        _deleted_xml_records,
    )
    _analytic_line_create_x_plan_column(env)
    _analytic_plan_update_applicability_into_property(env)
