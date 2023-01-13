from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    column = openupgrade.get_legacy_name("description")
    openupgrade.convert_field_to_html(
        env.cr, "purchase_requisition", column, "description", verbose=False
    )
