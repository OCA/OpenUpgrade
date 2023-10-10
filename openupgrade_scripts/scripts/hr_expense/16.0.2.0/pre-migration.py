from openupgradelib import openupgrade


def _hr_expense_table_new_columns(env):
    """Custom process to create new columns:
    - amount_tax: (total_amount - untaxed_amount).
    - amount_tax_company: set 0 value to re-set in post-migration."""
    # amount_tax
    if not openupgrade.column_exists(env.cr, "hr_expense", "amount_tax"):
        openupgrade.logged_query(
            env.cr,
            """
            ALTER TABLE hr_expense
            ADD COLUMN IF NOT EXISTS amount_tax numeric;
            """,
        )
        openupgrade.logged_query(
            env.cr, "UPDATE hr_expense SET amount_tax = (total_amount - untaxed_amount)"
        )
    # amount_tax_company field (to be filled in post-migration with ORM)
    if not openupgrade.column_exists(env.cr, "hr_expense", "amount_tax_company"):
        openupgrade.logged_query(
            env.cr,
            """
            ALTER TABLE hr_expense
            ADD COLUMN IF NOT EXISTS amount_tax_company numeric;
            """,
        )
        openupgrade.logged_query(env.cr, "UPDATE hr_expense SET amount_tax_company = 0")


def _hr_expense_sheet_table_new_columns(env):
    """Custom process to create new columns:
    - total_amount_taxes: set 0 value to re-set in post-migration.
    - untaxed_amount: set 0 value to re-set in post-migration"""
    # total_amount_taxes
    if not openupgrade.column_exists(env.cr, "hr_expense_sheet", "total_amount_taxes"):
        openupgrade.logged_query(
            env.cr,
            """
            ALTER TABLE hr_expense_sheet
            ADD COLUMN IF NOT EXISTS total_amount_taxes numeric;
            """,
        )
        openupgrade.logged_query(
            env.cr, "UPDATE hr_expense_sheet SET total_amount_taxes = 0"
        )
    # untaxed_amount field
    if not openupgrade.column_exists(env.cr, "hr_expense_sheet", "untaxed_amount"):
        openupgrade.logged_query(
            env.cr,
            """
            ALTER TABLE hr_expense_sheet
            ADD COLUMN IF NOT EXISTS untaxed_amount numeric;
            """,
        )
        openupgrade.logged_query(
            env.cr, "UPDATE hr_expense_sheet SET untaxed_amount = 0"
        )


def _fast_fill_analytic_distribution_on_hr_expense(env):
    """Similar process to the one performed at
    https://github.com/OCA/OpenUpgrade/pull/4004"""
    if not openupgrade.column_exists(env.cr, "hr_expense", "analytic_distribution"):
        openupgrade.logged_query(
            env.cr,
            """
            ALTER TABLE hr_expense
            ADD COLUMN IF NOT EXISTS analytic_distribution jsonb;
            """,
        )

    openupgrade.logged_query(
        env.cr,
        """
        WITH distribution_data AS (
            WITH sub AS (
                SELECT
                    all_line_data.expense_id,
                    all_line_data.analytic_account_id,
                    SUM(all_line_data.percentage) AS percentage
                FROM (
                    SELECT
                        he.id AS expense_id,
                        account.id AS analytic_account_id,
                        100 AS percentage
                    FROM hr_expense he
                    JOIN account_analytic_account account
                        ON account.id = he.analytic_account_id
                    WHERE he.analytic_account_id IS NOT NULL
                    UNION ALL
                    SELECT
                        he.id AS expense_id,
                        dist.account_id AS analytic_account_id,
                        dist.percentage AS percentage
                    FROM hr_expense he
                    JOIN account_analytic_tag_hr_expense_rel tag_rel
                        ON tag_rel.hr_expense_id = he.id
                    JOIN account_analytic_distribution dist
                        ON dist.tag_id = tag_rel.account_analytic_tag_id
                ) AS all_line_data
                GROUP BY all_line_data.expense_id, all_line_data.analytic_account_id
            )
            SELECT
                sub.expense_id,
                jsonb_object_agg(sub.analytic_account_id::text, sub.percentage)
                    AS analytic_distribution
            FROM sub
            GROUP BY sub.expense_id
        )
        UPDATE hr_expense he SET analytic_distribution = dist.analytic_distribution
        FROM distribution_data dist WHERE he.id = dist.expense_id
        """,
    )


_xmlid_renames = [
    (
        "hr_expense.product_product_zero_cost",
        "hr_expense.product_product_no_cost",
    ),
]


@openupgrade.migrate()
def migrate(env, version):
    _hr_expense_table_new_columns(env)
    _hr_expense_sheet_table_new_columns(env)
    _fast_fill_analytic_distribution_on_hr_expense(env)
    openupgrade.rename_xmlids(env.cr, _xmlid_renames)
