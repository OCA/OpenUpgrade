# Copyright Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.addons.base.models.ir_module import Module, _logger


def button_upgrade(self):
    """Port of https://github.com/odoo/odoo/pull/83543"""
    if self.env.context.get("openupgrade_upgrade_orphaned"):
        self = self.with_context(openupgrade_upgrade_orphaned=False)
    elif "base" in self.mapped("name"):
        self = self.with_context(openupgrade_upgrade_orphaned=True)
    return Module.button_upgrade._original_method(self)


button_upgrade._original_method = Module.button_upgrade
Module.button_upgrade = button_upgrade


def button_install(self):
    """Port of https://github.com/odoo/odoo/pull/83543"""
    if self.env.context.get("openupgrade_upgrade_orphaned"):
        self = self.with_context(openupgrade_upgrade_orphaned=False)
        orphaned = self.search(
            [("state", "=", "installed"), ("name", "!=", "studio_customization")]
        )
        if orphaned:
            _logger.info(
                "Selecting orphaned modules %s for upgrade", orphaned.mapped("name")
            )
            orphaned.button_upgrade()
    return Module.button_install._original_method(self)


button_install._original_method = Module.button_install
Module.button_install = button_install
