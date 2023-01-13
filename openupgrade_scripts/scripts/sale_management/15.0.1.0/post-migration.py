from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    column = openupgrade.get_legacy_name("note")
    openupgrade.convert_field_to_html(
        env.cr, "sale_order_template", column, "note", verbose=False
    )
