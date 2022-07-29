# Copyright (C) 2021 Open Source Integrators <https://www.opensourceintegrators.com/>
# Copyright 2021 ForgeFlow S.L.  <https://www.forgeflow.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

_model_renames = [
    ("product.style", "product.ribbon"),
]

_field_renames = [
    ("product.ribbon", "product_ribbon", "name", "html"),
]

_table_renames = [
    ("product_style", "product_ribbon"),
]

_xmlid_renames = [
    ("website_sale.image_promo", "website_sale.sale_ribbon"),
    ("website_sale.access_product_style", "website_sale.access_product_ribbon_public"),
]


def update_product_ribbon_sale_ribbon(env):
    # it is noupdate data, not in noupdate_changes.xml
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE product_ribbon pr
        SET html_class = 'bg-success o_ribbon_left', html = 'Sale'
        FROM ir_model_data imd
        WHERE imd.model = 'product.ribbon' AND imd.res_id = pr.id
            AND imd.module = 'website_sale' AND imd.name = 'sale_ribbon'""",
    )


def set_product_ribbon_html_class_default(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE product_ribbon
        SET html_class = trim(both from html_class)
        WHERE NULLIF(html_class, '') IS NOT NULL""",
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE product_ribbon
        SET html_class = ''
        WHERE html_class IS NULL""",
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_models(env.cr, _model_renames)
    openupgrade.rename_tables(env.cr, _table_renames)
    openupgrade.rename_fields(env, _field_renames)
    openupgrade.rename_xmlids(env.cr, _xmlid_renames)
    update_product_ribbon_sale_ribbon(env)
    set_product_ribbon_html_class_default(env)
    openupgrade.remove_tables_fks(env.cr, ["product_style_product_template_rel"])
