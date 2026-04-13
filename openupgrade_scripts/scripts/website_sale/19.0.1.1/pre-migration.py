# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


def website_add_to_cart_action(env):
    """
    website#add_to_cart_action == force_dialog has been removed, map to stay
    """
    openupgrade.copy_columns(env.cr, {"website": [("add_to_cart_action", None, None)]})
    openupgrade.map_values(
        env.cr,
        openupgrade.get_legacy_name("add_to_cart_action"),
        "add_to_cart_action",
        [("force_dialog", "stay")],
        table="website",
    )


@openupgrade.migrate()
def migrate(env, version):
    website_add_to_cart_action(env)
