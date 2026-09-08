# Copyright 2024 Viindoo Technology Joint Stock Company (Viindoo)
# Copyright 2025 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def set_default_header(env):
    """
    For websites with a deprecated header layout, activate default header
    """
    deprecated_layout_keys = (
        "website.template_header_slogan",
        "website.template_header_contact",
        "website.template_header_image",
        "website.template_header_hamburger_full",
        "website.template_header_centered_logo",
        "website.template_header_magazine",
    )
    for website in env["website"].search([]):
        View = env["ir.ui.view"].with_context(
            website_id=website.id, load_all_views=True
        )
        view_id = View._get_view_id("website.layout")
        view = View.browse(view_id)
        deprecated_view = view._get_inheriting_views().filtered(
            lambda x: x.key in deprecated_layout_keys
        )
        if deprecated_view:
            deprecated_view.active = False
            View.with_context(active_test=False).search(
                [
                    ("key", "=", "website.template_header_default"),
                    ("website_id", "=", website.id),
                ]
            ).active = True


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env, "website", "17.0.1.0/noupdate_changes.xml")
    set_default_header(env)
