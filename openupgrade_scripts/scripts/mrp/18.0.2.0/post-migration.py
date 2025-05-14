# Copyright 2025 Akretion
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from openupgradelib import openupgrade


def _migrate_mrp_documents(env):
    if not openupgrade.table_exists(env.cr, "product_document_mrp_legacy"):
        return

    # Fetch old mrp_document data: ir_attachment_id, active, priority.
    # `product_document_mrp_legacy` contains fields from old `mrp_document`.
    # `ir_attachment_id` was M2O to `ir.attachment`.
    # `id` was the own ID of the `mrp_document` record.
    env.cr.execute(
        """
        SELECT ir_attachment_id, active, priority
        FROM product_document_mrp_legacy
        WHERE ir_attachment_id IS NOT NULL
    """
    )
    old_docs_data = env.cr.dictfetchall()

    if not old_docs_data:
        openupgrade.drop_tables(env.cr, ["product_document_mrp_legacy"])
        return

    # Mapping from old priorities to new sequence values.
    # Default sequence on product.document is 10. Lower sequence means higher priority.
    priority_to_sequence = {
        "0": 15,  # Normal
        "1": 20,  # Low
        "2": 10,  # High
        "3": 5,  # Very High
    }

    ProductDocument = env["product.document"]
    attachment_ids_to_migrate = [
        r["ir_attachment_id"] for r in old_docs_data if r["ir_attachment_id"]
    ]

    # Pre-fetch existing product.document records to avoid duplicates and update them.
    # Handles cases where product module might have already created product.document.
    existing_product_docs = ProductDocument.search(
        [("ir_attachment_id", "in", attachment_ids_to_migrate)]
    )
    attachments_to_existing_pd = {
        pd.ir_attachment_id.id: pd for pd in existing_product_docs
    }

    pd_vals_list_create = []
    updated_count = 0
    created_count = 0

    for old_doc_data in old_docs_data:
        ir_attachment_id = old_doc_data["ir_attachment_id"]
        if not ir_attachment_id:
            continue

        # Ensure priority key is a string for dict lookup
        sequence_val = priority_to_sequence.get(str(old_doc_data["priority"]), 10)
        active_val = old_doc_data["active"]

        existing_pd = attachments_to_existing_pd.get(ir_attachment_id)

        if existing_pd:
            # Update existing product.document if necessary
            write_vals = {}
            # 'bom' takes precedence. If it was 'hidden' or not set, update to 'bom'.
            if existing_pd.attached_on_mrp != "bom":
                write_vals["attached_on_mrp"] = "bom"

            # Update sequence if it was the default (10) and new mapping
            # suggests different,
            # or if explicitly set priority implies a new sequence different
            # from current.
            if (existing_pd.sequence == 10 and sequence_val != 10) or (
                old_doc_data["priority"] is not None
                and existing_pd.sequence != sequence_val
            ):
                write_vals["sequence"] = sequence_val

            if existing_pd.active != active_val:
                write_vals["active"] = active_val

            if write_vals:
                existing_pd.write(write_vals)
                updated_count += 1
        else:
            # Create new product.document
            pd_vals_list_create.append(
                {
                    "ir_attachment_id": ir_attachment_id,
                    "active": active_val,
                    "attached_on_mrp": "bom",  # Assume all old docs are 'bom' relevant
                    "sequence": sequence_val,
                }
            )
            created_count += 1

    if pd_vals_list_create:
        ProductDocument.create(pd_vals_list_create)

    openupgrade.drop_tables(env.cr, ["product_document_mrp_legacy"])
    log_message = (
        f"Migrated mrp.document records to product.document: "
        f"{created_count} created, {updated_count} updated."
    )
    openupgrade.log(env.cr, "MRP", log_message)


def _set_mrp_bom_line_manual_consumption(env):
    # Old logic for mrp.bom.line.manual_consumption (v17):
    # line.manual_consumption = (line.tracking != 'none' or line.operation_id)
    # `product_id.tracking` (on product.product) is related
    # to `product_tmpl_id.tracking`.
    # `product.template.tracking` depends on `is_storable` in v18.
    # The `stock` module migration scripts handle `type` -> `is_storable`
    # and adjusts `tracking`. So, reading `product_id.tracking` here should give
    # the v18-compatible value. `mrp.bom.line` has a `tracking` field related to
    # `product_id.tracking`.
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE mrp_bom_line
        SET manual_consumption = TRUE
        WHERE (tracking IS NOT NULL AND tracking != 'none') OR operation_id IS NOT NULL;
        """,
        reason=(
            "Set manual_consumption on mrp.bom.line based on v17 logic "
            "(tracked product or specific operation)."
        ),
    )


@openupgrade.migrate()
def migrate(env, version):
    _migrate_mrp_documents(env)
    _set_mrp_bom_line_manual_consumption(env)

    xml_ids_to_delete = [
        "mrp.act_assign_serial_numbers_production",
        "mrp.view_mrp_workorder_view_gantt",  # Gantt views often refactored/removed
        "mrp.view_assign_serial_numbers_production",
        "mrp.view_document_file_kanban_mrp",  # Replaced by product.document views
        "mrp.view_mrp_document_form",  # Replaced by product.document views
        "mrp.workcenter_line_gantt_production",  # Gantt views often refactored/removed
    ]
    openupgrade.delete_records_safely_by_xml_id(env, xml_ids_to_delete)
