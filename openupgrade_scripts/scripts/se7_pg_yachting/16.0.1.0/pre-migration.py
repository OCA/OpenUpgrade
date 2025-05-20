from openupgradelib import openupgrade

_fields_renames = [
    (
        "sale.order",
        "sale_order",
        "project_id",
        "boat_project_id",
    ),
    (
        "sale.order.line",
        "sale_order_line",
        "project_id",
        "boat_project_id",
    ),
    (
        "sale.order.line",
        "sale_order_line",
        "yacht_area",
        "boat_area_id",
    ),
    (
        "res.partner",
        "res_partner",
        "supplier_invoice_line_ids",
        "vendor_invoice_line_ids",
    ),
    (
        "res.config.settings",
        "res_config_settings",
        "supplier_commission_product",
        "vendor_commission_product",
    ),
    (
        "res.company",
        "res_company",
        "supplier_commission_product",
        "vendor_commission_product",
    ),
    (
        "purchase.order",
        "purchase_order",
        "project_id",
        "boat_project_id",
    ),
    (
        "purchase.order.line",
        "purchase_order_line",
        "project_id",
        "boat_project_id",
    ),
    (
        "purchase.order.line",
        "purchase_order_line",
        "yacht_area",
        "boat_area_id",
    ),
    (
        "project.pending.activation",
        "project_pending_activation",
        "invoice_line_ids",
        "move_line_ids",
    ),
    (
        "project.project",
        "project_project",
        "supplier_ids",
        "commission_vendor_ids",
    ),
    (
        "project.project",
        "project_project",
        "supplier_invoice_line_ids",
        "commission_vendor_invoice_line_ids",
    ),
    (
        "project.project",
        "project_project",
        "account_move_ids",
        "activation_account_move_ids",
    ),
]
_tables_renames = [
    ("invoice_sale_purchase_line_rel", "in_out_account_move_line_rel")
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_fields(env, _fields_renames)
    if openupgrade.column_exists(env.cr, "invoice_sale_purchase_line_rel", "sale_line_id"):
        openupgrade.rename_columns(
            env.cr,
            {
                "invoice_sale_purchase_line_rel": [
                    ("sale_line_id", "out_move_line_id"),
                ],
            },
        )
    if openupgrade.column_exists(env.cr, "invoice_sale_purchase_line_rel", "purchase_line_id"):
        openupgrade.rename_columns(
            env.cr,
            {
                "invoice_sale_purchase_line_rel": [
                    ("purchase_line_id", "in_move_line_id"),
                ],
            },
        )
    openupgrade.rename_tables(env.cr, _tables_renames)
