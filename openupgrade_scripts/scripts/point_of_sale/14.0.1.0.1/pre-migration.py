from openupgradelib import openupgrade


def fill_pos_config_default_picking_type_id(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE pos_config pc
        SET picking_type_id = sw.pos_type_id
        FROM stock_warehouse sw
        WHERE sw.company_id = pc.company_id
            AND pc.picking_type_id IS NULL""",
    )


def delete_constraint(env):
    # Disappeared constraint
    openupgrade.delete_sql_constraint_safely(
        env, "point_of_sale", "res_partner", "unique_barcode"
    )


@openupgrade.migrate()
def migrate(env, version):
    fill_pos_config_default_picking_type_id(env)
    openupgrade.set_xml_ids_noupdate_value(
        env,
        "point_of_sale",
        [
            "rule_pos_bank_statement_account_user",
            "rule_pos_bank_statement_line_account_user",
            "rule_pos_bank_statement_line_user",
            "rule_pos_bank_statement_user",
            "rule_pos_cashbox_line_accountant",
            "rule_pos_config_multi_company",
            "rule_pos_multi_company",
            "rule_pos_order_report_multi_company",
            "rule_pos_payment_method_multi_company",
            "rule_pos_payment_multi_company",
            "rule_pos_session_multi_company",
        ],
        True,
    )
    delete_constraint(env)
