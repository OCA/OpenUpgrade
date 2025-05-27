# Copyright 2025 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade, openupgrade_180


def product_document_sequence(env):
    """
    Set sequence matching previous name only ordering
    """
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE product_document
        SET sequence=seq.seq
        FROM
        (
            SELECT
            product_document.id, row_number() OVER (
                PARTITION BY ir_attachment.res_id, ir_attachment.res_model
                ORDER BY ir_attachment.name
            ) AS seq
            FROM
            product_document
            JOIN ir_attachment
            ON product_document.ir_attachment_id=ir_attachment.id
        ) AS seq
        WHERE
        seq.id=product_document.id
        AND product_document.sequence IS NULL
        """,
    )


def product_template_is_favorite(env):
    """
    Set is_favorite flag based on priority
    """
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE
        product_template
        SET is_favorite = (priority IS NOT NULL AND priority != '0')
        """,
    )


def res_partner_specific_property_product_pricelist(env):
    """
    Get value for specific_property_product_pricelist from v17
    property_product_pricelist
    """
    old_field = env.ref("product.field_res_partner__property_product_pricelist")
    openupgrade_180.convert_company_dependent(
        env,
        "res.partner",
        "specific_property_product_pricelist",
        old_field_id=old_field.id,
    )
    # convert_company_dependent might have created ir.default entries, wipe them
    new_field = env.ref(
        "product.field_res_partner__specific_property_product_pricelist"
    )
    env["ir.default"].search([("field_id", "=", new_field.id)]).unlink()


@openupgrade.migrate()
def migrate(env, version):
    product_document_sequence(env)
    product_template_is_favorite(env)
    res_partner_specific_property_product_pricelist(env)
    openupgrade_180.convert_company_dependent(env, "product.product", "standard_price")
