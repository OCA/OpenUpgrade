# Copyright 2020 ForgeFlow <http://www.forgeflow.com>
# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade
from odoo.tools import sql


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


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(
        env.cr, "product", "migrations/13.0.1.2/noupdate_changes.xml")
    convert_image_attachments(env)
    empty_template_pricelist_company(env)
    sql.drop_index(
        env.cr, 'product_template_attribute_value_ou_migration_idx',
        "product_template_attribute_value")
