from openupgradelib import openupgrade


def date_to_datetime_fields(env):
    # convert column from date to datetime
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE sale_order ALTER COLUMN effective_date TYPE TIMESTAMP WITHOUT TIME ZONE
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        WITH subquery (sale_id, date_done) AS (
            SELECT sale_id, MIN(date_done)
            FROM stock_picking AS sp
            WHERE date_done IS NOT NULL AND sale_id IS NOT NULL
            GROUP BY sale_id
        )
        UPDATE sale_order so
        SET effective_date = sub.date_done
        FROM subquery sub
        WHERE sub.sale_id = so.id
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    date_to_datetime_fields(env)
