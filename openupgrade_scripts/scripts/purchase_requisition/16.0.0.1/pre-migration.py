from openupgradelib import openupgrade


def _fill_analytic_distribution_on_purchase_requisition_line(env):
    if not openupgrade.column_exists(
        env.cr, "purchase_requisition_line", "analytic_distribution"
    ):
        openupgrade.logged_query(
            env.cr,
            """
            ALTER TABLE purchase_requisition_line
            ADD COLUMN IF NOT EXISTS analytic_distribution jsonb;
            """,
        )

    openupgrade.logged_query(
        env.cr,
        """
        WITH distribution_data AS (
            WITH sub AS (
                SELECT
                    all_line_data.requis_line_id,
                    all_line_data.account_analytic_id,
                    SUM(all_line_data.percentage) AS percentage
                FROM (
                    SELECT
                        requis_line.id AS requis_line_id,
                        account.id AS account_analytic_id,
                        100 AS percentage
                      FROM purchase_requisition_line requis_line
                      JOIN account_analytic_account account
                            ON account.id = requis_line.account_analytic_id
                     WHERE requis_line.account_analytic_id IS NOT NULL

                     UNION ALL

                    SELECT
                        requis_line.id AS requis_line_id,
                        dist.account_id AS account_analytic_id,
                        dist.percentage AS percentage
                      FROM purchase_requisition_line requis_line
                      JOIN account_analytic_tag_purchase_requisition_line_rel tag_rel
                            ON tag_rel.purchase_requisition_line_id = requis_line.id
                      JOIN account_analytic_distribution dist
                            ON dist.tag_id = tag_rel.account_analytic_tag_id
                ) AS all_line_data
                GROUP BY all_line_data.requis_line_id, all_line_data.account_analytic_id
            )
            SELECT
                sub.requis_line_id,
                jsonb_object_agg(
                    sub.account_analytic_id::text, sub.percentage
                ) AS analytic_distribution
              FROM sub
             GROUP BY sub.requis_line_id
        )
        UPDATE purchase_requisition_line requis_line
           SET analytic_distribution = dist.analytic_distribution
          FROM distribution_data dist
         WHERE requis_line.id = dist.requis_line_id;
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    _fill_analytic_distribution_on_purchase_requisition_line(env)
