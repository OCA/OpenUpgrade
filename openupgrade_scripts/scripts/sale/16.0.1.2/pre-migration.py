from openupgradelib import openupgrade

_models_renames = [
    (
        "sale.payment.acquirer.onboarding.wizard",
        "sale.payment.provider.onboarding.wizard",
    ),
]

_tables_renames = [
    (
        "sale_payment_acquirer_onboarding_wizard",
        "sale_payment_provider_onboarding_wizard",
    ),
]

_renames_xmlids = [
    (
        "sale_management.menu_product_attribute_action",
        "sale.menu_product_attribute_action",
    ),
]


def _noupdate_switch(env):
    openupgrade.set_xml_ids_noupdate_value(
        env, "sale", ["model_sale_order_action_share"], False
    )


def _remove_table_constraints(env):
    openupgrade.delete_sql_constraint_safely(
        env, "sale", "sale_order", "date_order_conditional_required"
    )


def _drop_sql_views(env):
    openupgrade.logged_query(
        env.cr,
        """
        DROP VIEW IF EXISTS report_all_channels_sales
        """,
    )


def _fast_fill_analytic_distribution_on_sale_order_line(env):
    """
    Dynamically fill analytic_distribution for model that inherit from analytic.mixin
    Hmmm this method should be placed in the library
    Take a look with example of account.move.line
    The idea is to take all the distribution of an account.move.line
    which has analytic.tag then form it as a jsonb like {'1': 100, '2': 50}
    and also check if the table has analytic_account_column then check if it
    exist in the analytic_account of all the analytic_distribution of the analytic tags
    then take it as the 100%, which mean an account.move.line both specify '2' as the
    analytic.account.id and it has 1 analytic.tag also have that analytic.account then
    the value will sum together
    """
    if not openupgrade.column_exists(
        env.cr, "sale_order_line", "analytic_distribution"
    ):
        openupgrade.logged_query(
            env.cr,
            """
            ALTER TABLE sale_order_line
            ADD COLUMN IF NOT EXISTS analytic_distribution jsonb;
            """,
        )

    openupgrade.logged_query(
        env.cr,
        """
        WITH distribution_data AS (
            WITH sub AS (
                SELECT
                    all_line_data.sale_order_line_id,
                    all_line_data.analytic_account_id,
                    SUM(all_line_data.percentage) AS percentage
                FROM (
                    SELECT
                        so_line.id AS sale_order_line_id,
                        account.id AS analytic_account_id,
                        100 AS percentage
                    FROM sale_order_line so_line
                    JOIN sale_order so ON so.id = so_line.order_id
                    JOIN account_analytic_account account
                        ON account.id = so.analytic_account_id
                    WHERE so.analytic_account_id IS NOT NULL

                    UNION ALL

                    SELECT
                        so_line.id AS sale_order_line_id,
                        dist.account_id AS analytic_account_id,
                        dist.percentage AS percentage
                    FROM sale_order_line so_line
                    JOIN account_analytic_tag_sale_order_line_rel tag_rel
                        ON tag_rel.sale_order_line_id = so_line.id
                    JOIN account_analytic_distribution dist
                        ON dist.tag_id = tag_rel.account_analytic_tag_id
                ) AS all_line_data
                GROUP BY all_line_data.sale_order_line_id, all_line_data.analytic_account_id
            )
            SELECT
                sub.sale_order_line_id,
                jsonb_object_agg(sub.analytic_account_id::text, sub.percentage)
                    AS analytic_distribution
            FROM sub
            GROUP BY sub.sale_order_line_id
        )

        UPDATE sale_order_line so_line SET analytic_distribution = dist.analytic_distribution
        FROM distribution_data dist WHERE so_line.id = dist.sale_order_line_id
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_models(env.cr, _models_renames)
    openupgrade.rename_tables(env.cr, _tables_renames)
    openupgrade.rename_xmlids(env.cr, _renames_xmlids)
    _drop_sql_views(env)
    _noupdate_switch(env)
    _remove_table_constraints(env)
    _fast_fill_analytic_distribution_on_sale_order_line(env)
