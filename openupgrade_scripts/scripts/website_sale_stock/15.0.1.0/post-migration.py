from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(
        env.cr,
        """
            UPDATE product_template
            SET allow_out_of_stock_order = CASE
            WHEN inventory_availability = 'never' THEN true ELSE false
            END
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
            UPDATE product_template
            SET show_availability = CASE
            WHEN inventory_availability = 'threshold' THEN true ELSE false
            END
        """,
    )
