# Copyright 2025 Tecnativa - Pedro M. Baeza
# Copyright 2025 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import json

from openupgradelib import openupgrade

from odoo.tools import html2plaintext


def _convert_product_ribbon_html_to_name(env):
    env.cr.execute("SELECT id, html FROM product_ribbon")
    for row in env.cr.fetchall():
        record_id, translations = row
        for lang in translations:
            translations[lang] = html2plaintext(translations[lang])
        query = "UPDATE product_ribbon SET name = %s::jsonb WHERE id = %s"
        env.cr.execute(query, (json.dumps(translations), record_id))


def _website_sale_product_attachment(env):
    """Compatibility with website_sale_product_attachment to create the necessary
    product_document records and display those attachments in the e-commerce
    product file.
    """
    if not openupgrade.table_exists(env.cr, "ir_attachment_product_template_rel"):
        return
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO ir_attachment (
            name,
            res_id,
            res_model,
            company_id,
            file_size,
            type,
            store_fname,
            checksum,
            mimetype,
            index_content,
            create_uid,
            create_date,
            write_uid,
            write_date
        )
        SELECT
            a.name,
            rel.product_template_id,
            'product.template',
            a.company_id,
            a.file_size,
            a.type,
            a.store_fname,
            a.checksum,
            a.mimetype,
            a.index_content,
            a.create_uid,
            a.create_date,
            a.write_uid,
            a.write_date
        FROM ir_attachment_product_template_rel AS rel
        JOIN ir_attachment AS a ON rel.ir_attachment_id = a.id
        RETURNING id
        """,
    )
    new_attachment_ids = [x[0] for x in env.cr.fetchall()]
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO product_document (
            ir_attachment_id,
            sequence,
            active,
            shown_on_product_page,
            create_uid,
            create_date,
            write_uid,
            write_date
        )
        SELECT
            a.id,
            10,
            true,
            true,
            a.create_uid,
            a.create_date,
            a.write_uid,
            a.write_date
        FROM ir_attachment a
        WHERE a.id IN %s
        """,
        (tuple(new_attachment_ids),),
    )


@openupgrade.migrate()
def migrate(env, version):
    _convert_product_ribbon_html_to_name(env)
    _website_sale_product_attachment(env)
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE product_ribbon SET position='right'
        WHERE html_class LIKE '%o_ribbon_right%'
        """,
    )
    openupgrade.load_data(env, "website_sale", "18.0.1.1/noupdate_changes_work.xml")
