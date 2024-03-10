from openupgradelib import openupgrade


def _update_account_analytic_line_timesheet_invoice_type(env):
    openupgrade.logged_query(
        env.cr,
        """
        WITH timesheet_info as (
            SELECT aal.id as id,
                   product_tmpl.service_type as service_type
            FROM account_analytic_line aal
            JOIN sale_order_line sol
             ON sol.id = aal.so_line
            JOIN product_product product
             ON product.id = sol.product_id
            JOIN product_template product_tmpl
             ON product_tmpl.id = product.product_tmpl_id
            WHERE product_tmpl.type = 'service'
                  AND product_tmpl.invoice_policy = 'delivery'
                  AND product_tmpl.service_type IN ('milestones', 'manual')
        )
        UPDATE account_analytic_line aal
        SET timesheet_invoice_type = CONCAT('billable_', info.service_type)
        FROM timesheet_info info
        WHERE aal.id = info.id
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    _update_account_analytic_line_timesheet_invoice_type(env)
    # Remove SQL view project_profitability_report not used anymore in Odoo 16
    openupgrade.logged_query(
        env.cr, "DROP VIEW IF EXISTS project_profitability_report CASCADE"
    )
