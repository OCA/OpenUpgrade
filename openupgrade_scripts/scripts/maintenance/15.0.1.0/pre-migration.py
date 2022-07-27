from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.convert_field_to_html(
        env.cr,
        "maintenance_equipment",
        "note",
        "note",
    )
    openupgrade.convert_field_to_html(
        env.cr,
        "maintenance_equipment_category",
        "note",
        "note",
    )
    openupgrade.convert_field_to_html(
        env.cr,
        "maintenance_request",
        "description",
        "description",
    )
