from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version=None):
    if not openupgrade.column_exists(env.cr, "purchase_order_line", "discount"):
        openupgrade.logged_query(
            env.cr,
            "ALTER TABLE purchase_order_line ADD COLUMN discount FLOAT DEFAULT 0",
        )
        openupgrade.logged_query(
            env.cr,
            "ALTER TABLE purchase_order_line ALTER COLUMN discount DROP DEFAULT",
        )
