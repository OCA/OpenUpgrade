# Copyright 2025 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


def mrp_document_to_product_document(env):
    """
    mrp.document has been replaced by product.document.
    copy all records of mrp_document to product_document, keep a link
    """
    link_column = openupgrade.get_legacy_name("mrp_document_id")
    openupgrade.add_columns(
        env,
        [("product.document", link_column, "integer")],
    )
    openupgrade.logged_query(
        env.cr,
        f"""
        INSERT INTO product_document
        (ir_attachment_id, active, sequence, {link_column}, attached_on_mrp)
        SELECT
        ir_attachment_id, active, 10-COALESCE(priority, '0')::int, id, 'hidden'
        FROM mrp_document
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    mrp_document_to_product_document(env)
