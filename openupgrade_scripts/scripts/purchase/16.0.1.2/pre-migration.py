from openupgradelib import openupgrade


def _fill_analytic_distribution(env):

    openupgrade.logged_query(
        env.cr,
        """
        WITH distribution_data AS (
            WITH sub AS (
                SELECT
                    all_line_data.porder_line_id,
                    all_line_data.account_analytic_id,
                    SUM(all_line_data.percentage) AS percentage
                FROM (
                    SELECT
                        porder_line.id AS porder_line_id,
                        account.id AS account_analytic_id,
                        100 AS percentage
                      FROM purchase_order_line porder_line
                      JOIN account_analytic_account account
                            ON account.id = porder_line.account_analytic_id
                     WHERE porder_line.account_analytic_id IS NOT NULL

                     UNION ALL

                    SELECT
                        porder_line.id AS porder_line_id,
                        dist.account_id AS account_analytic_id,
                        dist.percentage AS percentage
                      FROM purchase_order_line porder_line
                      JOIN account_analytic_tag_purchase_order_line_rel tag_rel
                            ON tag_rel.purchase_order_line_id = porder_line.id
                      JOIN account_analytic_distribution dist
                            ON dist.tag_id = tag_rel.account_analytic_tag_id
                ) AS all_line_data
                GROUP BY all_line_data.porder_line_id, all_line_data.account_analytic_id
            )
            SELECT
                sub.porder_line_id,
                jsonb_object_agg(
                    sub.account_analytic_id::text, sub.percentage
                ) AS analytic_distribution
              FROM sub
             GROUP BY sub.porder_line_id
        )
        UPDATE purchase_order_line porder_line
           SET analytic_distribution = dist.analytic_distribution
          FROM distribution_data dist
         WHERE porder_line.id = dist.porder_line_id;
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    _fill_analytic_distribution(env)
