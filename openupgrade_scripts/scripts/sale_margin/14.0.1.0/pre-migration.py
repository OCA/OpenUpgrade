from openupgradelib import openupgrade


def recompute_margin_percent(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE sale_order
        SET margin_percent = percent / 100;

        UPDATE sale_order_line
        SET margin_percent = margin_percent / 100;
        """,
    )


def fast_filled_margin_percent(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE sale_order_line
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


@openupgrade.migrate()
def migrate(env, installed_version):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE sale_order
        ADD COLUMN IF NOT EXISTS margin_percent double precision;
        """,
    )
    # If sale_order_margin_percent module was installed,
    # recompute margin_percent field."
    if openupgrade.column_exists(
        env.cr, "sale_order_line", "margin_percent"
    ) and openupgrade.column_exists(env.cr, "sale_order", "percent"):
        recompute_margin_percent(env)
    else:
        fast_filled_margin_percent(env)
