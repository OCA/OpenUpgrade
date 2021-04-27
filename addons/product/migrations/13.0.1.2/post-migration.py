# Copyright 2020 ForgeFlow <http://www.forgeflow.com>
# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def fill_product_template_attribute_value_attribute_line_id(env):
    openupgrade.logged_query(
        env.cr, """
        UPDATE product_template_attribute_value ptav
        SET attribute_line_id = ptal.id
        FROM product_template_attribute_line ptal
        JOIN product_template pt ON ptal.product_tmpl_id = pt.id
        JOIN product_attribute_value_product_template_attribute_line_rel
            avtalr ON avtalr.product_template_attribute_line_id = ptal.id
        WHERE ptal.active = TRUE AND ptav.product_tmpl_id = pt.id AND
            ptav.product_attribute_value_id = avtalr.product_attribute_value_id
        """,
    )


def fill_product_template_attribute_value__attribute_id_related(env):
    openupgrade.logged_query(
        env.cr, """
        UPDATE product_template_attribute_value ptav
        SET attribute_id = ptal.attribute_id
        FROM product_template_attribute_line ptal
        WHERE ptav.attribute_line_id = ptal.id""",
    )


def fill_product_variant_combination_table(env):
    openupgrade.logged_query(
        env.cr, """
        INSERT INTO product_variant_combination
        (product_product_id, product_template_attribute_value_id)
        SELECT pavppr.product_product_id, ptav.id
        FROM product_attribute_value_product_product_rel pavppr
        JOIN product_product pp
            ON pp.id = pavppr.product_product_id
        JOIN product_template_attribute_value ptav
            ON ptav.product_attribute_value_id = pavppr.product_attribute_value_id
                AND pp.product_tmpl_id = ptav.product_tmpl_id
        """,
    )


def convert_image_attachments(env):
    mapping = {
        'product.product': "image_variant",
        'product.template': "image",
    }
    for model, field in mapping.items():
        Model = env[model]
        attachments = env['ir.attachment'].search([
            ('res_model', '=', model),
            ('res_field', '=', field),
            ('res_id', '!=', False),
        ])
        for attachment in attachments:
            Model.browse(attachment.res_id).image_1920 = attachment.datas


def empty_product_company(env):
    """In V12 the company_id field in product template had the user's company
    as default value. This causes that in the pricelist items user can not filter
    by product.
    In V13 this field has not a default value, so the value would be a null
    value for instances with one company only.
    """
    companies = env["res.company"].search([])
    if len(companies) == 1:
        openupgrade.logged_query(env.cr, """
        UPDATE product_template SET company_id = null
        WHERE company_id IS NOT NULL;
        """)


@openupgrade.migrate()
def migrate(env, version):
    fill_product_template_attribute_value_attribute_line_id(env)
    fill_product_template_attribute_value__attribute_id_related(env)
    fill_product_variant_combination_table(env)
    openupgrade.load_data(
        env.cr, "product", "migrations/13.0.1.2/noupdate_changes.xml")
    convert_image_attachments(env)
    empty_product_company(env)
