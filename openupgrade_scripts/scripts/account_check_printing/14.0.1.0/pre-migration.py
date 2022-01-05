from openupgradelib import openupgrade


def add_preferred_payment_method_id_field_account_move(env):
    if not openupgrade.column_exists(
        env.cr, "account_move", "preferred_payment_method_id"
    ):
        openupgrade.logged_query(
            env.cr,
            """
            ALTER TABLE account_move
            ADD COLUMN preferred_payment_method_id integer
            """,
        )
        openupgrade.logged_query(
            env.cr,
            """
            UPDATE account_move am
            SET preferred_payment_method_id = CAST(
                SPLIT_PART(ip.value_reference, ',', 2) AS int)
            FROM ir_property ip
            WHERE ip.company_id = am.company_id AND
                ip.res_id = CONCAT('res.partner,', am.partner_id) AND
                ip.name = 'property_payment_method_id'
            """,
        )


def fill_res_company_account_check_printing_layout(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE res_company
        SET account_check_printing_layout = 'disabled'
        WHERE account_check_printing_layout != 'disabled' AND
            account_check_printing_layout IS NOT NULL
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.copy_columns(
        env.cr,
        {"res_company": [("account_check_printing_layout", None, None)]},
    )
    add_preferred_payment_method_id_field_account_move(env)
    fill_res_company_account_check_printing_layout(env)
