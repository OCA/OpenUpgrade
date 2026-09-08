# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import json

from openupgradelib import openupgrade

from odoo.tools.translate import get_translation


def translate_section_name(env):
    """
    After translations have been loaded, translate the section name for optional
    products
    """
    translated_section_name = {
        "en_US": "Optional Products Section",
    }
    translated_section_name.update(
        {
            lang.code: get_translation(
                "sale_management", lang.code, translated_section_name["en_US"], []
            )
            for lang in env["res.lang"].search([])
        }
    )
    for lang, name in translated_section_name.items():
        openupgrade.logged_query(
            env.cr,
            """
            UPDATE sale_order_line
            SET name=%s
            FROM sale_order, res_users, res_partner
            WHERE
            sale_order_line.order_id=sale_order.id
            AND sale_order.create_uid=res_users.id
            AND res_users.partner_id=res_partner.id
            AND display_type='line_section'
            AND is_optional=True
            AND COALESCE(res_partner.lang, 'en_US')=%s
            """,
            (name, lang),
        )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE sale_order_template_line
        SET name=%s
        WHERE display_type='line_section' AND is_optional=True
        """,
        (json.dumps(translated_section_name),),
    )


@openupgrade.migrate()
def migrate(env, version):
    translate_section_name(env)
