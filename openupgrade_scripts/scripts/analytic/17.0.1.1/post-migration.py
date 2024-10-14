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
    Manually create ir.property for default_applicability of account.analytic.plan
    """
    vals_list = []
    field_id = (
        env["ir.model.fields"]._get("account.analytic.plan", "default_applicability").id
    )
    env.cr.execute(
        """
        SELECT id, default_applicability, company_id FROM account_analytic_plan
        WHERE default_applicability != 'optional'
        """
    )
    for plan_id, default_applicability, company_id in env.cr.fetchall():
        vals_list.append(
            {
                "fields_id": field_id,
                "company_id": company_id,
                "res_id": "account.analytic.plan,%s" % plan_id,
                "name": "default_applicability",
                "value": default_applicability,
                "type": "selection",
            }
        )
    if vals_list:
        env["ir.property"].create(vals_list)


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.delete_records_safely_by_xml_id(
        env,
        _deleted_xml_records,
    )
    _analytic_line_create_x_plan_column(env)
    _analytic_plan_update_applicability_into_property(env)
