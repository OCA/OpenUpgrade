from openupgradelib import openupgrade

_fields_renames = [
    (
        "sale_management_equips.equipo",
        "sale_management_equips_equipo",
        "num_serie",
        "serial_number",
    ),
    (
        "sale_management_equips.equipo",
        "sale_management_equips_equipo",
        "puesta_en_marcha",
        "start_up_date",
    ),
    (
        "sale.order.line",
        "sale_order_line",
        "equipo",
        "equipment_id",
    ),
    (
        "product.template",
        "product_template",
        "requiere_equipo",
        "requires_equipment",
    ),
    (
        "product.template",
        "product_template",
        "crear_equipo",
        "create_equipment",
    ),
]
_models_renames = [("sale_management_equips.equipo", "equipment.equipment")]
_tables_renames = [("sale_management_equips_equipo", "equipment_equipment")]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_fields(env, _fields_renames)
    openupgrade.rename_models(env.cr, _models_renames)
    openupgrade.rename_tables(env.cr, _tables_renames)
