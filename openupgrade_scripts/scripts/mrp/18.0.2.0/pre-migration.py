# Copyright 2025 Akretion
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from openupgradelib import openupgrade

_renamed_fields = [
    ("mrp.production", "mrp_production", "date_planned_start", "date_start"),
    ("mrp.production", "mrp_production", "date_planned_finished", "date_finished"),
    ("mrp.workorder", "mrp_workorder", "date_planned_start", "date_start"),
    ("mrp.workorder", "mrp_workorder", "date_planned_finished", "date_finished"),
]


@openupgrade.migrate()
def migrate(env, version):
    # Handle mrp.document model removal and merge into product.document
    # The old mrp_document model inherited ir.attachment via 'ir_attachment_id' M2O.
    # The product_document_mrp_legacy table will contain fields specific
    # to the old mrp_document.
    if openupgrade.table_exists(env.cr, "mrp_document"):
        openupgrade.rename_tables(
            env.cr, [("mrp_document", "product_document_mrp_legacy")]
        )

    openupgrade.rename_fields(env, _renamed_fields)

    # Attempt to get column type for 'produce_delay'
    # If get_pg_column_type is not available, this part might need adjustment
    # based on your specific openupgradelib version or available helpers.
    # For now, proceeding with a direct check and alter.
    if openupgrade.column_exists(env.cr, "mrp_bom", "produce_delay"):
        # A more robust check would be to inspect information_schema.columns.data_type
        # but that's more complex without a helper.
        # Assuming if it exists and needs conversion, it's likely 'double precision'.
        try:
            openupgrade.alter_column_type(
                env.cr,
                "mrp_bom",
                "produce_delay",
                "integer",
                "USING ROUND(produce_delay)::integer",
            )
            openupgrade.log(
                env.cr,
                "MRP",
                "Altered column type of mrp_bom.produce_delay to integer.",
            )
        except Exception as e:
            openupgrade.log(
                env.cr,
                "MRP",
                "Could not alter column type of mrp_bom.produce_delay: %s. "
                "Manual check might be needed." % e,
                level="warning",
            )
