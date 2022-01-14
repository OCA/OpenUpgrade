from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.set_xml_ids_noupdate_value(
        env,
        "stock_sms",
        ["ir_rule_sms_template_stock_manager"],
        True,
    )
