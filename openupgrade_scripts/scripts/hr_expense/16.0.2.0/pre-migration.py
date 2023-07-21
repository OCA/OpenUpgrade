from openupgradelib import openupgrade


def _fill_analytic_distribution(env):
    if not openupgrade.column_exists(
        env.cr, "purchase_requisition_line", "analytic_distribution"
    ):
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
            WITH distribution_mapping AS (
                WITH all_line_sum_percentage AS (
                    SELECT
                        all_line_data.he_id,
                        all_line_data.analytic_account_id,
                        SUM(all_line_data.percentage) AS percentage
                    FROM (
                        SELECT
                            he.id AS he_id,
                            he.analytic_account_id AS analytic_account_id,
                            100 AS percentage
                        FROM hr_expense he
                        WHERE he.analytic_account_id IS NOT NULL
                        UNION ALL
                        SELECT
                            he.id AS he_id,
                            dist.account_id AS analytic_account_id,
                            dist.percentage AS percentage
                        FROM hr_expense he
                        JOIN account_analytic_tag_hr_expense_rel account_tag_rel
                            ON account_tag_rel.hr_expense_id = he.id
                        JOIN account_analytic_distribution dist
                            ON dist.tag_id = account_tag_rel.account_analytic_tag_id
                    ) AS all_line_data
                    GROUP BY all_line_data.he_id, all_line_data.analytic_account_id
                )
                SELECT
                    he_id,
                    jsonb_object_agg(analytic_account_id, percentage) AS analytic_distribution
                  FROM all_line_sum_percentage
                 GROUP BY he_id
            )

            UPDATE hr_expense he
            SET analytic_distribution = dist.analytic_distribution
            FROM distribution_mapping dist
            WHERE he.id = dist.he_id
            """,
        )


@openupgrade.migrate()
def migrate(env, version):
    _fill_analytic_distribution(env)
    openupgrade.rename_xmlids(
        env.cr,
        [
            (
                "hr_expense.product_product_zero_cost",
                "hr_expense.product_product_no_cost",
            ),
        ],
    )
    openupgrade.set_xml_ids_noupdate_value(
        env,
        "hr_expense",
        [
            "product_product_no_cost",
        ],
        True,
    )
    openupgrade.delete_records_safely_by_xml_id(
        env,
        [
            "hr_expense.product_product_fixed_cost",
        ],
    )
