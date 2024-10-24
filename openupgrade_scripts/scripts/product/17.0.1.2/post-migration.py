# Copyright 2024 Viindoo Technology Joint Stock Company (Viindoo)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env, "product", "17.0.1.2/noupdate_changes.xml")
    openupgrade.delete_records_safely_by_xml_id(env, ["product.list0"])
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO product_document (
            ir_attachment_id, active, create_uid, write_uid, create_date, write_date
        )
        SELECT id, True, create_uid, write_uid, create_date, write_date
        FROM ir_attachment
        WHERE res_model IN ('product.product', 'product.template')
        AND res_field IS NULL
        """,
    )
