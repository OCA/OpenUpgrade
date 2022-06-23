from openupgradelib import openupgrade


def _rename_field_product_packaging_to_product_packaging_id(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE sale_order_line
        ADD COLUMN IF NOT EXISTS product_packaging_id integer
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE sale_order_line
        SET product_packaging_id = product_packaging
        WHERE product_packaging IS NOT NULL
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    _rename_field_product_packaging_to_product_packaging_id(env)
