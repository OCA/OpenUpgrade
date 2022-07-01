from openupgradelib import openupgrade


def _fast_fill_account_analytic_line_order_id(env):

    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE account_analytic_line
        ADD COLUMN IF NOT EXISTS order_id integer
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
            UPDATE account_analytic_line aal
            SET order_id = sol.order_id
            FROM sale_order_line sol
            WHERE aal.so_line IS NOT NULL AND aal.so_line = sol.id
            """,
    )


def _fast_fill_project_sale_line_employee_map_is_cost_changed(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE project_sale_line_employee_map
        ADD COLUMN IF NOT EXISTS is_cost_changed boolean
        """,
    )
    # 1. Set is_cost_changed = False when employee_id IS NULL
    openupgrade.logged_query(
        env.cr,
        """
            UPDATE project_sale_line_employee_map
            SET is_cost_changed = CASE
                WHEN employee_id IS NULL THEN false
                ELSE true
                END
            WHERE is_cost_changed IS NULL
            """,
    )


def _fast_fill_project_sale_line_employee_map_cost(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE project_sale_line_employee_map
        ADD COLUMN IF NOT EXISTS cost numeric
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
            UPDATE project_sale_line_employee_map
            SET cost = 0
            WHERE is_cost_changed = false AND employee_id IS NULL
            """,
    )
    openupgrade.logged_query(
        env.cr,
        """
            UPDATE project_sale_line_employee_map emp_map
            SET cost = emp.timesheet_cost
            FROM hr_employee emp
            WHERE emp_map.is_cost_changed = false AND emp_map.employee_id IS NOT NULL
                AND emp_map.employee_id = emp.id
            """,
    )


def _fill_project_task_analytic_account_id(env):
    openupgrade.logged_query(
        env.cr,
        """
            UPDATE project_task task
            SET analytic_account_id = so.analytic_account_id
            FROM sale_order so
            WHERE task.sale_order_id = so.id AND task.sale_order_id IS NOT NULL
                AND task.analytic_account_id IS NULL
            """,
    )


def _re_fill_account_analytic_line_timesheet_invoice_type(env):
    openupgrade.logged_query(
        env.cr,
        """
        WITH aal_tmp AS (
            SELECT aal.id AS aal_id,
                CASE
                    WHEN product IS NOT NULL
                        AND tmpl.type = 'service' THEN 'service_revenues'
                    WHEN aal.amount >=0 THEN 'other_revenues' ELSE 'other_costs' END
                AS timesheet_invoice_type
            FROM account_analytic_line aal
            LEFT JOIN sale_order_line so_line ON aal.so_line = so_line.id
            LEFT JOIN product_product product ON so_line.product_id = product.id
            LEFT JOIN product_template tmpl ON tmpl.id = product.product_tmpl_id
            WHERE aal.project_id IS NULL
        )
        UPDATE account_analytic_line aal
        SET timesheet_invoice_type = aal_tmp.timesheet_invoice_type
        FROM aal_tmp WHERE aal_tmp.aal_id = aal.id
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        WITH aal_tmp AS (
            SELECT aal.id AS aal_id,
            CASE
            WHEN so_line IS NOT NULL AND product IS NOT NULL
                AND tmpl.type = 'service' AND tmpl.invoice_policy = 'order'
                THEN 'billable_fixed'
            WHEN so_line IS NOT NULL AND product IS NOT NULL
                AND tmpl.type = 'service' AND tmpl.invoice_policy = 'delivery'
                AND tmpl.service_type = 'timesheet' AND aal.amount > 0
                THEN 'timesheet_revenues'
            WHEN so_line IS NOT NULL AND product IS NOT NULL
                AND tmpl.type = 'service' AND tmpl.invoice_policy = 'delivery'
                AND tmpl.service_type = 'timesheet' AND aal.amount <= 0
                THEN 'billable_time'
            WHEN so_line IS NOT NULL AND product IS NOT NULL
                AND tmpl.type = 'service' AND tmpl.invoice_policy = 'delivery'
                AND tmpl.service_type != 'timesheet'
                THEN 'billable_fixed'
            WHEN so_line IS NOT NULL AND product IS NOT NULL
                AND tmpl.type = 'service' AND tmpl.invoice_policy = 'order'
                THEN 'billable_fixed'
            WHEN so_line IS NULL OR (product IS NOT NULL AND tmpl.type != 'service')
                THEN 'non_billable'
            END
            AS timesheet_invoice_type
        FROM account_analytic_line aal
        LEFT JOIN sale_order_line so_line ON aal.so_line = so_line.id
        LEFT JOIN product_product product ON so_line.product_id = product.id
        LEFT JOIN product_template tmpl ON tmpl.id = product.product_tmpl_id
        WHERE aal.project_id IS NOT NULL AND aal.timesheet_invoice_type IS NULL
        )
        UPDATE account_analytic_line aal
        SET timesheet_invoice_type = aal_tmp.timesheet_invoice_type
        FROM aal_tmp WHERE aal_tmp.aal_id = aal.id
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    _fast_fill_account_analytic_line_order_id(env)
    _fast_fill_project_sale_line_employee_map_is_cost_changed(env)
    _fast_fill_project_sale_line_employee_map_cost(env)
    _fill_project_task_analytic_account_id(env)
    _re_fill_account_analytic_line_timesheet_invoice_type(env)
