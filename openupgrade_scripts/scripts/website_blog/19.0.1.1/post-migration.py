# Copyright 2026 Tecnativa - Carlos Lopez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env, "website_blog", "19.0.1.1/noupdate_changes.xml")
    openupgrade.delete_record_translations(
        env.cr,
        "website_blog",
        ["blog_post_template_new_post"],
        ["arch_db"],
    )
