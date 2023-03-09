from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(
        env.cr,
        """UPDATE product_template
            SET allow_out_of_stock_order = CASE
                WHEN inventory_availability IN ('never', 'custom', 'always_no_lock')
                THEN true ELSE false END,
            show_availability = CASE
                WHEN inventory_availability IN ('always', 'threshold', 'always_no_lock')
                THEN true ELSE false END,
            available_threshold = CASE
                WHEN inventory_availability IN ('always', 'always_no_lock')
                THEN 999999999 END,
            out_of_stock_message = CASE
                WHEN inventory_availability = 'always_no_lock' THEN '0 Stock' END
        """,
    )
