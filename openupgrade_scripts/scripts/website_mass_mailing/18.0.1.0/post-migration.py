# Copyright 2026 Dixmit Consulting
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from lxml import etree
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    new_snippet = env.ref("website_mass_mailing.s_newsletter_subscribe_form")
    views = env["ir.ui.view"].search(
        [
            (
                "arch_db",
                "ilike",
                'class="s_newsletter_subscribe_form s_newsletter_list js_subscribe"',
            ),
            ("website_id", "!=", False),
        ]
    )
    for view in views:
        root = etree.fromstring(view.arch_db)
        for node in root.cssselect(".s_newsletter_subscribe_form"):
            new_node = new_snippet._get_combined_arch().getchildren()[0]
            button = node.cssselect(".js_subscribe_btn")
            if button:
                new_node.cssselect(".js_subscribe_btn")[0].text = button[0].text
            thanks = node.cssselect(".js_subscribed_btn")
            if thanks:
                new_node.xpath("//*[hasclass('js_subscribed_wrap')]/p")[0].text = (
                    " " + thanks[0].text
                )
            # TODO: Check what happens with translations
            node.getparent().replace(node, new_node)
        view.arch_db = etree.tostring(root)
