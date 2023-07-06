from openupgradelib import openupgrade


def _update_delivery_status(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE sale_order
        ADD COLUMN IF NOT EXISTS delivery_status character varying
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE sale_order as so
        SET delivery_status =
        CASE
            WHEN
            (SELECT COUNT(*) FROM stock_picking WHERE sale_id = so.id) = 0
            OR
            (
                SELECT COUNT(*)
                FROM stock_picking
                WHERE sale_id = so.id AND state = 'cancel'
            ) = (
                    SELECT COUNT(*)
                    FROM stock_picking
                    WHERE sale_id = so.id
                ) THEN NULL
            WHEN
            (
                SELECT COUNT(*)
                FROM stock_picking
                WHERE sale_id = so.id AND state IN ('done', 'cancel')
            ) = (
                    SELECT COUNT(*)
                    FROM stock_picking
                    WHERE sale_id = so.id
                ) THEN 'full'
            WHEN
            (
                SELECT COUNT(*)
                FROM stock_picking
                WHERE sale_id = so.id AND state = 'done'
            ) > 0 THEN 'partial'
            ELSE 'pending'
        END
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    _update_delivery_status(env)
