from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    column = openupgrade.get_legacy_name("notes")
    openupgrade.convert_field_to_html(
        env.cr, "hr_contract", column, "notes", verbose=True
    )
