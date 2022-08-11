from openupgradelib import openupgrade

_columns_copy = {
    "purchase_order": [
        ("notes", None, None),
    ],
}


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.copy_columns(env.cr, _columns_copy)
    openupgrade.set_xml_ids_noupdate_value(
        env,
        "purchase",
        [
            "track_po_line_qty_received_template",
            "track_po_line_template",
        ],
        True,
    )
    openupgrade.add_fields(
        env,
        [
            (
                "purchase",
                "product.packaging",
                "product_packaging",
                "boolean",
                "bool",
                "purchase",
                True,
            )
        ],
    )
