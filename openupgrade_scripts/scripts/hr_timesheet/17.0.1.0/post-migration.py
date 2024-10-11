from collections import defaultdict

from openupgradelib import openupgrade


def _project_update_fill_timesheet(env):
    updates = env["project.update"].with_context(active_test=False).search([])
    timesheets_read_group = env["account.analytic.line"]._read_group(
        [
            (
                "project_id",
                "in",
                env["project.project"].with_context(active_test=False).search([]).ids,
            )
        ],
        ["project_id", "product_uom_id", "date:day"],
        ["unit_amount:sum"],
    )
    timesheet_time_dict = defaultdict(list)
    for project, product_uom, date, unit_amount_sum in timesheets_read_group:
        timesheet_time_dict[project.id].append((product_uom, date, unit_amount_sum))
    for update in updates:
        project = update.project_id
        encode_uom = project.company_id.timesheet_encode_uom_id
        if not encode_uom:
            continue

        total_time = 0.0
        for product_uom, date, unit_amount in timesheet_time_dict[project.id]:
            if date > update.date:
                continue
            factor = (product_uom or project.timesheet_encode_uom_id).factor_inv
            total_time += unit_amount * (1.0 if project.encode_uom_in_days else factor)
        total_time *= project.timesheet_encode_uom_id.factor

        ratio = env.ref("uom.product_uom_hour").ratio / encode_uom.ratio
        update.write(
            {
                "uom_id": encode_uom,
                "allocated_time": round(project.allocated_hours / ratio),
                "timesheet_time": round(total_time / ratio),
            }
        )


@openupgrade.migrate()
def migrate(env, version):
    _project_update_fill_timesheet(env)
