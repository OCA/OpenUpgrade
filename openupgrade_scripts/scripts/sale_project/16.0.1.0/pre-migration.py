from openupgradelib import openupgrade


def _move_fields(env):
    openupgrade.update_module_moved_fields(
        env.cr, "product.product", ["service_policy"], "sale_timesheet", "sale"
    )
    openupgrade.update_module_moved_fields(
        env.cr, "product.template", ["service_policy"], "sale_timesheet", "sale"
    )
    openupgrade.update_module_moved_fields(
        env.cr, "project.project", ["allow_billable"], "sale_timesheet", "sale"
    )
    openupgrade.update_module_moved_fields(
        env.cr, "project.project", ["invoice_count"], "account_sale_timesheet", "sale"
    )
    openupgrade.update_module_moved_fields(
        env.cr, "project.project", ["vendor_bill_count"], "sale_project_account", "sale"
    )


@openupgrade.migrate()
def migrate(env, version):
    _move_fields(env)
