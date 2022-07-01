from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # try delete noupdate records
    openupgrade.delete_records_safely_by_xml_id(
        env,
        [
            "coupon.mail_template_sale_coupon",
        ],
    )
