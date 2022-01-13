# Copyright 2020 ForgeFlow <http://www.forgeflow.com>
# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade
from odoo.tools import sql


def fill_product_variant_combination_table(env):
    openupgrade.logged_query(
        env.cr, """
        INSERT INTO product_variant_combination
        (product_product_id, product_template_attribute_value_id)
        SELECT pavppr.product_product_id, ptav.id
        FROM product_attribute_value_product_product_rel pavppr
        JOIN product_attribute_value pav
            ON pav.id = pavppr.product_attribute_value_id
        JOIN product_product pp
            ON pp.id = pavppr.product_product_id
        JOIN product_template_attribute_value ptav
            ON ptav.product_attribute_value_id = pav.id
                AND pp.product_tmpl_id = ptav.product_tmpl_id
                AND ptav.attribute_id = pav.attribute_id
        GROUP BY pavppr.product_product_id, ptav.id""",
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


@openupgrade.logging()
def empty_template_pricelist_company(env):
    """On v13, there's no default company associated with the template nor the
    pricelist, on contrary than on v12. We need to empty the company_id field in
    case of having only one company for not having problems later when creating
    new pricelists and not being able to select old products due to the
    difference on the company_id field (on a pricelist without company, you can
    only select templates without company, and vice versa, but not a mix of
    both).

    We need to empty the company of pricelists as well.

    If there are more than one company in the DB, then everything is
    preserved as it is.
    """
    env.cr.execute("SELECT COUNT(*) FROM res_company")
    if env.cr.fetchone()[0] == 1:
        openupgrade.logged_query(
            env.cr, "UPDATE product_template SET company_id = NULL WHERE company_id is NOT NULL",
        )
        openupgrade.logged_query(
            env.cr, "UPDATE product_pricelist SET company_id = NULL WHERE company_id is NOT NULL",
        )


def adapt_pricelist_settings(env):
    """In v12, if pricelist setting was marked it implied group_sale_pricelist,
    and if the setting was 'percentage' it also implied group_product_pricelist.
    In v13, if pricelist setting was marked it implies group_product_pricelist,
    and if the setting is 'advanced', then it has also group_sale_pricelist.
    And about the options, 'percentage' has become 'basic' and 'formula' has become 'advanced'."""
    group_user = env.ref("base.group_user").sudo()
    group_product_pricelist = env.ref("product.group_product_pricelist").sudo()
    group_sale_pricelist = env.ref("product.group_sale_pricelist").sudo()
    ir_config_param = env["ir.config_parameter"].sudo()
    sale_installed = openupgrade.table_exists(env.cr, "sale_order")
    pos_installed = openupgrade.table_exists(env.cr, "pos_order")
    sale_pricelist_setting = ir_config_param.get_param(
        "sale.sale_pricelist_setting", ""
    )
    pos_pricelist_setting = ir_config_param.get_param(
        "point_of_sale.pos_pricelist_setting", ""
    )
    # multi_sales_price = sale_pricelist_setting and sale_pricelist_setting in ['percentage', 'formula']
    pos_sales_price = ir_config_param.get_param("point_of_sale.pos_sales_price")
    with env.norecompute():
        if (
            (
                group_product_pricelist in group_user.implied_ids
                and group_sale_pricelist in group_user.implied_ids
                and not sale_installed
                and not pos_installed
            )
            or (
                sale_installed
                and sale_pricelist_setting == "percentage"
                and pos_pricelist_setting != "formula"
            )
            or (
                pos_installed
                and pos_sales_price
                and pos_pricelist_setting == "percentage"
                and sale_pricelist_setting != "formula"
            )
        ):
            # 'basic' case
            group_user.write({"implied_ids": [(3, group_sale_pricelist.id)]})
            group_sale_pricelist.write({"users": [(5,)]})
            ir_config_param.set_param("product.product_pricelist_setting", "basic")
        elif (
            (
                group_product_pricelist not in group_user.implied_ids
                and group_sale_pricelist in group_user.implied_ids
                and not sale_installed
                and not pos_installed
            )
            or (sale_installed and sale_pricelist_setting == "formula")
            or (
                pos_installed and pos_sales_price and pos_pricelist_setting == "formula"
            )
        ):
            # 'advanced' case
            group_user.write({"implied_ids": [(4, group_product_pricelist.id)]})
            ir_config_param.set_param("product.product_pricelist_setting", "advanced")


@openupgrade.migrate()
def migrate(env, version):
    fill_product_variant_combination_table(env)
    openupgrade.load_data(
        env.cr, "product", "migrations/13.0.1.2/noupdate_changes.xml")
    convert_image_attachments(env)
    empty_template_pricelist_company(env)
    adapt_pricelist_settings(env)
    sql.drop_index(
        env.cr, 'product_template_attribute_value_ou_migration_idx',
        "product_template_attribute_value")
