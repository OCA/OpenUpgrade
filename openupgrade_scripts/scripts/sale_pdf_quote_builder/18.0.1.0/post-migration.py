# Copyright 2025 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def fill_quotation_document(env):
    # company attachments
    env.cr.execute(
        """
        SELECT rc.sale_header_name, it.id AS attachment_id
        FROM res_company rc
        JOIN ir_attachment it ON it.res_model = 'res.company'
            AND it.type = 'binary' AND it.res_id = rc.id
        WHERE it.res_field = 'sale_header'
        """
    )
    headers = env.cr.fetchall()
    for header in headers:
        env["quotation.document"].create(
            {
                "name": header[0],
                "ir_attachment_id": header[1],
                "document_type": "header",
                "res_field": False,
            }
        )
    env.cr.execute(
        """
        SELECT rc.sale_footer_name, it.id AS attachment_id
        FROM res_company rc
        JOIN ir_attachment it ON it.res_model = 'res.company'
            AND it.type = 'binary' AND it.res_id = rc.id
        WHERE it.res_field = 'sale_footer'
        """
    )
    footers = env.cr.fetchall()
    for footer in footers:
        env["quotation.document"].create(
            {
                "name": footer[0],
                "ir_attachment_id": footer[1],
                "document_type": "footer",
                "res_field": False,
            }
        )
    # template attachments
    env.cr.execute(
        """
        SELECT sot.id, sot.sale_header_name, it.id AS attachment_id
        FROM sale_order_template sot
        JOIN ir_attachment it ON it.res_model = 'sale.order.template'
            AND it.type = 'binary' AND it.res_id = sot.id
        WHERE it.res_field = 'sale_header'
        """
    )
    headers = env.cr.fetchall()
    for header in headers:
        env["quotation.document"].create(
            {
                "name": header[1],
                "ir_attachment_id": header[2],
                "document_type": "header",
                "res_field": False,
                "quotation_template_ids": [(4, header[0])],
            }
        )
    env.cr.execute(
        """
        SELECT sot.id, sot.sale_footer_name, it.id AS attachment_id
        FROM sale_order_template sot
        JOIN ir_attachment it ON it.res_model = 'sale.order.template'
            AND it.type = 'binary' AND it.res_id = sot.id
        WHERE it.res_field = 'sale_footer'
        """
    )
    footers = env.cr.fetchall()
    for footer in footers:
        env["quotation.document"].create(
            {
                "name": footer[1],
                "ir_attachment_id": footer[2],
                "document_type": "footer",
                "res_field": False,
                "quotation_template_ids": [(4, footer[0])],
            }
        )


def fill_sale_pdf_form_field(env):
    # force execute this function (it's noupdate=1 in xml data)
    env["sale.pdf.form.field"]._add_basic_mapped_form_fields()


@openupgrade.migrate()
def migrate(env, version):
    fill_quotation_document(env)
    fill_sale_pdf_form_field(env)
