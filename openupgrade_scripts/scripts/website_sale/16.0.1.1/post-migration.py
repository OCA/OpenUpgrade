# Copyright 2024 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def _convert_add_to_cart_action(env):
    """Old boolean is now a selection. Let's convert it for those websites not matching
    the default value.
    """
    openupgrade.logged_query(
        env.cr,
        "UPDATE website SET add_to_cart_action = 'go_to_cart' "
        "WHERE NOT cart_add_on_page",
    )


@openupgrade.migrate()
def migrate(env, version):
    _convert_add_to_cart_action(env)
    openupgrade.load_data(env.cr, "website_sale", "16.0.1.1/noupdate_changes.xml")
    openupgrade.delete_record_translations(
        env.cr, "website_sale", ["mail_template_sale_cart_recovery"]
    )
