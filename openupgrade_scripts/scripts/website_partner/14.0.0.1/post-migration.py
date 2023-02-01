from openupgradelib import openupgrade, openupgrade_140


@openupgrade.migrate()
def migrate(env, version):
    openupgrade_140.convert_field_html_string_13to14(
        env,
        "res.partner",
        "website_description",
    )
