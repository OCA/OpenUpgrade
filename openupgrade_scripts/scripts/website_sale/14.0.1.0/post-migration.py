# Copyright (C) 2021 Open Source Integrators <https://www.opensourceintegrators.com/>
# Copyright 2021 ForgeFlow S.L.  <https://www.forgeflow.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # set simple ribbons (simple case):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE product_template pt
        SET website_ribbon_id = sub.id
        FROM (
            SELECT min(rel.product_style_id) as id, rel.product_template_id
            FROM product_style_product_template_rel rel
            JOIN product_ribbon pr ON pr.id = rel.product_style_id
            WHERE pr.html_class NOT IN ('oe_image_full', '')
            GROUP BY rel.product_template_id
            HAVING count(pr.id) = 1
        ) as sub
        WHERE sub.product_template_id = pt.id""",
    )
    # set new fused ribbons (complex case):
    openupgrade.logged_query(
        env.cr,
        """
        WITH sub AS (
            SELECT STRING_AGG(pr.html, ' ' ORDER BY pr.html) as new_name,
                STRING_AGG(pr.html_class, ' ' ORDER BY pr.html_class) as group_class,
                rel.product_template_id
            FROM product_style_product_template_rel rel
            JOIN product_ribbon pr ON pr.id = rel.product_style_id
            WHERE pr.html_class NOT IN ('oe_image_full', '')
            GROUP BY rel.product_template_id
            HAVING count(pr.id) > 1
        ), new_ribbon AS (
            INSERT INTO product_ribbon (html, html_class)
            SELECT DISTINCT new_name, group_class
            FROM sub
            RETURNING id, html, html_class
        )
        UPDATE product_template pt
        SET website_ribbon_id = pr.id
        FROM sub
        JOIN new_ribbon pr ON (
            sub.new_name = pr.html AND sub.group_class = pr.html_class)
        WHERE pt.id = sub.product_template_id AND pt.website_ribbon_id IS NULL""",
    )
    openupgrade.load_data(env.cr, "website_sale", "14.0.1.0/noupdate_changes.xml")
    openupgrade.logged_query(
        env.cr,
        """
        DELETE FROM ir_model_data
        WHERE module = 'website_sale' and name = 'image_full'
        """,
    )
