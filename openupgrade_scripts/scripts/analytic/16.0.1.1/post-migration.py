from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.delete_records_safely_by_xml_id(
        env, ["analytic.analytic_tag_comp_rule", "analytic.analytic_group_comp_rule"]
    )
    # Define the appropriate value for the root_plan_id field. Necessary for accounts
    # that previously had an account.analytic.group defined.
    accounts = env["account.analytic.account"].search([("root_plan_id", "=", False)])
    accounts._compute_root_plan()
