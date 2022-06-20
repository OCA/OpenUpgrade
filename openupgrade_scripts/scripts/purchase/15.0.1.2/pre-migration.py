from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.set_xml_ids_noupdate_value(
        env,
        "purchase",
        [
            "track_po_line_qty_received_template",
            "track_po_line_template",
        ],
        True,
    )
