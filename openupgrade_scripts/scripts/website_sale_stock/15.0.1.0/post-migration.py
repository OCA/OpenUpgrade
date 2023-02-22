from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(
        env.cr,
        """UPDATE product_template
            SET allow_out_of_stock_order = CASE
                WHEN inventory_availability IN ('never', 'custom')
                    THEN true ELSE false END, show_availability = CASE
                WHEN inventory_availability IN ('always', 'threshold')
                    THEN true ELSE false END,
                    available_threshold = CASE WHEN inventory_availability = 'always'
                        THEN 999999999 END
        """,
    )
