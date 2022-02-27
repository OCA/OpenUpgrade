from openupgradelib import openupgrade

_xmlid_renames_sale_project = [
    (
        "sale_timesheet.access_sale_order_line_project_manager",
        "sale_project.access_sale_order_line_project_manager",
    ),
    (
        "sale_timesheet.access_sale_order_project_manager",
        "sale_project.access_sale_order_project_manager",
    ),
    (
        "sale_timesheet.constraint_project_project_sale_order_required_if_sale_line",
        "sale_project.constraint_project_project_sale_order_required_if_sale_line",
    ),
    (
        "sale_timesheet.sale_order_line_rule_project_manager",
        "sale_project.sale_order_line_rule_project_manager",
    ),
]


@openupgrade.migrate(no_version=True)
def migrate(env, version):
    openupgrade.rename_xmlids(env.cr, _xmlid_renames_sale_project)
