from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.convert_field_to_html(
        env.cr, "snailmail_letter", "info_msg", "info_msg", verbose=False
    )
