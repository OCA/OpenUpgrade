from openupgradelib import openupgrade


def _create_column_for_avoiding_automatic_computing(env):
    openupgrade.logged_query(
        env.cr,
        """
            ALTER TABLE stock_move
                ADD COLUMN IF NOT EXISTS reservation_date date;
        """,
    )


def _fill_stock_quant_package_name_if_null(env):
    openupgrade.logged_query(
        env.cr,
        """
            UPDATE stock_quant_package
            SET name = 'Unknown Pack'
            WHERE name IS NULL;
        """,
    )


def _fill_stock_quant_in_date(env):
    openupgrade.logged_query(
        env.cr,
        """
            UPDATE stock_quant
            SET in_date = create_date
            WHERE in_date IS NULL;
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.convert_field_to_html(env.cr, "stock_location", "comment", "comment")
    openupgrade.convert_field_to_html(env.cr, "stock_picking", "note", "note")
    _create_column_for_avoiding_automatic_computing(env)
    _fill_stock_quant_package_name_if_null(env)
    _fill_stock_quant_in_date(env)
