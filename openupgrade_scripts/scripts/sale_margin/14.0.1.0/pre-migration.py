from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, installed_version):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE sale_order_line
        ADD COLUMN IF NOT EXISTS margin_percent double precision;

        ALTER TABLE sale_order
        ADD COLUMN IF NOT EXISTS margin_percent double precision;
        """,
    )

    openupgrade.logged_query(
        env.cr,
        """
        UPDATE sale_order_line
        SET margin_percent = COALESCE(margin / NULLIF(price_subtotal, 0), 0);

        UPDATE sale_order
        SET margin_percent = COALESCE(margin / NULLIF(amount_untaxed, 0), 0);
        """,
    )
