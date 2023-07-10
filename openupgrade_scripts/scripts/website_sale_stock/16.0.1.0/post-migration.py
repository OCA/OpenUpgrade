from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE sale_order
            SET shop_warning = warning_stock
        WHERE warning_stock IS NOT NULL
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE sale_order_line
            SET shop_warning = warning_stock
        WHERE warning_stock IS NOT NULL
        """,
    )
