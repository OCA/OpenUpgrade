# Copyright 2020 ForgeFlow <http://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_xmlid_renames = [
    ("website_blog.menu_news", "website_blog.menu_blog"),
]


def switch_noupdate_records(env):
    openupgrade.set_xml_ids_noupdate_value(
        env,
        "website_blog",
        [
            "mt_blog_blog_published",
        ],
        True,
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(
        env.cr, "website_blog", "migrations/13.0.1.0/noupdate_changes.xml")
    openupgrade.rename_xmlids(env.cr, _xmlid_renames)
    switch_noupdate_records(env)
