# Copyright 2025 Tecnativa - Pedro M. Baeza
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


@openupgrade.migrate()
def migrate(env, version):
    _convert_product_ribbon_html_to_name(env)
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE product_ribbon SET position='right'
        WHERE html_class LIKE '%o_ribbon_right%'
        """,
    )
    openupgrade.load_data(env, "website_sale", "18.0.1.1/noupdate_changes_work.xml")
